import ujson
import struct
from collections import deque

from twisted.internet import task, defer, reactor
from twisted.test import proto_helpers
from twisted.protocols import stateful
from twisted.python import log

from txgearman.client import GearmanProtocol
from txgearman import constants

from mamba.workers.gearmanized import Gearmanized, StopWorker
from mamba.workers.tests.test_server import GearmanServerProtocol
from mamba.test import unittest
from mamba import await


TEST_DATA = ujson.dumps([0, 1 , 2])


class CustomTransport(proto_helpers.StringTransportWithDisconnection):

    def writeSequence(self, data):
        ss = struct.unpack(">II", data[1])
        if ss[0] == constants.WORK_COMPLETE:
            self.lastSent = data
        proto_helpers.StringTransportWithDisconnection.writeSequence(self, data)




class TestGearmanizedService(Gearmanized):

    job_name = "TestGearmanizedService"

    def __init__(self, transport):
        super(TestGearmanizedService, self).__init__()
        self._fake_transport = transport

    def invoke(self, job):
        return {}

    def _connect_to_gearman(self):
        self.proto = GearmanProtocol()
        self.proto.makeConnection(self._fake_transport)
        return self.proto


class GearmanizedTestCase(unittest.TestCase):

    def setUp(self):
        self.transport = CustomTransport()
        self.server = GearmanServerProtocol()
        self.worker = TestGearmanizedService(self.transport)
        self.server.makeConnection(self.transport)

    def assertWorkerReturnStatus(self, status=constants.WORK_COMPLETE):
        self.assertEqual(struct.unpack(">II", self.transport.lastSent[1])[0], status)

    def _send_data_and_close(self, data):
        for d in data:
           self.worker._gearman.dataReceived(d)
        self._close()

    def _close(self):
        self.server.transport.clear()
        self.worker._gearman.connectionLost(StopWorker())

    @defer.inlineCallbacks
    def test_worker_loop_do_job_if_exists(self):
        self.worker.worker()
        self.server.transport.clear()
        data = yield self.server.assign_job("TestGearmanizedService", TEST_DATA)
        yield self._send_data_and_close(data)
        self.assertWorkerReturnStatus(constants.WORK_COMPLETE)

    @defer.inlineCallbacks
    def test_worker_loop_do_sleep_if_no_job(self):
        self.worker.worker()
        self.server.transport.clear()
        data = yield self.server.no_job("TestGearmanizedService")
        yield self._send_data_and_close(data)
        self.assertTrue(self.worker._sleeping)





