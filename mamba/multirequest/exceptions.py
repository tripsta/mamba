from mamba.helpers import decode_unless_unicode
from copy import deepcopy

class _BaseException(Exception):
    code = None

    def __init__(self, message):
        Exception.__init__(self, message)
        if isinstance(message, (Exception,)):
            self.message = decode_unless_unicode(message.message)
        else:
            self.message = decode_unless_unicode(message)

    def to_dict(self):
        return {"code": self.code, "message": self.message}

    def __str__(self):
        return self.message.encode("UTF-8")


class WebserviceError(_BaseException):
    code = 100


class FormatError(_BaseException):
    code = 300


class ValidationError(_BaseException):
    code = 350


class InternalError(_BaseException):
    code = 500

__all__ = ['WebserviceError', 'FormatError', 'ValidationError', 'InternalError']
