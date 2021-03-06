
from os import path, environ
import os
from mamba.application import BasicApplication, NoConfigurationError
from mamba.test import unittest
from mamba.soap.suds_client import SudsClient
from twisted.internet import reactor, defer, task
from time import time

this_path = path.realpath(path.dirname(__file__))


class CallableInitializer(object):
    def __init__(self, val):
        self.val = val

    def __call__(self):
        return self.val

class TestingInitializerApp(BasicApplication):
    
    def init__Foo(self):
        return 'foobar'

    def init__FooBar(self):
        return 'foobarbaz'

    def init__FooBarBaz(self):
        return 'foobarbazbar'


class TestingCallableInitializerApp(BasicApplication):

    init__Arrays  = CallableInitializer( [1, 2, 3] )
    init__Strings = CallableInitializer( "string" )
    init__Integers = CallableInitializer( 1983 )


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

    def init__a_third_deferred(self):
        d = defer.Deferred()
        task.deferLater(reactor, 1, d.callback, 4)
        return d

    def init__my_product_key(self):
        key = self.config.product.item.key
        return key + key

    @defer.inlineCallbacks
    def init__soap_client(self):
        self.wsdl = 'file://' + os.path.realpath(os.path.dirname(os.path.realpath(__file__)) + '/data/dummy.wsdl')
        d = yield SudsClient(self.wsdl)
        e = yield SudsClient(self.wsdl)
        defer.returnValue([d,e])

class BaseApplicationTestCase(unittest.TestCase):

    def setUp(self):
        self.ini_path = path.realpath(this_path + '/data/application.ini')
        self.doc_root = path.realpath(this_path)
        self.ini_folder_path = path.realpath(this_path + '/data')
        self.application = self._make_basic_app('test', self.ini_path, self.doc_root)

    def tearDown(self):
        if environ.get("APP_ENV"):
            del environ['APP_ENV']

    def test_init_assign_docroot_if_given(self):
        self.assertEquals(self.doc_root, self.application.doc_root)

    def test_init_autoassign_docroot_if_None_given(self):
        self.application = self._make_basic_app('test', self.ini_path, None)
        self.assertEquals(path.realpath(path.realpath(path.dirname('.'))), self.application.doc_root)
    
    def test_init_assign_application_env_if_given(self):
        self.assertEquals(self.application.application_env, 'test')

    def test_init_assign_application_env_from_application_id_file(self):
        ini_path = path.realpath(this_path + '/data/application.ini')
        doc_root = path.realpath(this_path)
        self.application = self._make_basic_app(None, ini_path, doc_root)
        self.assertEquals(self.application.application_env, 'common')

    def test_init_lazy_not_load_config(self):
        self.skipTest("Lazy loading not applicable because of fluentd loading at startup")
        self.assertFalse('config' in self.application._loaded_initializers)

    def test___getattr___lazy_load_config(self):
        config = self.application.config
        self.assertTrue('config' in self.application._loaded_initializers)

    def test___getattr___config_get_overridden_environment_configuration(self):
        self.assertEquals('abc6789', self.application.config.product.item.key)

    def test___setattr___application_env_reload_config(self):
        test_config = self.application.config
        self.application.application_env = 'common'
        self.assertEquals('abc1234', self.application.config.product.item.key)

    def test___setattr___application_env_invalidate_all_loaded_initializers(self):
        ini_path = path.realpath(this_path + '/data/application.ini')
        doc_root = path.realpath(this_path)
        app = ApplicationWithLazyDeferreds(ini_path=ini_path, doc_root=doc_root)
        self.assertEquals(app.my_product_key, "abc1234abc1234")
        app.application_env = 'test'
        self.assertEqual(len(app._loaded_initializers), 0)

    def test___setattr___application_env_invalidate_all_loaded_deferred_initializers(self):
        ini_path = path.realpath(this_path + '/data/application.ini')
        doc_root = path.realpath(this_path)
        app = ApplicationWithLazyDeferreds(ini_path=ini_path, doc_root=doc_root)
        self.assertEquals(app.my_product_key, "abc1234abc1234")
        app.application_env = 'test'
        self.assertEqual(len(app._loaded_deferred_initializers), 0)

    def test___setattr___application_env_use_new_env_on_next_getattr(self):
        ini_path = path.realpath(this_path + '/data/application.ini')
        doc_root = path.realpath(this_path)
        app = ApplicationWithLazyDeferreds(ini_path=ini_path, doc_root=doc_root)
        self.assertEquals(app.my_product_key, "abc1234abc1234")
        app.application_env = 'test'
        self.assertEquals(app.my_product_key, "abc6789abc6789")

    def test___getattr___raise_AttributeError_on_unexpected_property_access(self):
        try:
            self.application.foo
        except AttributeError, e:
            self.assertIsInstance(e, AttributeError)
        else:
            self.fail("unexpected key should raise AttributeError")

    def test_subclass_load_initializers(self):
        app = TestingInitializerApp(application_env='test', ini_path=self.ini_path, doc_root=self.doc_root)
        for attr, expected in {'foo': 'foobar', 'foobar': 'foobarbaz', 'foobarbaz': 'foobarbazbar'}.iteritems():
            self.assertTrue(attr in app._init_lazily)
            self.assertEquals(expected, getattr(app, attr))

    def test__initializer_can_be_any_callable(self):
        app = TestingCallableInitializerApp(application_env='test', ini_path=self.ini_path, doc_root=self.doc_root)
        for attr, expected in {'arrays': [1, 2, 3], 'strings': 'string', 'integers': 1983}.iteritems():
            self.assertTrue(attr in app._init_lazily)
            self.assertEquals(expected, getattr(app, attr))

    def test__init__read_directory(self):
        app = self._make_basic_app('development', self.ini_folder_path, self.doc_root)
        self.assertAttributeNotRaises( (app, 'config'), IOError )

    def test___getattr____config_read_all_contents_of_configuration_folder_if_directory_given(self):
      self.ini_folder_path = path.realpath(this_path + '/data')
      app = self._make_basic_app('test', self.ini_folder_path, self.doc_root)
      self.assertAttributeNotRaises((app.config, 'application'), AttributeError)

    def test_init_config_raise_if_no_ini_files(self):
        self.ini_folder_path = path.realpath(this_path + '/data/dummy')
        app = self._make_basic_app('test', self.ini_folder_path, self.doc_root)
        self.assertAttributeRaises((app, 'config'), NoConfigurationError)

    @defer.inlineCallbacks
    def test_can_handle_deferreds(self):
        app = ApplicationWithLazyDeferreds(application_env='test', ini_path=self.ini_path, doc_root=self.doc_root)
        value = yield app.my_deferred
        self.assertEquals(value, "hello")

    @defer.inlineCallbacks
    def test_getters_that_return_deferreds_always_return_deferreds(self):
        app = ApplicationWithLazyDeferreds(application_env='test', ini_path=self.ini_path, doc_root=self.doc_root)
        value  = yield app.my_deferred
        value2 = yield app.my_deferred
        self.assertEquals(value, value2)

    @defer.inlineCallbacks
    def test_initializers_returning_deferreds_fire_once(self):
        app = ApplicationWithLazyDeferreds(application_env='test', ini_path=self.ini_path, doc_root=self.doc_root)
        value  = yield app.a_deferred_model
        value2 = yield app.a_deferred_model
        value3 = yield app.a_deferred_model
        self.assertEquals(value.time, value2.time)
        self.assertEquals(value2.time, value3.time)

    @defer.inlineCallbacks
    def test_deferred_initializers(self):
        app = ApplicationWithLazyDeferreds(application_env='test', ini_path=self.ini_path, doc_root=self.doc_root)
        value = yield app.a_third_deferred
        yield app.soap_client
        yield app.soap_client
        soap = yield app.soap_client
        self.assertEquals(value, 4)
        self.assertIsInstance(soap[0], SudsClient)

    def test_get_application_env_from_environ(self):
        environ["APP_ENV"] = 'test'
        app = self._make_basic_app(None, self.ini_folder_path, self.doc_root)
        self.assertEquals(app.application_env, 'test')

    def _make_basic_app(self, application_env=None, ini_path=None, doc_root=None):
        return BasicApplication(
            application_env = application_env,
            ini_path = ini_path,
            doc_root = doc_root
        )
