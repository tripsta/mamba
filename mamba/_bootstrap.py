from os import path
from config.pyconfigini import parse_ini

class _TP24(object):

	APPLICATION_ENV = None

	'''
	Singleton Pattern
	'''
	_instance = None
	def __new__(cls, *args, **kwargs):
		if not cls._instance:
			cls._instance = super(_TP24, cls).__new__(cls, *args, **kwargs)
			cls._instance.doc_root = path.realpath(path.dirname(path.realpath(__file__)))
			try:
				env = kwargs.pop('application_env')
				cls._instance.APPLICATION_ENV = env
			except KeyError:
				if cls._instance.APPLICATION_ENV is None:
					config_section_file = path.join(cls._instance.doc_root, 'app/config/application.id')
					with open(config_section_file, 'r') as f:
						section = f.read()
					cls._instance.APPLICATION_ENV = section

			cls._instance.config = cls._instance._initConfig()

		return cls._instance

	def __init__(self, application_env=None):
		object.__init__(self)

	def _initConfig(self):
		config_file = path.join(self.doc_root, 'app/config/application.ini')
		config = parse_ini(config_file, self.APPLICATION_ENV)

		return config

	def path(self, partial_path=''):
		return path.realpath(self.doc_root + partial_path)