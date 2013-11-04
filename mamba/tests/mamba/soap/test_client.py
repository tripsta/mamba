# import sys
# import os
from twisted.trial import unittest
# from mamba.soap.client import SoapClient
# import suds
# import fixtures

# wsdl = 'file://' + os.path.realpath(os.path.dirname(os.path.realpath(__file__)) + '/../../../app/apis/amadeus/liveTest/1ASIWT2FTRP_PDT_07September11.wsdl')
# testClient = SoapClient(wsdl)

class SoapClientTestCase(unittest.TestCase):
	pass
	# def test_init_set_proper_client_options(self):
	# 	self.assertIsInstance(testClient, SoapClient)
	# 	assert testClient.client.service is not None
	# 	sudsClient = testClient.client
	# 	self.assertTrue(testClient.client.options.nosend)
	# 	self.assertEquals(suds.client.Client, sudsClient.__class__)

	# def test_send_raise_method_not_found(self):
	# 	self.assertRaises(suds.MethodNotFound, testClient.body, 'FooBar', {})

	# def test_set_headers_set_proper_options(self):
	# 	headers = {'Session': {'SecurityToken': '', 'SequenceNumber': '', 'SessionId': ''}}
	# 	testClient.setHeaders(headers)
	# 	self.assertEquals(headers, testClient.client.options.soapheaders)
