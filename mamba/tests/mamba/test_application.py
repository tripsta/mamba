from twisted.trial import unittest
from os import path
from mamba.application import BasicApplication

this_path = path.realpath(path.dirname(__file__))


class TestingInitializers(BasicApplication):
	def _initFoo(self):
		return 'foobar'

	def _initFooBar(self):
		return 'foobarbaz'

	def _initFooBarBaz(self):
		return 'foobarbazbar'


class BaseApplicationTest(unittest.TestCase):

	def setUp(self):
		self.ini_path = path.realpath(this_path + '/data/application.ini')
		self.doc_root = path.realpath(this_path)
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
		app = TestingInitializers(application_env='test', ini_path=self.ini_path, doc_root=self.doc_root)
		for attr, expected in {'foo': 'foobar', 'foobar': 'foobarbaz', 'foobarbaz': 'foobarbazbar'}.iteritems():
			self.assertTrue(attr in app._init_lazily)
			self.assertEquals(expected, getattr(app, attr))

	def _make_basic_app(self, application_env=None, ini_path=None, doc_root=None):
		return BasicApplication(
			application_env = application_env,
			ini_path = ini_path,
			doc_root = doc_root
		)