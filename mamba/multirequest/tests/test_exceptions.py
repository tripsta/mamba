from mamba.test import unittest
from mamba.multirequest.exceptions import InternalError

class SessionUnavailableError(InternalError):
    code = 501
    def __init__(self):
        InternalError.__init__(self, "STS Session Unavailable")

class SessionUnavailableTestCase(unittest.TestCase):

    def setUp(self):
        self.session_exc = SessionUnavailableError()

    def test_inherit_from_InternalError(self):
        self.assertIsInstance(self.session_exc, InternalError)

    def test_code_is_not_500(self):
        self.assertEquals(self.session_exc.code, 501)
