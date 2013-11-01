from twisted.internet import defer
from zope.interface import implements
from twisted.web.iweb import IBodyProducer

class StringProducer(object):
	implements(IBodyProducer)

	def __init__(self, body):
		self.body = body
		self.length = len(body)

	def startProducing(self, consumer):
		consumer.write(self.body)
		return defer.succeed(None)

	def pauseProducing(self):
		pass

	def stopProducing(self):
		pass
