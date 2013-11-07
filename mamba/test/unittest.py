import sys
from twisted.trial import unittest
import unittest as pyunittest
from zope.interface.exceptions import BrokenImplementation
from zope.interface.verify     import verifyObject
import functools


class TestCase(unittest.TestCase):

	def assertImplementInterface(self, expected_interface, actual_interface):
		self.assertNotRaiseException(BrokenImplementation, verifyObject, expected_interface, actual_interface)

	assertImplements = assertImplementInterface

	def assertRaisesException(self, exception, method, *args, **kargs):
		try:
			method(*args, **kargs)
		except Exception, e:
			exception_raised = sys.exc_info()[0]
			self.assertIsInstance(e, exception)
		else:
			self.fail()

	def assertNotRaiseException(self, exception, method, *args, **kargs):
		exception_raised = False
		try:
			method(*args, **kargs)
		except Exception, e:
			if isinstance(e, exception):
				exception_raised = True
		finally:
			self.assertFalse(exception_raised, "exception {} should not be raised".format(str(exception)))

	def assertAttributeRaises(self, object_and_attr, exception):
		obj, attr = object_and_attr
		_partial = functools.partial(getattr, obj, attr)
		self.assertRaisesException(exception, _partial)

	def assertAttributeNotRaises(self, object_and_attr, exception):
		obj, attr = object_and_attr
		_partial = functools.partial(getattr, obj, attr)
		self.assertNotRaiseException(exception, _partial)
