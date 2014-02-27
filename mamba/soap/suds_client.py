from __future__ import print_function
import zope.interface
from twisted.internet import defer
from mamba.soap.client import SoapEnvelopeNamespaceFix
from suds.client import Client
from suds.plugin import MessagePlugin


from mamba.soap.client_adapter import ClientAdapter


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