# Mamba (tripsta python lib) 

## Contents

* Application Configuration
* SoapClient for twisted

## Local development

	pip install -e <path-to-mamba-root>

## Provided classes

### mamba.application.BasicApplication

`BasicApplication` is a class that can handle ini reading and bootstrapping of resources in a lazy way

example

    from __future__ import print_function, absolute_import, division
    from mamba.application import BasicApplication

    app = BasicApplication(application_env='test', ini_path='.', doc_root='.')

    print(app.config)

    class MyApp(BasicApplication):

        def init__MySQL(self):
            # do config
            return mysql

        init__mycallable = MyCallable()

methods that return deferreds always return deferreds

    from twisted.internet import defer, reactor, task
    from mamba.application import BasicApplication

    class TestDeferredModel(object):
        def __init__(self):
            self.time = time()


    class ApplicationWithLazyDeferreds(BasicApplication):

        def init__my_deferred(self):
            def _call_fn():
                return "hello"
            return task.deferLater(reactor, 0, _call_fn)

        def init__a_deferred_model(self):
            def _create_object():
                return TestDeferredModel()
            return task.deferLater(reactor, 0, _create_object)


    # using with twisted.internet.defer.inlineCallbacks:
    @defer.inlineCallbacks
    def app_with_deferreds():
        app = ApplicationWithLazyDeferreds()
        v = yield app.my_deferred
        v2 = yield app.a_deferred_model