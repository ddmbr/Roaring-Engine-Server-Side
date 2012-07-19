import room
import time

class Player():
    def __init__(self, address, ID = None):
        self.address = address
        self.ID = ID
        self.lastAlive = int(time.time())
    def getName(self):
        return self.address[0]+':'+str(self.address[1])
    def setLastAlive(self):
        self.lastAlive = int(time.time())

    def checkTimeOut(self):
        if int(time.time()) - self.lastAlive > 15:
            if self.ID != None:
                r = room.findRoomByID(self.ID)
                print 'player', self.address, 'is disconnected'
                for i in range(len(r.players)):
                    if r.players[i] == self:
                        del r.players[i]
                        break

def findPlayerByAddress(address):
    global room
    success = False
    for r in room.rooms:
        for player in r.players:
            if player.address == address:
                success = True
                break
    if success:
        return player
    else:
        return None
