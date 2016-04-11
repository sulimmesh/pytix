'''wrapper class for Trello REST API'''
import requests
import yaml
import datetime

BASE = "https://api.trello.com/1/"


class Trello():
	def __init__(self, project=None, username=None, password=None):
		self._key = None
		self._token = None
		self._authorize()
		if project:
			self._board = self.setProject(project)
		else:
			try:
				with open("projects.yaml", "r") as f:
					data = f.read()
				boards = yaml.load(data)
				self._board = boards["trello"]
			except IOError:
				print "If you have not previously set a Trello board as your current project, you must\nspecify a board name."
				board_name = raw_input("Board name: ")
				self._board = self.setProject(board_name)


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

	def _getCreds(self):
		with open("credentials.yaml", "r") as f:
			data = f.read()
		creds = yaml.load(data)
		key = creds["trello"]["key"]
		token = creds["trello"]["token"]
		return key, token

	def setProject(self, proj_name):
		key, token = self._getCreds()
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

	def getProject(self):
		key, token = self._getCreds()
		board = self._board
		url = BASE + "boards/{0}?lists=open&cards=open&key={1}&token={2}".format(board, key, token)
		response = requests.get(url)
		#TODO deal with the response here
		#what do we want to show the user about the board?
		json = response.json()
		lists = json["lists"]
		cards = json["cards"]
		list_stats = {}
		max_length = 0
		for item in lists:
			cur_length = len(item["name"])
			if cur_length > max_length:
				max_length = cur_length
			list_stats[item["id"]] = {
				"name": item["name"],
				"no. of cards": 0
			}
		for card in cards:
			list_stats[card["idList"]]["no. of cards"] += 1
		left_side = " List Name "
		right_side = " No. of Cards ".format("no. of cards")
		if len(left_side)-2 > max_length:
			max_length = len(left_side)-2
		print "\n"+json["name"]
		print "\nStatistics:" 
		print "-"*(19+max_length)
		print "|{0:{1}}|{2}|".format(left_side, max_length+2, right_side)
		print "-"*(19+max_length)
		for key in list_stats:
			name = " {} ".format(list_stats[key]["name"])
			num = " {} ".format(str(list_stats[key]["no. of cards"]))
			print "|{0:{1}}|{2:14}|".format(
				name,
				max_length+2,
				num)
			print "-"*(19+max_length)

	def getList(self, name):
		key, token = self._getCreds()
		board = self._board
		url = BASE + "boards/{0}?lists=open&key={1}&token={2}".format(board, key, token)
		response = requests.get(url)
		json = response.json()
		for item in json["lists"]:
			if item["name"] == name:
				list_id = item["id"]
		if list_id:
			url = BASE + "lists/{0}?cards=open&key={1}&token={2}".format(list_id, key, token)
			response = requests.get(url)
			json = response.json()
			cards = {}
			max_name_len = 0
			max_id_len = 0
			for card in json["cards"]:
				if len(card["name"]) > max_name_len:
					max_name_len = len(card["name"])
				if len(card["id"]) > max_id_len:
					max_id_len = len(card["id"])
				cards[card["id"]] = {
					"name": card["name"],
					"id": card["id"]
				}
			left_side = " Card Name "
			right_side = " Card ID "
			if len(left_side)-2 > max_name_len:
				max_name_len = len(left_side)-2
			if len(right_side)-2 > max_id_len:
				max_id_len = len(right_side)-2
			print "\n"+json["name"]
			print "-"*(7+max_id_len+max_name_len)
			print "|{0:{1}}|{2:{3}}|".format(left_side, max_name_len+2, right_side,
				max_id_len+2)
			print "-"*(7+max_id_len+max_name_len)
			for key in cards:
				name = " {} ".format(cards[key]["name"])
				ID = " {} ".format(cards[key]["id"])
				print "|{0:{1}}|{2:{3}}|".format(
					name,
					max_name_len+2,
					ID,
					max_id_len+2)
				print "-"*(7+max_id_len+max_name_len)
		else:
			print "List not found. Check your spelling."

	def getTask(self, name=None, ID=None):
		if not name and not ID:
			print "You must specify either a card name or a card ID."
			return None
		key, token = self._getCreds()
		board = self._board
		url = BASE + "boards/{0}?cards=open&key={1}&token={2}".format(board, key, token)
		response = requests.get(url)
		json = response.json()
		card_id = None
		if ID:
			card_id = ID
		else:
			for card in json["cards"]:
				if card["name"] == name:
					card_id = card["id"]
		if card_id:
			url = BASE + "cards/{0}?actions=commentCard&key={1}&token={2}".format(card_id, key, token)
			response = requests.get(url)
			json = response.json()
			comments = {}
			max_name_len = 0
			max_text_len = 0
			max_date_len = 0
			for comment in json["actions"]:
				if len(comment["memberCreator"]["username"])-2 > max_name_len:
					max_name_len = len(comment["memberCreator"]["username"])
				if len(comment["data"]["text"])-2 > max_text_len:
					max_text_len = len(comment["data"]["text"])
				date = comment["date"].split("T")[0]
				if len(date)-2 > max_date_len:
					max_date_len = len(date)
				comments[comment["id"]] = {
					"username": comment["memberCreator"]["username"],
					"text": comment["data"]["text"],
					"date": date
				}
			name = json["name"]
			name_label = " Username "
			text_label = " Comment Text "
			date_label = " Date "
			if len(name_label)-2 > max_name_len:
				max_name_len = len(name_label)-2
			if len(text_label)-2 > max_text_len:
				max_text_len = len(text_label)-2
			print "\n"+name
			print "-"*(10+max_text_len+max_name_len+max_date_len)
			print "|{0:{1}}|{2:{3}}|{4:{5}}|".format(name_label, max_name_len+2, text_label,
				max_text_len+2, date_label, max_date_len+2)
			print "-"*(10+max_text_len+max_name_len+max_date_len)
			#TODO need to handle comments where overall table width > 80 chars
			for key in comments:
				name = " {} ".format(comments[key]["username"])
				text = " {} ".format(comments[key]["text"])
				date = " {} ".format(comments[key]["date"])
				print "|{0:{1}}|{2:{3}}|{4:{5}}|".format(
					name,
					max_name_len+2,
					text,
					max_text_len+2,
					date,
					max_date_len+2)
				print "-"*(10+max_text_len+max_name_len+max_date_len)
		else:
			print "Card not found. Check your spelling."

if __name__ == "__main__":
	trello = Trello()
	trello.getList("Current Sprint")
	trello.getTask("Edit Trello task")