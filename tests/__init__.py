import unittest
from tests.server_commands import ServerCommandsTestCase

try:
  import hiredis
  use_hiredis = True
except ImportError:
  use_hiredis = False

def all_tests():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(ServerCommandsTestCase))
  return suite
