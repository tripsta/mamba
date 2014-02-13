from __future__ import division, print_function
from twisted.spread import pb, flavors
from mamba.multirequest.core import BasicRequestRunner
from mamba.multirequest import webservice
from mamba.multirequest.webservice.fake import ping


class BasicRequest(flavors.Copyable):

    def __init__(self, method):
        self.method = method


class RemoteBasicRequest(flavors.RemoteCopy):
    pass


class obj(object):
    def __init__(self, d):
        assert isinstance(d, dict)
        for a, b in d.iteritems():
            if self._is_iterable(b):
                what = [self._make_obj(x) for x in b]
            else:
                what = self._make_obj(b)
            setattr(self, a, b)

    def _make_obj(self, sth):
        return obj(sth) if isinstance(sth, dict) else sth

    def _is_iterable(self, thing):
        try:
            _ = iter(thing)
            return False if isinstance(thing, dict) else True
        except TypeError, te:
            return False


flavors.setUnjellyableForClass(BasicRequest, RemoteBasicRequest)


class BasicMultiRequest(flavors.Copyable):

    def __init__(self, requests):
        self.requests = requests

    def __iter__(self):
        return iter(self.requests)


class RemoteBasicMultiRequest(flavors.RemoteCopy):
    pass


class BasicResponse(flavors.Copyable):
    pass


class RemoteBasicResponse(flavors.RemoteCopy):
    pass


flavors.setUnjellyableForClass(BasicMultiRequest, RemoteBasicMultiRequest)


class BasicRequestFullfiler(object):

    def __init__(self, request_runner):
        self.request_runner = request_runner

    def __call__(self, request):
        """Fullfill a BasicRequest or a BasicMultiRequest,
        returns a DeferredList"""
        try:
            it = iter(request)
        except TypeError:
            it = iter([request])

        requests = (self._get_callable(r) for r in it)

        return self.request_runner.run_requests(requests)

    def _get_callable(self, request):
        """Called with a BasicRequest object returns a callable"""
        if isinstance(request, dict):
            parts = request['method'].split(".")
        else:
            parts = request.method.split(".")
        function_to_call = getattr(self.webservice_module, parts.pop(0))

        for name in parts:
            function_to_call = getattr(function_to_call, name)

        return function_to_call(request)

    def set_webservice_module(self, mod):
        self.webservice_module = mod
        return self


fullfill_request = BasicRequestFullfiler(request_runner=BasicRequestRunner()).set_webservice_module(webservice)


__all__ = ['BasicRequest', 'BasicRequestFullfiler', 'fullfill_request']
