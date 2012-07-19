import SocketServer
import json
import random

import room
import player

class MyUDPHandler(SocketServer.BaseRequestHandler):
    """
    This class works similar to the TCP handler class, except that
    self.request consists of a pair of data and client socket, and since
    there is no connection the client address must be given explicitly
    when sending data back via sendto().
    """

    def send(self, data, address = None):
        if address == None:
            address = self.client_address
        socket = self.request[1]
        socket.sendto(json.dumps(data), address)

    def handle(self):
        global player, room
        data = self.request[0].strip()
        data = json.loads(data)
        socket = self.request[1]
        ################################
        #
        # Situations when game not ready
        #
        ################################
        #
        # Create new room
        if data[0] == 'new-room':
            print self.client_address, 'want to create a room'
            p = player.findPlayerByAddress(self.client_address)
            if p != None and p.ID != None:
                print 'but he\'d joined room', p.ID
                return
            r = room.newRoom()
            r.addPlayer(self.client_address)
            print 'he is now in room', r.ID
        #
        # Get the player's current room info
        # msg format is
        # [player's name, [room ID, number of players, , track, etc]]
        elif data[0] == 'my-room':
            p = player.findPlayerByAddress(self.client_address)
            if p == None:
                data = ['', 'my-room', [-1]]
                self.send(data)
            else:
                data = roomInfo(ID, 'my-room')
                self.send(data)
        #
        # Get the rooms list
        elif data[0] == 'view-rooms':
            room.processTimeOut()
            room_list = map(lambda x:x.ID, room.rooms)
            data = ['', 'room-list', room_list]
            self.send(data)
            print self.client_address, 'want to view rooms'
        #
        # change track
        elif data[0] == 'chg-track':
            # Do exception handling TODO
            p = player.findPlayerByAddress(self.client_address)
            r = room.findRoomByID(p.ID)
            r.track = data[1]
            data = room.roomInfo(ID, 'my-room')
            self.send(data)
        #
        # Join the player to a room
        elif data[0] == 'join-room':
            p = player.findPlayerByAddress(self.client_address)
            ID = data[1]
            if p != None and p.ID == ID:
                print 'he\'d already joined the room'
                return
            # TODO quit room
            r = room.findRoomByID(ID)
            if r != None:
                r.addPlayer(self.client_address)
                print self.client_address, 'joined room', ID
                # tell the player the current room info
                data = room.roomInfo(ID, 'my-room')
                self.send(data)
        #
        # Tell all players in the room to start the game
        elif data[0] == 'start':
            p = player.findPlayerByAddress(self.client_address)
            if p == None:
                print 'He didn\'t join a room'
                data = ['', 'msg', 'Join a room first!']
            else:
                r = room.findRoomByID(p.ID)
                r.status = 'running'
                # tell every player in the room to start the game
                # and initialize their position
                # TODO! Replace position with 'Sequence'
                seq = 0
                for p in r.players:
                    p.seq = seq
                    print p.getName(), 'is at', p.seq
                    seq += 1
                # First start a player's game,
                # then add other players to his game
                for p in r.players:
                    print 'I want to tell', p.address, 'to start'
                    self.startGame(p, r)
        #
        # When a player want to be started
        # just start him
        elif data[0] == 'start-me':
            p = player.findPlayerByAddress(self.client_address)
            r = room.findRoomByID(p.ID)
            self.startGame(p, r)

        elif data[0] == 'request-player':
            p = player.findPlayerByAddress(self.client_address)
            if p == None:
                print 'error occur'
                return
            p.setLastAlive()
            r = room.findRoomByID(p.ID)
            for p in r.players:
                print 'I want to tell', p.address, 'to add player'
                for p_o in r.players:
                    if p == p_o:
                        adj_data = json.dumps(['player', 'adjust-pos', p_o.seq])
                        socket.sendto(adj_data, p.address)
                        continue
                    print 'add', p_o.getName()
                    crt_data = json.dumps([p_o.getName(), 'create-player', p_o.seq])
                    socket.sendto(crt_data, p.address)
                    adj_data = json.dumps([p_o.getName(), 'adjust-pos', p_o.seq])
                    socket.sendto(adj_data, p.address)
        ################################
        #
        # Situations after game started
        #
        ################################
        #
        # Adjust a player's physics info
        elif data[0] == 'adjust-physical':
            p = player.findPlayerByAddress(self.client_address)
            if p == None:
                print 'Error! Player not found when adjusting physics'
            r = room.findRoomByID(p.ID)
            if r.status != 'running': return
            adjust_data = [p.getName(), 'adjust-physical', data[1]]
            for p_o in r.players:
                if p == p_o: continue
                self.send(adjust_data, p_o.address)
        #
        # Sync keys
        elif data[0] == 'keys':
            p = player.findPlayerByAddress(self.client_address)
            p.setLastAlive()
            r = room.findRoomByID(p.ID)
            if r.status != 'running': return
            sync_data= [p.getName(), 'keys', data[1]]
            for p_o in r.players:
                if p_o == p: continue
                self.send(sync_data, p_o.address)
        #
        # Someone win the game
        elif data[0] == 'win':
            p = player.findPlayerByAddress(self.client_address)
            r = room.findRoomByID(p.ID)
            if r.status != 'running': return
            r.status = 'over'
            lose_data= ['', 'lose']
            for p_o in r.players:
                if p_o == p: continue
                self.send(lose_data, p_o.address)
            

    def startGame(self, p, r):
        """ Tell the specific player to start the game """

        start_data = ['','start', [len(r.players), r.track]]
        self.send(start_data, p.address)
        for p_o in r.players:
            if p == p_o: continue
            crt_data = [p_o.getName(), 'create-player', p_o.seq]
            self.send(crt_data, p.address)

if __name__ == "__main__":
    HOST, PORT = "184.82.236.126", 9999
    server = SocketServer.UDPServer((HOST, PORT), MyUDPHandler)
    server.serve_forever()

