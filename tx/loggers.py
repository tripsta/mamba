import os
import datetime
from pythepie.bootstrap import TP24

class WebserviceLogger(object):

	def log(self, text, suffix):
		import pymongo
		host = TP24.config.mongo.host
		database = TP24.config.mongo.database
		replicaset = TP24.config.mongo.replicaset
		client = pymongo.MongoClient(host, replicaset=replicaset)
		db = getattr(client, database)
		db.api.save({'module' : 'flights', 'suffix' : text, 'dateCreated' : datetime.datetime.utcnow()})
		WebserviceFileLogger().log(text, suffix)

class WebserviceFileLogger(object):

	def log(self, text, suffix):
		date_str = datetime.datetime.utcnow().strftime("%Y%m%d")
		datetime_str = datetime.datetime.utcnow().strftime("%Y-%m-%d-%H%M%SZ")
		folder_path = os.path.join(os.path.dirname(os.path.realpath(__file__)) + ('/../../data/logs/%s/' % date_str))
		if not os.path.exists(folder_path) :
			os.makedirs(folder_path)
		filename = 'pricexplorer-%s%s.xml' % (datetime_str, suffix)
		filepath = os.path.join(folder_path, filename)
		f = open(filepath, 'w')
		f.write(text)
		f.close()

class WebserviceTestLogger(WebserviceLogger):

	def __init__(self, testCase=None):
		self.logs = {'request': [], 'response': []}
		self.testCase = testCase

	def log(self, text, suffix):
		if suffix is 'request':
			self.logs['request'].append(text)
		else:
			self.logs['request'].append(text)

	def assertRequestLogged(self):
		self.testCase.assertNotEquals(0, len(self.logs['request']))

	def assertResponseLogged(self):
		self.testCase.assertNotEquals(0, len(self.logs['response']))


if __name__ == '__main__':

	logger = WebserviceLogger()
	logger.log('abc', 'def')

