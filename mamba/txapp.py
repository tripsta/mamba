import logger
from twisted.internet import reactor, task
from twisted.python import log
from mamba.helpers import log_with_traceback



def _start_logging(app_name):
    import sys
    log.startLogging(sys.stdout)


def await(sec):
    return task.deferLater(reactor, sec, lambda *a: True)


def react_main(fn, app_name=None, logger_factory=_start_logging, *args, **kwargs):

    if not app_name:
        app_name = fn.__name__

    def log_err(what):
        log_with_traceback(what)
        return what

    def stop_if_running(ignored):
        if reactor.running:
            reactor.stop()

    logger_factory(app_name)

    d = task.deferLater(reactor, 0, fn, *args, **kwargs)
    d.addErrback(log_err)
    d.addBoth(stop_if_running)

    reactor.run()


if __name__ == '__main__':

    def demo():
        print('txapp demo')
        raise ValueError()

    react_main(demo)
