import os
import time
import mock
from datetime import datetime


import suds
from suds.client import RequestContext
from mamba.soap.suds_client import SudsClient
from mamba.test.unittest import TestCase
from mamba.soap.client_adapter import ClientAdapter
from mamba.soap.client import SoapEnvelopeNamespaceFix
from twisted.internet import defer


class SudsClientTestCase(TestCase):
	client = None

	@defer.inlineCallbacks
	def setUp(self):
		self.wsdl = 'file://' + os.path.realpath(os.path.dirname(os.path.realpath(__file__)) + '/../../../../mamba/tests/mamba/data/dummy.wsdl')
		if not SudsClientTestCase.client:
			SudsClientTestCase.client = yield SudsClient(self.wsdl)
		self.client = SudsClientTestCase.client


class SudsClientImplementSoapClientInterfaceTest(SudsClientTestCase):

	def test_implement_interface(self):
		self.assertImplementInterface(ClientAdapter, self.client)


class SudsClientInitTest(SudsClientTestCase):

	@defer.inlineCallbacks
	def test_options_if_options_are_given(self):
		options = {"retxml": True, "soapheaders": "foobar"}
		self.client = yield SudsClient(self.wsdl, options=options)
		self.assertIsInstance(self.client, SudsClient)
		assert self.client.client.service is not None
		suds_client = self.client.client
		self.assertEqual(True, self.client.client.options.retxml)
		self.assertEqual(0, self.client.client.options.cachingpolicy)
		self.assertEqual("foobar", self.client.client.options.soapheaders)
		self.assertEqual(suds.client.Client, suds_client.__class__)
		self.assertEqual({"Accept-Encoding": "gzip"}, suds_client.options.transport.options.headers)

	@defer.inlineCallbacks
	def test_options_default_if_no_options_given(self):
		self.client = yield SudsClient(self.wsdl)
		self.assertEqual(False, self.client.client.options.retxml)
		self.assertTupleEqual((), self.client.client.options.soapheaders)


class SudsClientSetHeadersTest(SudsClientTestCase):

	def test_set_proper_headers(self):
		headers = {'foo': {'bar': '', 'foobar': '', 'barfoo': ''}}
		self.client.set_headers(headers)
		self.assertEquals(headers, self.client.client.options.soapheaders)


class SudsClientGetLastRequestTest(SudsClientTestCase):

	@classmethod
	def mock_last_request(cls):
		return 'foobar'

	@mock.patch('suds.client.Client.last_sent', mock_last_request)
	def test_return_last_request(self):
		self.assertEqual(self.mock_last_request(), self.client.get_last_request())


class SudsClientGetLastResponseTest(SudsClientTestCase):

	@classmethod
	def mock_last_response(cls):
		return 'John Smith'

	@mock.patch('suds.client.Client.last_received', mock_last_response)
	def test_return_last_response(self):
		self.assertEqual(self.mock_last_response(), self.client.get_last_response())

class SudsClientSendRequestTest(SudsClientTestCase):

	def test_send_function_with_proper_arguments(self):
		args = {"foo":"bar", "John":"Smith"}
		method_name = 'quite_nice_method'
		self.client.client.service = mock.Mock()
		self.client.send_request(method_name, args)
		self.client.client.service.quite_nice_method.assert_called_with(**args)