import player

rooms = []
room_num = 0

class Room():
	def __init__(self, ID):
		self.ID = ID
		self.players = []
	def addPlayer(self, new_player):
		global player
		new_player = player.Player(new_player, self.ID)
		self.players.append(new_player)
		

def findRoomByID(ID):
	success = False
	for room in rooms:
		if room.ID == ID:
			success = True
			break
	if success:
		return room
	else:
		return None

def new_room():
    ID = room_num
    rooms.append(Room(ID))
    room_num += 1
    room = findRoomByID(ID)
