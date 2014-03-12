from setuptools import setup, find_packages

setup(
	name = 'mamba',
	packages = find_packages(),
	version = '0.1.13',
	description = 'Tripsta python utility library',
	author = 'Tripsta SA',
	author_email = 'developers@travelplanet24.com',
	url = 'https://github.com/tripsta/mamba',
	long_description = """\
Tripsta python utility library

- Zend-like configuration with .ini files (built on top of https://bitbucket.org/maascamp/pyconfigini/src/f2b0f95b53d5/pyconfigini.py?at=default)
- bootstrapping according to environment supporting lazy initializers
- Testing classes and Decorators
- Soap Client
- Twisted helper classes
- Multirequest utility classes

Works with python 2.7.x
"""

)
