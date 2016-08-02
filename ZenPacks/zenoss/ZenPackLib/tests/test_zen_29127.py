#!/usr/bin/env python

##############################################################################
#
# Copyright (C) Zenoss, Inc. 2015, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

"""
    This is designed to test whether or not a relation added to a 
    zenpacklib.Device subclass wipes out other relations added to 
    Products.ZenModel.Device (ZEN-29127)
"""

# stdlib Imports
import os
import unittest
import logging
import traceback
from Products.ZenTestCase.BaseTestCase import BaseTestCase

logging.basicConfig(level=logging.INFO)
log = logging.getLogger('zen.zenpacklib.tests')

from ZenPacks.zenoss.ZenPackLib import zenpacklib

# Zenoss Imports
import Globals  # noqa
from Products.ZenUtils.Utils import unused
unused(Globals)


class TestZen21927(unittest.TestCase):

    """Specs test suite."""
    zps = []

    def setUp(self):
        fdir = '%s/data/yaml' % os.path.dirname(__file__)
        self._file = '%s/%s' % (fdir, 'zen-21927-fail.yaml')

    def test_undefined_relations(self):
        try:
            cfg = zenpacklib.load_yaml(self._file)
        except:
            msg = traceback.format_exc(limit=0)
            self.fail(msg)

def test_suite():
    """Return test suite for this module."""
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestZen21927))
    return suite

if __name__ == "__main__":
    from zope.testrunner.runner import Runner
    runner = Runner(found_suites=[test_suite()])
    runner.run()
