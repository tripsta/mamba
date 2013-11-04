from os import path
from mamba.application import BasicApplication

try:
	Mamba
except ImportError:
	doc_root = path.realpath(path.dirname(__file__))
	Mamba = BasicApplication(application_env= 'test', doc_root=doc_root)
