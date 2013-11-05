from mamba.test.unittest import TestCase
from zope.interface import implements, Interface

ArgError = type('ArgError', (ValueError,), {})

class ISystem(Interface):

	def raising_error():
		pass

	def raising_error_with_args(arg1, arg2):
		pass


class UnitUnderTest(object):

	implements(ISystem)

	def raising_error(self):
		raise AttributeError("this raises an error")

	def raising_error_with_args(self, arg1, arg2):
		raise ArgError()


class TestCaseTest(TestCase):

	def test_assertRaisesException(self):
		sut = UnitUnderTest()
		self.assertRaisesException( AttributeError, sut.raising_error )

	def test_assertRaisesException_with_args_and_kwargs(self):
		sut = UnitUnderTest()
		self.assertRaisesException( ArgError, sut.raising_error_with_args, 0, arg2=1 )

	def test_assertAttributeRaises(self):
		sut = UnitUnderTest()
		self.assertAttributeRaises( (sut, 'foo'), AttributeError )

	def test_assertImplements(self):
		sut = UnitUnderTest()
		self.assertImplements(sut, ISystem)
