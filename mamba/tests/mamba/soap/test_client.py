import mock
import os
import suds
import sys
from mamba.test.unittest import TestCase
from mamba.soap.client import SoapClient, SoapEnvelopeNamespaceFix


class TestContext(object):
	envelope = None

	def __init__(self, envelope):
		self.envelope = envelope


class SoapEnvelopeNamespaceFixSendingTestCase(TestCase):
	fix = None

	def setUp(self):
		self.fix = SoapEnvelopeNamespaceFix()

	def test_replace_nothing_if_no_match_is_found(self):
		expected_envelope = "foobar"
		context = TestContext(expected_envelope)
		self.fix.sending(context)
		self.assertEqual(expected_envelope, context.envelope)

	def test_replace_proper_namespace_if_match_is_found(self):
		envelope = 'xmlns:ns0="http://schemas.xmlsoap.org/soap/envelope/" xmlns:ns1="foobar" <ns1:Body>body1</ns1:Body> <ns0:Body>body0</ns0:Body>'
		context = TestContext(envelope)
		self.fix.sending(context)
		self.assertEqual(' xmlns:ns1="foobar" <ns1:Body>body1</ns1:Body> <SOAP-ENV:Body>body0</SOAP-ENV:Body>', context.envelope)

wsdl = 'file://' + os.path.realpath(os.path.dirname(os.path.realpath(__file__)) + '/../data/dummy.wsdl')
test_client = SoapClient(wsdl)


class SoapClientTestCase(TestCase):

	def test_init_set_proper_client_options(self):
		self.assertIsInstance(test_client, SoapClient)
		suds_client = test_client.client
		self.assertTrue(test_client.client.options.nosend)
		self.assertEquals(suds.client.Client, suds_client.__class__)

	def test_send_raise_exception_if_method_not_found(self):
		test_client.client.service = mock.Mock()
		self.assertRaises(Exception, test_client.body, 'FooBar')

	def test_set_headers_set_proper_options(self):
		headers = {'Session': {'SecurityToken': '', 'SequenceNumber': '', 'SessionId': ''}}
		test_client.setHeaders(headers)
		self.assertEquals(headers, test_client.client.options.soapheaders)
