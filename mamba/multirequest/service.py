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
        for a, b in d.items():
            if isinstance(b, (list, tuple)):
               setattr(self, a, [obj(x) if isinstance(x, dict) else x for x in b])
            else:
               setattr(self, a, obj(b) if isinstance(b, dict) else b)


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
