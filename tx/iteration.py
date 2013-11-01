from twisted.internet import defer
from twisted.python.failure import Failure
from pythepie.app.xtreme.search.helpers.errors import SoapFault, SessionInactive

def runIterator(reactor, iterator):
	try:
		iterator.next()
	except StopIteration:
		pass
	else:
		reactor.callLater(0, runIterator, reactor, iterator)

def wrap_iterator_to_deferred(generator_or_iterator):

	def defer_wrapper(*args):
		d = defer.Deferred()
		results = []
		def _():
			try:
				for solution in generator_or_iterator(*args):
					results.append(solution)
					yield None
				d.callback(results)
			except (SoapFault, SessionInactive, Exception) as e:
				d.errback(Failure(e))

		return d, _()

	return defer_wrapper
