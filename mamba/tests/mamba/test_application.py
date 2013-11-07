
from os import path
from mamba.application import BasicApplication, NoConfigurationError
from mamba.test import unittest

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


class BaseApplicationTestCase(unittest.TestCase):

    def setUp(self):
        self.ini_path = path.realpath(this_path + '/data/application.ini')
        self.doc_root = path.realpath(this_path)
        self.ini_folder_path = path.realpath(this_path + '/data')
        self.application = self._make_basic_app('test', self.ini_path, self.doc_root)

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

    def _make_basic_app(self, application_env=None, ini_path=None, doc_root=None):
        return BasicApplication(
            application_env = application_env,
            ini_path = ini_path,
            doc_root = doc_root
        )
