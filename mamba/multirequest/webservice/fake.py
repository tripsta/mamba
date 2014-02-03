from twisted.internet import reactor, defer
from mamba.multirequest.core import FakeRequestCallable

def ping(request):
	return FakeRequestCallable(reactor)

__all__ = ["ping"]
