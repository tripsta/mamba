import traceback
from twisted.python import log
from twisted.python.failure import Failure

def log_with_traceback(exc, reraise=False, extras={}):
    if isinstance(exc, (Failure,)):
        log.err(exc)
        if reraise:
            return exc
    else:
        tb = traceback.format_exc()
        e = repr(exc)
        messages = [e, tb]
        for key in extras:
            messages.append("{}: {}".format(key, extras[key]))

        log.err("\n".join(messages))
        if reraise:
            raise exc

def decode_unless_unicode(some_string, encoding="utf-8"):
    if isinstance(some_string, unicode):
        return some_string
    try:
        some_string = str(some_string) # in case it is basestring
    except Exception, e:
        pass
    return unicode(some_string, encoding)


def get_refcounts(n=100):
    d = {}

    for m in sys.modules.values():
        for sym in dir(m):
            try:
                o = getattr(m, sym)
                if type(o) is types.ClassType:
                    d[o] = sys.getrefcount (o)
            except Exception, e:
                log_with_traceback(e)

    pairs = map(lambda x: (x[1], x[0]), d.items())
    pairs.sort(reverse=True)

    return pairs[:n]
