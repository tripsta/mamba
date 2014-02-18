from twisted.internet import reactor, defer
from mamba.multirequest.core import FakeRequestCallable

def ping(request):
	return FakeRequestCallable(reactor)

def fail(request):
	f = FakeRequestCallable(reactor, shouldfail=True)
	return f

__all__ = ["ping", "fail"]
