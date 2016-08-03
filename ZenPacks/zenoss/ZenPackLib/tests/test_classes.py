#!/usr/bin/env python

##############################################################################
#
# Copyright (C) Zenoss, Inc. 2015, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

"""Spec unit tests.

This module tests zenpacklib "Specs". These are the intermediate step
between YAML and Zenoss functionality.

"""

# stdlib Imports
import os
import logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger('zen.zenpacklib.tests')

# Zenoss Imports
import Globals  # noqa
from Products.ZenUtils.Utils import unused
unused(Globals)

from Products.ZenTestCase.BaseTestCase import BaseTestCase

from .ZPLTestHarness import ZPLTestHarness


class TestClasses(BaseTestCase):

    """Specs test suite."""
    zps = []

    def setUp(self):
        fdir = '%s/data/yaml' % os.path.dirname(__file__)
        for f in os.listdir(fdir):
            if '.yaml' not in f:
                continue
            file = os.path.join(os.path.dirname(__file__), 'data/yaml/%s' % f)
            log.info("loading file: %s" % file)
            self.zps.append(ZPLTestHarness(file))

    def test_ClassProperties(self):
        '''
        check that class properties follow the spec
        '''
        log.info("Checking Properties")
        for zp in self.zps:
            self.assertTrue(zp.check_properties(),"Test Failed")

    def test_ClassRelations(self):
        '''
        check that class relations follow the spec
        '''
        log.info("Checking relations")
        for zp in self.zps:
            self.assertTrue(zp.check_cfg_relations(),"Test Failed")

    def test_Templates_YAML(self):
        '''
        check that class relations follow the spec
        '''
        log.info("Checking relations")
        for zp in self.zps:
            self.assertTrue(zp.check_templates_vs_yaml(),"Test Failed")

    def test_Templates_Spec(self):
        '''
        check that class relations follow the spec
        '''
        log.info("Checking relations")
        for zp in self.zps:
            self.assertTrue(zp.check_templates_vs_specs(),"Test Failed")

def test_suite():
    """Return test suite for this module."""
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestClasses))
    return suite

if __name__ == "__main__":
    from zope.testrunner.runner import Runner
    runner = Runner(found_suites=[test_suite()])
    runner.run()
