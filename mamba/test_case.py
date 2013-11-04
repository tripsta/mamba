import sys
import os
this_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.abspath(this_path + './../../lib'))

from twisted.trial import unittest
from test_bootstrap import TP24

class TestCase(unittest.TestCase):
	pass
