from __future__ import division, print_function
from zope.interface import Interface, implements, verify
from zope.interface.verify import verifyObject
from zope.interface.exceptions import DoesNotImplement
from twisted.internet import task
from twisted.internet import defer


class IRequestCallable(Interface):

    def __call__(*args, **kwargs):
        """do the actual request
        return a twisted.internet.defer.Deferred
        """


class IWebserviceRequestDelegate(Interface):

    def set_soap_headers():
        pass

    def build_request(self):
        pass

    def parse_response(self):
        pass

    def get_wsdl(self):
        pass

    def handle_send_error(e):
        pass


class IWebserviceLoggable(Interface):

    def log_conversation():
        pass


class WebserviceRequestCallableMixin(object):
    implements(IRequestCallable)

    @defer.inlineCallbacks
    def send(self):
        yield defer.maybeDeferred(self.set_soap_headers)
        val = yield defer.maybeDeferred(self.client.send_request,
                                        self.method_name,
                                        self.params)
        defer.returnValue(val)

    @defer.inlineCallbacks
    def perform(self):
        yield self.connect()
        yield defer.maybeDeferred(self.build_request)
        try:
            self.response = yield self.send()
        except Exception, e:
            yield defer.maybeDeferred(self.handle_send_error, e)
            defer.returnValue(None)

        self.log_conversation()
        resp = yield defer.maybeDeferred(self.parse_response)
        defer.returnValue(resp)

    @defer.inlineCallbacks
    def __call__(self, *args, **kwargs):
        resp = yield self.perform()
        defer.returnValue(resp)


class IRequestRunner(Interface):
    def run_requests(request_collection):
        """run all requests in the collection
        return a twisted.internet.defer.DeferredList
        """


class RequestError(Exception):
    pass


class FakeRequestCallable(object):
    implements(IRequestCallable)

    def __init__(self, _reactor=0, value=True, delay_sec=1.0, shouldfail=False):
        self._reactor = _reactor
        self._delay_sec = delay_sec
        self._success_val = True
        self.shouldfail = shouldfail

    def __call__(self, *args, **kwargs):
        what = self._fail if self.shouldfail else self._succeed
        return task.deferLater(self._reactor, self._delay_sec, what)

    def _succeed(self):
        return self._success_val

    def _fail(self):
        raise RequestError("Fake Request Failed")


class BasicRequestRunner(object):
    implements(IRequestRunner)

    def __init__(self, _reactor=None):
        self._reactor = _reactor

    def run_requests(self, request_collection):
        deferreds = []
        for request in self._iterable(request_collection):
            if not callable(request):
                self._cancel_deferreds(deferreds)
                fmt = "object {0} does not implement IRequestCallable"\
                      .format(str(request))
                raise TypeError(fmt)

            d = request()
            if not isinstance(d, defer.Deferred):
                self._cancel_deferreds(deferreds)
                raise TypeError("Callable should return twisted.internet.defer.Deferred")
            deferreds.append(d)

        return defer.DeferredList(deferreds)

    def _cancel_deferreds(self, deferreds):
        return [d.cancel() for d in deferreds]

    def _iterable(self, item):
        try:
            return iter(item)
        except TypeError, te:
            return [item]
