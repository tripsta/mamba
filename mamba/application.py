from __future__ import absolute_import, division, print_function

import glob
from os import path
from os.path import realpath, join
import inspect
from mamba.config.pyconfigini import parse_ini, _Obj


class NoConfigurationError(Exception):
	pass


class BasicApplication(object):

	DEFAULT_INI_PATH    = 'app/config/application.ini'
	DEFAULT_ENV_ID_PATH = 'app/config/application.id'

	def __init__(self, application_env=None, ini_path=None, doc_root=None):

		self._init_lazily         = {}
		self._loaded_initializers = {}

		if not doc_root:
			doc_root = realpath(path.dirname('.'))

		self.doc_root = realpath(doc_root)

		if not application_env:
			environment_file_path = realpath(join(self.doc_root, self.DEFAULT_ENV_ID_PATH))
			with open(environment_file_path) as env_file:
				environment = env_file.read()
				application_env = environment

		self.application_env = application_env

		if not ini_path:
			ini_path = realpath(join(self.doc_root, self.DEFAULT_INI_PATH))
		self.ini_path =ini_path
		self._populate_lazy_initializers()

	def __setattr__(self, attr, value):
		if attr == 'application_env':
			if 'config' in self._loaded_initializers:
				del self._loaded_initializers['config']
		self.__dict__[attr] = value

	def __getattr__(self, attr):
		if attr in self._init_lazily:
			if attr not in self._loaded_initializers:
				method = getattr(self, self._init_lazily[attr])
				self._loaded_initializers[attr] = method()

			return self._loaded_initializers[attr]

		elif attr in self.__dict__:
			return self.__dict__[attr]

		else:
			raise AttributeError("{} object has no attribute {}".format(self.__class__, attr))

	def init__Config(self):
		config_file = join(self.doc_root, self.ini_path)

		if path.isdir(config_file):
			config = _Obj({'__default__': _Obj()})
			ini_files_in_path = glob.glob("{}/*.ini".format(config_file))
			if len(ini_files_in_path) == 0:
				raise NoConfigurationError("No configuration (.ini) files in {}".format(config_file))

			for ini_file_path in ini_files_in_path:
				head, section_name = path.split(path.splitext(ini_file_path)[0])
				section_config = parse_ini(ini_file_path, self.application_env)
				config[section_name] = section_config
		else:
			config = parse_ini(config_file, self.application_env)

		return config


	def _populate_lazy_initializers(self, lazily=True):
		for attrname, method in inspect.getmembers(self):
			if callable(method) and attrname.startswith("init__"):
				key = attrname.split("init__").pop(-1).lower()
				self._init_lazily[key] = attrname

	def path(self, partial_path=''):
		return realpath(self.doc_root + partial_path)

