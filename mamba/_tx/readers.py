from twisted.internet.protocol import Protocol

class ResponseBodyReader(Protocol):

	def __init__(self, finished, length):
		self.finished = finished
		self.bodyLength = length
		self.body = bytearray()

	def dataReceived(self, bytes):
		self.body += bytes

	def connectionLost(self, reason):
		self.finished.callback(self.body)
