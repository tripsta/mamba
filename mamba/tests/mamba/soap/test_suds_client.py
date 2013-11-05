import os
import time
import mock
from datetime import datetime

import suds

from mamba.soap.suds_client import SudsClient
from mamba.test.unittest import TestCase
from mamba.soap.client_adapter import ClientAdapter


class SudsClientTestCase(TestCase):
	client = None

	def setUp(self):
		if not SudsClientTestCase.client:
			self.wsdl = 'file://' + os.path.realpath(os.path.dirname(os.path.realpath(__file__)) + '/../data/dummy.wsdl')
			SudsClientTestCase.client = SudsClient(self.wsdl)
		self.client = SudsClientTestCase.client


class SudsClientImplementSoapClientInterfaceTest(SudsClientTestCase):

	def test_implement_interface(self):
		self.assertImplementInterface(ClientAdapter, self.client)


class SudsClientInitTest(SudsClientTestCase):

	def test_set_proper_client_options(self):
		self.assertIsInstance(self.client, SudsClient)
		assert self.client.client.service is not None
		suds_client = self.client.client
		self.assertTrue(self.client.client.options.retxml)
		self.assertEquals(suds.client.Client, suds_client.__class__)


class SudsClientSetHeadersTest(SudsClientTestCase):

	def test_set_proper_headers(self):
		headers = {'Session': {'SecurityToken': '', 'SequenceNumber': '', 'SessionId': ''}}
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