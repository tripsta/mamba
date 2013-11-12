from time import time
import logging
from collections import deque
from mamba.test.unittest import TestCase
from mamba.logger import TwistedThreadedLoggingObserver
from mamba.logger import ThreadedLogger


class ArrayLogger(object):
	def __init__(self):
		super(ArrayLogger, self).__init__()
		self.logs = []

	def createMethod(self, level):
		def actualMethod(*args, **kwargs):
			self.logs.append((level, time(), args, kwargs))
			return True
		return actualMethod

	def __getattr__(self, attr):
		return self.createMethod(attr)

def _setupArrayLogger():
	return ArrayLogger()


class TwistedThreadedLoggerObserverTest(TestCase):

	def setUp(self):
		self.logger = TwistedThreadedLoggingObserver(_setupArrayLogger)

	def tearDown(self):
		# DO NOT REMOVE force garbage collection of observer to release thread
		self.logger = None

	def test_init_with_setup_function(self):
		self.assertIsInstance(self.logger.logger.logger, ArrayLogger)

	def test_is_callable(self):
		self.assertTrue(callable(self.logger))

	def test_stress_test_logging(self):
		for i in xrange(0, 10):
			self.logger({'logLevel': logging.INFO, 'message': 'foo {0}'.format(i)})
		self.logger.logger.stopLogging()
		self.assertEqual(10, len(self.logger.logger.logger.logs))
		for log in self.logger.logger.logger.logs:
			self.assertEqual('log', log[0])


class ThreadedLoggerTestCase(TestCase):

	def setUp(self):
		self.logger = ThreadedLogger(_setupArrayLogger)
		# self.logger.startLogging()

	def tearDown(self):
		self.logger.stopLogging()

	def test_init_assign(self):
		self.assertIsInstance(self.logger.messages, deque)
		self.assertIsInstance(self.logger.logger, ArrayLogger)
		self.assertIsNone(self.logger.thread)

	def test___getattr__add_messages(self):
		self.logger.info('foo')
		self.assertEqual(1, len(self.logger.messages))
		self.logger.startLogging()
		self.logger.stopLogging()
		self.assertEqual('foo', self.logger.logger.logs[0][2][0])

	def test___getattr___return_true_if_logger_has_attr(self):
		self.assertTrue(self.logger.info('foo'))

	def test_stopLogging_stop_thread(self):
		self.logger.startLogging()
		self.assertIsNotNone(self.logger.thread)
		self.logger.stopLogging()
		self.assertIsNone(self.logger.thread)