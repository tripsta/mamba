from twisted.web.server import Site
import ujson
from pythepie.lib.jsonrpc.response import *
from twisted.internet import defer

AVAILABLE_METHODS = ['xsearch']

class JSONRPCFactory(Site):
	error = None

	def __init__(self, resource, logPath=None, timeout=60*60*12):
		Site.__init__(self, resource, logPath, timeout)
		self.resource.factory = self
		self.reactor = None

	def validate_jsonrpc_request(self, body):
		try:
			rpc_request = ujson.loads(body)
		except:
			return self._validation_failed(InvalidJSONError())
		request_id = rpc_request.get('id')
		if len(rpc_request) < 1:
			return self._validation_failed(InvalidJSONError(request_id))

		json_version = rpc_request.get('jsonrpc')
		if json_version != RPC_VERSION:
			return self._validation_failed(UnsupportedJsonRpcVersionError(request_id))

		method = rpc_request.get("method")
		params = rpc_request.get("params")

		if not method or not params or not request_id:
			return self._validation_failed(InvalidJSONError(request_id))

		if method not in AVAILABLE_METHODS:
			return self._validation_failed(NonExistentMethodError(request_id))
		return True

	def _validation_failed(self, response):
		self.error = response
		return False

	def _fail_with_error(self, error):
		d = defer.Deferred()
		self.reactor.callLater(0, lambda: d.errback(error))
		return d