from mamba.test import unittest
from mamba.multirequest.exceptions import InternalError

class SessionUnavailableError(InternalError):
    code = 501
    def __init__(self, message = "STS Session Unavailable", transactionId = 4):
        InternalError.__init__(self, message, transactionId)

class ExceptionTest(Exception):
    message = 'foo'
    transactionId = 5

class SessionUnavailableTestCase(unittest.TestCase):

    def setUp(self):
        self.session_exc = SessionUnavailableError()

    def test_inherit_from_InternalError(self):
        self.assertIsInstance(self.session_exc, InternalError)

    def test_code_is_not_500(self):
        self.assertEquals(self.session_exc.code, 501)

    def test_transactionId_is_set_when_message_not_exception(self):
        self.assertEquals(self.session_exc.transactionId, '4')

    def test_transactionId_is_set_when_message_exception(self):
        message = ExceptionTest()
        message.transactionId = 5
        self.session_exc = SessionUnavailableError(message)
        self.assertEquals(self.session_exc.transactionId, '5')