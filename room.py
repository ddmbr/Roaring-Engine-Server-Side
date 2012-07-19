import player

rooms = []
room_num = 0

class Room():
    def __init__(self, ID):
        self.ID = ID
        self.players = []
        self.track = 1
    def addPlayer(self, new_player):
        global player
        new_player = player.Player(new_player, self.ID)
        self.players.append(new_player)

def findRoomByID(ID):
    global rooms, room_num
    success = False
    for r in rooms:
        if r.ID == ID:
            success = True
            break
    if success:
        return r
    else:
        return None

def newRoom():
    global rooms, room_num
    ID = room_num
    rooms.append(Room(ID))
    room_num += 1
    r = findRoomByID(ID)
    return r

#
# TODO So, you can see other room's info, too
def roomInfo(ID, key='room-info'):
    global rooms, room_num
    r = findRoomByID(ID)
    data = ['', key, [ID, len(r.players), r.track]]
    return data

def processTimeOut():
    global rooms, room_num
    for i in range(len(rooms)):
        for j in range(len(rooms[i].players)):
            rooms[i].players[j].checkTimeOut()
        if len(rooms[i].players) == 0:
            print 'room', rooms[i].ID, 'is closed'
            del rooms[i]
