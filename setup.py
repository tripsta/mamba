from setuptools import setup, find_packages

setup(
	name = 'mamba',
	packages = find_packages(),
	version = '0.1.8',
	description = 'Tripsta python library',
	author = 'Tripsta SA',
	author_email = 'developers@travelplanet24.com',
	url = 'https://github.com/tripsta/mamba',
	long_description = """\
Tripsta python library

- Zend-like configuration with .ini files
- bootstrapping according to environment supporting lazy initializers
- Testing classes and Decorators
- Soap Client
- Twisted helper classes

Works with python 2.7.x
"""

)
