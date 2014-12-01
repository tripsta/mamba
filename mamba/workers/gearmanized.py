# messaging.py
from __future__ import print_function, division

import uuid
import ujson

from twisted.python import log
from twisted.internet import reactor
from twisted.internet.defer import returnValue, inlineCallbacks, Deferred, succeed
from twisted.internet.protocol import ClientCreator
from twisted.internet.error import ConnectionDone

from txgearman import client
from txgearman.client import GearmanProtocol
from txgearman.constants import NO_JOB, GRAB_JOB

from mamba import await
from mamba.helpers import log_with_traceback
from mamba.multirequest import exceptions as excs


class ShutdownInterrupt(object):
    pass


class StopWorker(Exception):
    pass


class Gearmanized(object):

    job_name = None
    config = {}

    def __init__(self, my_id=0, options=None):
        self._gearman = None
        self._sleeping = None
        self._worker = None
        self.shutdown_requested = None
        self.my_id = str(my_id)
        self.config['host'] = options.get('host') or "127.0.0.1"
        self.config['port'] = int(options.get('port') or 4730)

    @inlineCallbacks
    def __call__(self, job):
        try:
            values, data = None, None

            try:
                data = ujson.loads(job.data)
            except ValueError, ve:
                values = self._make_error(excs.FormatError("malformed request JSON"))
                returnValue(ujson.dumps(values))

            try:
                log.msg(data)
                values = yield self.invoke(data)
            except Exception, e:
                log_with_traceback(e)
                values = self._make_error(excs.InternalError(e))

            returnValue(ujson.dumps(values))
        except Exception, e:
            log_with_traceback(e)

    def invoke(self, job_data):
        raise NotImplementedError("Subclasses should implement this!")

    @inlineCallbacks
    def worker(self, *args, **kw):
        self._gearman = yield self._connect_to_gearman()

        self._worker = client.GearmanWorker(self._gearman)

        yield self._register_worker()

        while True:
            try:
                if self._sleeping:
                    yield self._sleep()

                if self.shutdown_requested:
                    yield self._deregister_worker()
                    break

                stuff = yield self._worker.protocol.send(GRAB_JOB)
                if stuff[0] == NO_JOB:
                    yield self._sleep()
                else:
                    yield self._do_job(stuff)
            except StopWorker, sw:
                break

    @inlineCallbacks
    def _sleep(self):
        if not self._sleeping:
            self._sleeping = self._worker._sleep()
        shutdown = yield self._sleeping
        self._sleeping = None
        if isinstance(shutdown, ShutdownInterrupt):
            yield self._deregister_worker()
            raise StopWorker()

    @inlineCallbacks
    def _do_job(self, stuff):
        log.msg("got job")
        handle, function, data = stuff[1].split('\0', 2)
        job = client._GearmanJob(handle, function, data)
        yield self._worker._finishJob(job)
        log.msg("job done!")

    def complete_job(self, force_timeout=False):
        log.msg("complete-job signal received")

        if self.shutdown_requested is None:
            self.shutdown_requested = Deferred()
            if force_timeout:
                await(self._get_timeout()).addCallback(self._deregister_worker)
        if self._sleeping:
            self._sleeping.callback(ShutdownInterrupt())
        return self.shutdown_requested

    def _make_error(self, error):
        return {u"error": error.to_dict()}

    def _get_worker_id(self):
        uid = str(uuid.uuid4())
        return "_".join([self.job_name, self.my_id, uid])

    def _get_timeout(self):
        return 0

    @inlineCallbacks
    def _deregister_worker(self, a=None):
        log.msg("disconnecting worker")
        if self.shutdown_requested:
            val = yield self._wait_for_disconnect()
        returnValue(True)

    def _wait_for_disconnect(self):
        log.msg("losing connection and waiting for buffer flush")
        d = Deferred()
        self._worker.protocol.deferreds.append(d)
        d.addBoth(self._done_disconnecting)
        self._worker.protocol.transport.loseConnection()
        return d

    def _done_disconnecting(self, reason):
        self.shutdown_requested.callback(True)
        self.shutdown_requested = None
        log.msg("Done")
        return True

    def _connect_to_gearman(self):
        return ClientCreator(reactor, GearmanProtocol).connectTCP(self.config['host'], self.config['port'])

    @inlineCallbacks
    def _register_worker(self):
        id_ = self._get_worker_id()
        yield self._worker.setId(id_)
        yield self._worker.registerFunction(self.job_name, self)
        log.msg("register worker {}".format(id_))

