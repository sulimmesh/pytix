'''wrapper class for Trello REST API'''

class Trello():
	def __init__(self, username, password, board=None):
		self._username = username
		self._password = password
		self._board = board
