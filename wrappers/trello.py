'''wrapper class for Trello REST API'''
import requests

class Trello():
	def __init__(self, username=None, password=None, board=None):
		self._username = username
		self._password = password
		self._board = board
		self._key = None
		self._token = None

	def authorize(self):
		#we'll check the keyring/file here to see if the api key and token exist currently
		#if so, we return them directly
		print "Your API key was not found on file."
		print "Navigate to the following link to obtain your API key\nand paste it into the terminal below. Make sure you are logged into Trello before following the link."
		print "Link: https://trello.com/app-key"
		key =  raw_input("API key: ")
		print "\nNow please follow the link below and click 'Allow'."
		print "Copy and paste the resulting token back into the terminal. Pytix will\ncache this key and token for future use. This is a one-time procedure."
		print "https://trello.com/1/authorize?expiration=never&scope=read%2Cwrite&name=SinglePurposeToken&key={}&response_type=token".format(key)
		token = raw_input("API token: ")
		self._key = key
		self._token = token
