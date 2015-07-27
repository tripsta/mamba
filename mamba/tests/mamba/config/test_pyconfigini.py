import os
from twisted.trial import unittest
from mamba.config.pyconfigini import parse_ini


class ConfigParseIniTestCase(unittest.TestCase):
    def test_parse_ini(self):
        config_file = os.path.join(os.path.dirname(__file__), 'config.ini')

        config = parse_ini(config_file, 'production')
        self.assertEquals('abc-production', config.section1.value)
        self.assertEquals(123, config.value)

        self.assertEquals('foo=bar', config.section2.value)

        config = parse_ini(config_file, 'development')
        self.assertEquals('abc-development', config.section1.value)
        self.assertEquals(123, config.value)

