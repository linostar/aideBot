import sys
import os
import json

class Data:
	DATA_JSON_FILE = "data/data.json"
	topics = {}

	def __init__(self):
		self.read_data()

	def read_data(self):
		if not os.path.exists(self.DATA_JSON_FILE):
			print('Error: data.json could not be found.')
			sys.exit(1)
		with open(self.DATA_JSON_FILE, 'r') as data_fp:
			self.topics = json.load(data_fp)
