import room

class Player():
	def __init__(self, address, ID = None):
		self.address = address
		self.ID = ID
	def getName(self):
		return self.address[0]+':'+str(self.address[1])

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
