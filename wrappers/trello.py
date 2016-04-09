'''wrapper class for Trello REST API'''
import requests
import yaml

BASE = "https://api.trello.com/1/"


class Trello():
	def __init__(self, username=None, password=None, board=None):
		self._board = board
		self._key = None
		self._token = None
		self._authorize()

	def _authorize(self):
		try:
			with open("credentials.yaml", "r") as f:
				data = f.read()
			creds = yaml.load(data)
		except IOError:
			creds = {}
		if not "trello" in creds:
			print "Your API key was not found on file."
			print "Navigate to the following link to obtain your API key\nand paste it into the terminal below. Make sure you are logged into Trello before following the link."
			print "Link: https://trello.com/app-key"
			key =  raw_input("API key: ")
			print "\nNow please follow the link below and click 'Allow'."
			print "Copy and paste the resulting token back into the terminal. Pytix will\ncache this key and token for future use. This is a one-time procedure."
			print "https://trello.com/1/authorize?expiration=never&scope=read%2Cwrite&name=pytix&key={}&response_type=token".format(key)
			token = raw_input("API token: ")
			self._key = key
			self._token = token
			new_creds = {}
			new_creds["key"] = key
			new_creds["token"] = token
			creds["trello"] = new_creds
			with open("credentials.yaml", "w") as f:
				f.write(yaml.dump(creds))

	def setProject(self, proj_name):
		with open("credentials.yaml", "r") as f:
			data = f.read()
		creds = yaml.load(data)
		key = creds["trello"]["key"]
		token = creds["trello"]["token"]
		url = BASE + "members/me?&boards=all&key={0}&token={1}".format(key, token)
		response = requests.get(url)
		boards = response.json()["boards"]
		for board in boards:
			print board
			if board["name"] == proj_name:
				self._board = board["id"]
				try:
					with open("projects.yaml", "r") as f:
						data = f.read()
					projs = yaml.load(data)
				except IOError:
					projs = {}
				projs["trello"] = board["id"]
				with open("projects.yaml", "w") as f:
					f.write(yaml.dump(projs))
				return board["id"]
