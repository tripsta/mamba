import sys
import os
this_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.abspath(this_path + './../../../app'))
sys.path.append(os.path.abspath(this_path + './../../../lib'))
sys.path.append(os.path.abspath(this_path + './../../data'))
from pythepie.lib.soap.client import SoapClient
import suds
import fixtures
from pythepie.lib.test.testcase import *

wsdl = 'file://' + os.path.realpath(os.path.dirname(os.path.realpath(__file__)) + '/../../../app/apis/amadeus/liveTest/1ASIWT2FTRP_PDT_07September11.wsdl')
testClient = SoapClient(wsdl)

class SoapClientTestCase(TestCase):
	def test_init_set_proper_client_options(self):
		self.assertIsInstance(testClient, SoapClient)
		assert testClient.client.service is not None
		sudsClient = testClient.client
		self.assertTrue(testClient.client.options.nosend)
		self.assertEquals(suds.client.Client, sudsClient.__class__)

	def test_send_raise_method_not_found(self):
		self.assertRaises(suds.MethodNotFound, testClient.body, 'FooBar', {})

	def test_set_headers_set_proper_options(self):
		headers = {'Session': {'SecurityToken': '', 'SequenceNumber': '', 'SessionId': ''}}
		testClient.setHeaders(headers)
		self.assertEquals(headers, testClient.client.options.soapheaders)
