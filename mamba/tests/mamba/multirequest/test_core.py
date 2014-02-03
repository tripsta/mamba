from mamba.test import unittest
from twisted.internet import task, defer
from mamba.multirequest import core

def returns_deferred():
	return defer.succeed(1)

def returns_a_value():
	return 1


class RequestCallableTestCase(unittest.TestCase):

	def setUp(self):
		self.fake_reactor = task.Clock()
		self.request = core.FakeRequestCallable(self.fake_reactor)

	def test_is_callable(self):
		self.assertTrue(callable(self.request))

	def test_is_IRequestCallable(self):
		self.assertImplements(core.IRequestCallable, self.request)

	def test_returns_deferred(self):
		self.assertIsInstance(self.request(), defer.Deferred)


class DefaultRequestRunnerTestCase(unittest.TestCase):

	def setUp(self):
		self.fake_reactor = task.Clock()
		self.runner = core.BasicRequestRunner(self.fake_reactor)

	def test_implements_IRequestRunner(self):
		self.assertImplements(core.IRequestRunner, self.runner)


class BasicRequestRunnerRunRequestsTestCase(unittest.TestCase):

	def setUp(self):
		self.fake_reactor = task.Clock()
		self.runner = core.BasicRequestRunner(self.fake_reactor)

	def test_run_requests_return_deferred(self):
		req = core.FakeRequestCallable(self.fake_reactor)
		d = self.runner.run_requests(req)
		self.assertIsInstance(d, defer.DeferredList)

	def test_run_requests_raise_TypeError_if_request_not_callable(self):
		self.assertRaises(TypeError, self.runner.run_requests, 1)

	def test_run_requests_accept_any_callable_as_param(self):
		self.assertNotRaiseException(TypeError,
									 self.runner.run_requests,
									 returns_deferred)

	def test_run_requests_accept_any_callable_as_param(self):
		self.assertNotRaiseException(TypeError,
									 self.runner.run_requests,
									 [returns_deferred, returns_deferred])

