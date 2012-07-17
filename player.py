import room
import time

class Player():
    def __init__(self, address, ID = None):
        self.address = address
        self.ID = ID
        self.lastAlive = int(time.time())
    def getName(self):
        return self.address[0]+':'+str(self.address[1])
    def setLastAlive(self, t):
        self.lastAlive = int(t)

    def checkTimeOut(self):
        if int(time.time()) - self.lastAlive > 5:
            if self.ID:
                r = room.findRoomByID(self.ID)
                if len(r.players) == 1:
                    print 'room', r.ID, 'is closed'
                    del r
            print 'player', self.address, 'is disconnected'
            del self

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
