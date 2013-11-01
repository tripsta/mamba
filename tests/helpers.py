
from twisted.web.test.test_web import DummyRequest
from twisted.internet import defer
from twisted.web import server

class _FakeContent(object):
    def __init__(self, bodyContent):
        self.content = bodyContent

    def read(self):
        return self.content

class _FakeHTTPRequest(DummyRequest):
    content = None
    def __init__(self, method, url, args=None, headers=None, body=None):
        DummyRequest.__init__(self, url.split('/'))
        if body is not None:
            self.content = _FakeContent(body)
        self.method = method
        self.headers.update(headers or {})
                                                                                                                                                                                       
        args = args or {}
        for k, v in args.items():
            self.addArg(k, v)

    def value(self):
        return "".join(self.written)
 
 
class SiteTestMixin(server.Site):

    def get(self, url, args=None, headers=None, body=None):
        return self._request("GET", url, args, headers, body)
 
    def post(self, url, args=None, headers=None, body=None):
        return self._request("POST", url, args, headers, body)
 
    def _request(self, method, url, args, headers, body):
        request = _FakeHTTPRequest(method, url, args, headers, body)
        resource = self.getResourceFor(request)
        result = resource.render(request)
        return self._resolveResult(request, result)

    def _resolveResult(self, request, result):
        if isinstance(result, str):
            request.write(result)
            request.finish()
            return defer.succeed(request)
        elif result is server.NOT_DONE_YET:
            if request.finished:
                return defer.succeed(request)
            else:
                return request.notifyFinish().addCallback(lambda _: request)
        else:
            raise ValueError("Unexpected return value: %r" % (result,))
