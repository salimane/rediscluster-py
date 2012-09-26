import unittest
from tests.cluster_commands import ClusterCommandsTestCase


def all_tests():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ClusterCommandsTestCase))
    return suite
