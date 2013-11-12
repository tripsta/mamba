import sys
import logging
from collections import deque
from functools import partial
import threading
from time import sleep
from os import path

from twisted.python.log import textFromEventDict

_INFO_FILTERS = (logging.DEBUG, logging.INFO)

class InfoFilter(logging.Filter):
	def filter(self, rec):
		return rec.levelno in _INFO_FILTERS


class ErrorFilter(logging.Filter):
	def filter(self, rec):
		return rec.levelno not in _INFO_FILTERS


StopLogging = object()

class Logger(object):

	def __init__(self, setupFunction=None):
		super(Logger, self).__init__()
		self.logger = setupFunction()

	def __getattr__(self, attr):
		"""
		@attr: delegate to logger
		@return True immediately
		"""

		logger_method = getattr(self.logger, attr)
		if logger_method:
			return logger_method
		else:
			return super(self).__getattr__(attr)

	def setupLogger(self, setupFunction):
		self.logger = setupFunction()

	def startLogging(self):
		pass

	def stopLogging(self):
		pass


class ThreadedLogger(Logger):
	"""
	Does logging in a separate thread, thus behaving well with nonblocking code,
	while allowing for arbitrary python logger configurations.
	Though, if for example the python logging backend is test to something blocking it might delay (but not block) ;-)
	"""

	def __init__(self, setupFunction=None):
		Logger.__init__(self, setupFunction)
		self.messages = deque()
		self.thread = None

	def __getattr__(self, attr):
		"""
		@attr: if it is a logger method do a partial function application
			   and queue it up for the logging thread to process
		@return True immediately
		"""

		logger_method = Logger.__getattr__(self, attr)
		if callable(logger_method):
			def wrapper(*args, **kwargs):
				self.messages.append(partial(logger_method, *args, **kwargs))
				return True

			return wrapper
		else:
			return super(self).__getattr__(attr)

	def setupLogger(self, setupFunction, start=False):
		if self.thread:
			self.stopLogging()
		self.logger = setupFunction()
		if start:
			self.startLogging()

	def run(self):
		while True:
			try:
				nextCallable = self.messages.popleft()
				if callable(nextCallable):
					nextCallable()
				elif nextCallable is StopLogging:
					return
			except IndexError:
				sleep(0.1)

	def startLogging(self):
		self.thread = threading.Thread(target=self.run)
		self.thread.start()

	def stopLogging(self):
		if self.thread:
			self.messages.append(StopLogging)
			self.thread.join()
			self.thread = None


class TwistedThreadedLoggingObserver(object):
	"""
	Output twisted log messages to the logger thread in a nonblocking fashion
	"""

	def __init__(self, setupFunction=None):
		super(TwistedThreadedLoggingObserver, self).__init__()
		self.logger = ThreadedLogger(setupFunction)
		self.logger.startLogging()

	def __call__(self, eventDictToLog):
		if 'logLevel' in eventDictToLog:
			level = eventDictToLog['logLevel']
		elif eventDictToLog['isError']:
			level = logging.ERROR
		else:
			level = logging.INFO

		text = textFromEventDict(eventDictToLog)
		if text is None:
			return
		self.logger.log(level, text)

	def __del__(self):
		self.logger.stopLogging()


class TwistedLoggingObserver(object):
	"""
	Output twisted log messages to the logger thread in a nonblocking fashion
	"""

	def __init__(self, setupFunction=None):
		super(TwistedLoggingObserver, self).__init__()
		self.logger = Logger(setupFunction)

	def __call__(self, eventDictToLog):
		if 'logLevel' in eventDictToLog:
			level = eventDictToLog['logLevel']
		elif eventDictToLog['isError']:
			level = logging.ERROR
		else:
			level = logging.INFO

		text = textFromEventDict(eventDictToLog)
		if text is None:
			return
		self.logger.log(level, text)


__all__ = ['ThreadedLogger', 'Logger' 'TwistedThreadedLoggingObserver', 'TwistedLoggingObserver']
