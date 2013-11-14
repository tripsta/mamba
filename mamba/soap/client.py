from suds.xsd.sxbasic import Import

import logging
import traceback as tb
import suds.metrics as metrics
from suds import WebFault
from suds.client import Client
from twisted.internet import reactor, defer
from suds.bindings import binding
from suds import WebFault, MethodNotFound
from suds.plugin import MessagePlugin
import re


class SoapEnvelopeNamespaceFix(MessagePlugin):

    def sending(self, context):
		p = re.compile('(xmlns:ns)+([0-9])+(="http://schemas.xmlsoap.org/soap/envelope/")')
		match = p.search(context.envelope)
		if match:
			ns_index = match.group(2)
			context.envelope = p.sub('', context.envelope)
			context.envelope = re.sub('(<ns)+({})+(:)'.format(ns_index), '<SOAP-ENV:', context.envelope)
			context.envelope = re.sub('(</ns)+({})+(:)'.format(ns_index), '</SOAP-ENV:', context.envelope)

"""
SoapClient just for building requests
"""
class SoapClient(object):

	def __init__(self, wsdl):
		self.client = Client(wsdl, plugins=[SoapEnvelopeNamespaceFix()])
		self.client.connect()
		self.client.set_options(nosend=True)

	def setHeaders(self, headers):
		self.client.set_options(soapheaders=headers)

	"""
    Fake send function.
    @return: deferred
    """
	def body(self, methodName, params):
		return getattr(self.client.service, methodName)(**params)
