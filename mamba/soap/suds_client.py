import zope.interface

from mamba.soap.client import SoapEnvelopeNamespaceFix
from suds.client import Client


from mamba.soap.client_adapter import ClientAdapter


class SudsClient(object):

	zope.interface.implements(ClientAdapter)

	def __init__(self, wsdl, options={"retXml" : True}, headers=None):
		self.client = Client(wsdl, plugins=[SoapEnvelopeNamespaceFix()])
		self.client.connect()
		if options:
			self.client.set_options(retxml=True)
		if headers:
			self.set_headers(headers)

	def set_headers(self, headers):
		self.client.set_options(soapheaders=headers)

	def send_request(self, method_name, params):
		return getattr(self.client.service, method_name)(**params)

	def get_last_response(self):
		return self.client.last_received()

	def get_last_request(self):
		return self.client.last_sent()

