from twisted.spread import pb
from twisted.internet import task

class PBReConnectingClientFactory(pb.PBClientFactory):

    def __init__(self, reactor):
        pb.PBClientFactory.__init__(self)
        self.reactor = reactor
        self.numReconnectAttempts = 0

    def clientConnectionFailed(self, connector, reason):
        task.deferLater(self.reactor, random_range(0.1, 0.2), connector.connect)
