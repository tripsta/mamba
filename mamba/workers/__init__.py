from __future__ import print_function, division
from random import random
from twisted.python import log
from twisted.internet.defer import DeferredList
from mamba import await


def _connector(workers, max_wait=1.0):
    """
    Calls worker method for each gearmanized subclass instance
    Returns DeferredList
    """
    log.msg("Registering gearman workers")

    deferred_list = []
    for worker in workers:
        wait_time = (random() * max_wait) + 0.0001
        d = await(wait_time)
        d.addCallback(worker.worker)
        deferred_list.append(d)

    return DeferredList(deferred_list)


def gearmanize(gearmanized_subclass, how_many, *args, **kwargs):
    """
    Creates Geamanized instances
    Return tuple of 2 items a list of instances and a connector function
    """
    workers = [gearmanized_subclass(i, *args, **kwargs) for i in xrange(how_many)]

    return workers, _connector
