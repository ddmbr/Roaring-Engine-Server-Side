import SocketServer
import json
import random

from room import *
import player


class MyUDPHandler(SocketServer.BaseRequestHandler):
    """
    This class works similar to the TCP handler class, except that
    self.request consists of a pair of data and client socket, and since
    there is no connection the client address must be given explicitly
    when sending data back via sendto().
    """

    def handle(self):
    global rooms, room_num, player
        data = self.request[0].strip()
    data = json.loads(data)
        socket = self.request[1]
        #print self.client_address[0],"wrote:", data
    # Situations when game not ready
    if data[0] == 'new-room':
        print self.client_address, 'want to create a room'
        p = player.findPlayerByAddress(self.client_address)
        if p != None:
            print 'but he\'d joined room', p.ID
            return
        ID = room_num
        rooms.append(Room(ID))
        room_num += 1
        room = findRoomByID(ID)
        room.addPlayer(self.client_address)
        print 'he is now in room', ID
    elif data[0] == 'my-room':
        player = player.findPlayerByAddress(self.client_address)
        if player == None:
            socket.sendto('null', self.client_address)
        else:
            socket.sendto(json.dumps([player.ID, len(findRoomByID(player.ID).players)]), self.client_address)
    elif data[0] == 'view-rooms':
        room_list = map(lambda x:x.ID, rooms)
        data = json.dumps(['', 'room-list', room_list])
        socket.sendto(data, self.client_address)
        print self.client_address, 'want to view rooms'
    elif data[0] == 'join-room':
        ID = data[1]
        room = findRoomByID(ID)
        if room != None:
            room.addPlayer(self.client_address)
    elif data[0] == 'start':
        p = player.findPlayerByAddress(self.client_address)
        if p == None:
            print 'He didn\'t join a room'
        else:
            room = findRoomByID(p.ID)
            # tell every player in the room to start the game and BTW give them position
            data = json.dumps(['','start', len(room.players)])
            pos = [200, 300]
            for p in room.players:
                p.pos = tuple(pos)
                print p.getName(), 'is at', p.pos
                pos[1] += 80
            for p in room.players:
                print 'I want to tell', p.address, 'to start'
                socket.sendto(data, p.address)
                for p_o in room.players:
                    if p == p_o: continue
                    crt_data = json.dumps([p_o.getName(), 'create-player', p_o.pos])
                    socket.sendto(crt_data, p.address)
    elif data[0] == 'adjust-physical':
        p = player.findPlayerByAddress(self.client_address)
        if p == None:
            print 'error'
        room = findRoomByID(p.ID)
        adjust_data = json.dumps([p.getName(), 'adjust-physical', data[1]])
        for p_o in room.players:
            if p == p_o: continue
            socket.sendto(adjust_data, p_o.address)
    elif data[0] == 'request-player':
        p = player.findPlayerByAddress(self.client_address)
        if p == None:
            print 'error occur'
            return
        room = findRoomByID(p.ID)
        for p in room.players:
            print 'I want to tell', p.address, 'to add player'
            for p_o in room.players:
                if p == p_o:
                    adj_data = json.dumps(['player', 'adjust-pos', p_o.pos])
                    socket.sendto(adj_data, p.address)
                    continue
                print 'add', p_o.getName()
                crt_data = json.dumps([p_o.getName(), 'create-player', p_o.pos])
                socket.sendto(crt_data, p.address)
                adj_data = json.dumps([p_o.getName(), 'adjust-pos', p_o.pos])
                socket.sendto(adj_data, p.address)
    # Situations when game started
    elif data[0] == 'name-me':
            print self.client_address, "want me to name him"
        name = self.client_address[0] + ':' + str(self.client_address[1])
        socket.sendto(name, self.client_address)
        print 'he is now named', name
    elif data[0] == 'keys':
        p = player.findPlayerByAddress(self.client_address)
        respond = json.dumps([p.getName(), 'keys', data[1]])
        room = findRoomByID(p.ID)
        for other_player in room.players:
            if other_player == p:
                continue
            else:
                socket.sendto(respond, other_player.address)

if __name__ == "__main__":
    HOST, PORT = "184.82.236.126", 9999
    server = SocketServer.UDPServer((HOST, PORT), MyUDPHandler)
    server.serve_forever()

