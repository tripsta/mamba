# test_server.py

import struct
from twisted.internet import protocol
from twisted.python import log
from txgearman import constants


class GearmanServerProtocol(protocol.Protocol):
    unsolicited = []

    def connectionMade(self):
        self.receivingCommand = 0
        self.deferreds = []
        self.unsolicited_handlers = set()

    def send_raw(self, cmd, *args):
        """Send a command with the given data with no response."""
        data = "\0".join(args)
        seq = [constants.RES_MAGIC, struct.pack(">II", cmd, len(data)), data]
        return seq

    def assign_job(self, jobname, *jobdata):
        return self.send_raw(constants.JOB_ASSIGN, "handle", jobname, *jobdata)

    def no_job(self, jobname, *jobdata):
        return self.send_raw(constants.NO_JOB, "handle", jobname, *jobdata)

    def dataReceived(self, data):
        print(data)
        self.data = data
        for d in self.deferreds:
            d.callback(data)

    def connectionLost(self, reason):
        for d in list(self.deferreds):
            d.errback(reason)
        self.deferreds.clear()




