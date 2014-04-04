from __future__ import print_function
import zope.interface
from twisted.internet import defer
from mamba.soap.client import SoapEnvelopeNamespaceFix
from suds.client import Client, Method, SoapClient
from suds.plugin import MessagePlugin


from mamba.soap.client_adapter import ClientAdapter



class SoapClientProxy(SoapClient):

    def __init__(self, *args, **kw):
        SoapClient.__init__(self, *args, **kw)
        self.messages = {}

    def last_sent(self, d=None):
        SoapClient.last_sent(self, d)
        return self._conversation('tx', d)

    def last_received(self, d=None):
        SoapClient.last_received(self, d)
        return self._conversation('rx', d)

    def _conversation(self, key, d=None):
        messages = self.messages
        if d is None:
            return messages.get(key)
        else:
            messages[key] = d


class MethodProxy(Method):

    def __init__(self, method):
        Method.__init__(self, method.client, method.method)
        self._actual_method = method
        self._soapclient = None

    def __call__(self, *args, **kwargs):
        client = self.invoker()
        if not self.faults():
            try:
                return client.invoke(args, kwargs)
            except WebFault, e:
                return (500, e)
        else:
            return client.invoke(args, kwargs)


    def clientclass(self, kw=None):
        return SoapClientProxy

    def invoker(self):
        if self._soapclient is None:
            clientclass = self.clientclass()
            self._soapclient = clientclass(self.client, self.method)
        return self._soapclient

class SudsClient(object):

    zope.interface.implements(ClientAdapter)

    def __init__(self, wsdl, options={}):
        if not 'plugins' in options:
            options['plugins'] = [SoapEnvelopeNamespaceFix()]
        else:
            options['plugins'].append(SoapEnvelopeNamespaceFix())

        # TODO: add headers for compression per provider/request
        if not 'headers' in options:
            options['headers'] = {}
        options['headers'].update({"Accept-Encoding": "gzip"})
        options['plugins'] = [SupportGZIPPlugin()]

        self.client = Client(wsdl, **options)
        self.client.connect()

    def set_headers(self, headers):
        self.client.set_options(soapheaders=headers)

    def send_request(self, method_name, params):
        return getattr(self.client.service, method_name)(**params)

    def get_last_response(self):
        return self.client.last_received()

    def get_last_request(self):
        return self.client.last_sent()

    def new_context(self):
        return SudsClientProxy(self)


class SudsClientProxy(object):
    zope.interface.implements(ClientAdapter)
    method = None
    invoker = None
    sudsclient = None

    def __init__(self, sudsclient):
        self.sudsclient = sudsclient
        self.method = None
        self.invoker = None

    def __getattr__(self, attr):
        return getattr(self.sudsclient, attr)

    def send_request(self, method_name, params, args=[]):
        self.method = MethodProxy(getattr(self.sudsclient.client.service, method_name))
        self.invoker = self.method.invoker()
        return self.method(**params)

    def get_last_response(self):
        return self.invoker.last_received()

    def get_last_request(self):
        return self.invoker.last_sent()


try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO
import gzip

class SupportGZIPPlugin(MessagePlugin):

    def received(self, context):
        try:
            compresseddata = context.reply
            compressedstream = StringIO(compresseddata)
            gzipper = gzip.GzipFile(fileobj=compressedstream)
            data = gzipper.read()
            context.reply = data
        except IOError, e:
            # means no gzip compression
            pass
        return context
