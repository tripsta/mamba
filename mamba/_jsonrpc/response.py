import json
import sys

"""
Credits go to https://github.com/dmora/python-mixin-json-rpc2/blob/master/jsonrpc2/mixin.py
"""
#corresponding spec version
RPC_VERSION = "2.0"

class BaseJSONRPCException(Exception):
    """ Base Exception for all RPC related exceptions"""
    pass

class ResourceResponseJSONEncoder(json.JSONEncoder):
    """ Encoder for JSON RPC Messages going out of the server.

    Just a Object oriented style to handle the correct format according to the
    JSON-RPC spec.

    The result of a method being invoked in a alternate library will result
    on a ResourceResponse object that can be encoded using this logic.

    Provides also an alternate way to block attributes that should not be
    transferred through the protocol.
    """
    def default(self, obj):
        if isinstance(obj, BaseResourceResponse):
            response = {"jsonrpc" : RPC_VERSION}
            for field in dir(obj):
                if not field.startswith('_') and not field in obj._exclude:
                    value = getattr(obj, field)
                    response[field] = value
            return response
        return json.JSONEncoder.default(self, obj)

class BaseResourceResponse(object):
    """Base Class for all Responses from the RPC implementation.

    The idea here is to handle responses as "views". Since we have the
    ResourceResponseJSONEncoder in place, we can just simple assign attributes
    to this class or any extending class that are going to be transferred trough
    the protocol.

    Extending the Protocol itself is as simple as extending this object.
    """
    def __init__(self, request_id):
        self.id = request_id
        # Members to exclude when encoding
        self._exclude = []

    def __str__(self, *args, **kwargs):
        return json.dumps(self, cls=ResourceResponseJSONEncoder)

class InternalError(BaseResourceResponse):
    """The error response for a Internal RPC provider Error"""
    def __init__(self, request_id = None, message = None):
        BaseResourceResponse.__init__(self, request_id)
        self.error = {"code": -32603, "message": message}

class NonExistentMethodError(BaseResourceResponse):
    """The error response for a Non Existent Method"""
    def __init__(self, request_id = None):
        BaseResourceResponse.__init__(self, request_id)
        self.error = {"code": -32601, "message": "Method not found."}

class InvalidJSONError(BaseResourceResponse):
    """The error response for a Invalid JSON (parse error)"""
    def __init__(self, request_id = None):
        BaseResourceResponse.__init__(self, request_id)
        self.error = {"code": -32700, "message": "Parse error."}

class UnsupportedJsonRpcVersionError(BaseResourceResponse):
    """The error response for a invalid Request Object"""
    def __init__(self, request_id = None):
        BaseResourceResponse.__init__(self, request_id)
        self.error = {"code": -32600, "message": "Unsupported Json Rpc Version."}

class CustomException(BaseResourceResponse):
    """The error response for a custom exception

    Use this when using a Exception (code and message) style of API implementation
    for error handling and by extending the BaseJSONRPCException
    """
    def __init__(self, e, request_id = None):
        BaseResourceResponse.__init__(self, request_id)
        self.error = {"code": e.code , "message": e.message}

class SuccessResponse(BaseResourceResponse):
    """Identifies a sucessful response

    Extend this class and return it on your service methods, this way the library
    will make use of the new Sucess Response.
    """
    def __init__(self, result, request_id = None):
        BaseResourceResponse.__init__(self, request_id)
        self.result = result