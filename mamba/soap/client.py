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
		if re.search('(xmlns:ns)+([0-9])+(="http://schemas.xmlsoap.org/soap/envelope/")', context.envelope):
			context.envelope = re.sub('(xmlns:ns)+[0-9]+(="http://schemas.xmlsoap.org/soap/envelope/")', '', context.envelope)
			context.envelope = re.sub('(<ns)+([0-9])+(:)', '<SOAP-ENV:', context.envelope)
			context.envelope = re.sub('(</ns)+([0-9])+(:)', '</SOAP-ENV:', context.envelope)

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





if __name__ == '__main__':
	from twisted.internet import task
	from twisted.internet import reactor
	def runEverySecond():
		print "a second has passed"
	def gotBody(request):
		print request.envelope
	l = task.LoopingCall(runEverySecond)
	l.start(0.1)
	# wsdl = 'file://' + os.path.realpath(os.path.dirname(os.path.realpath(__file__)) + '/../../app/apis/amadeus/liveTest/1ASIWT2FTRP_PDT_07September11.wsdl')
	wsdl = 'file:///home/johnecon/project/pythepie/pythepie/app/apis/amadeus/liveTest/1ASIWT2FTRP_PDT_07September11.wsdl'
	soapClient = SoapClient(wsdl)
	userIdentifier = {'originIdentification': {'sourceOffice':'ATHGR28BL'}, 'originatorTypeCode': 'U', 'originator': 'WSTRPT2F'}
	dutyCode = {'dutyCodeDetails': {'referenceQualifier': 'DUT', 'referenceIdentifier': 'SU'}}
	systemDetails = {'organizationDetails': {'organizationId': 'NMC-GREECE'}}
	passwordInfo = {'dataLength': '10', 'dataType': 'E', 'binaryData': 'Y3JhdWtiZWxpbg=='}
	soapClient.setHeaders({'Session': {'SequenceNumber': '', 'SessionId': '', 'SecurityToken': ''}})
	d = soapClient.body('Security_Authenticate', dict(dictdutyCode=dutyCode, userIdentifier=userIdentifier, systemDetails=systemDetails, passwordInfo=passwordInfo))
	d.addCallback(gotBody)
	reactor.run()