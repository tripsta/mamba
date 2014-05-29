from twisted.internet import reactor, task

def await(sec):
    return task.deferLater(reactor, sec, lambda *a: True)
