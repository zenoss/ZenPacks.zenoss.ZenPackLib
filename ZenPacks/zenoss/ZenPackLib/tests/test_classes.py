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

# Zenoss Imports
import Globals  # noqa
from Products.ZenUtils.Utils import unused
unused(Globals)

from Products.ZenTestCase.BaseTestCase import BaseTestCase
from ZenPacks.zenoss.ZenPackLib.tests.ZPLTestHarness import ZPLTestHarness


class TestClasses(BaseTestCase):

    """Specs test suite."""
    files = []

    def setUp(self):
        fdir = '{}/data/yaml'.format(os.path.abspath(os.path.dirname(__file__)))
        for f in os.listdir(fdir):
            if '.yaml' not in f:
                continue
            file = os.path.join(os.path.dirname(__file__), 'data/yaml/%s' % f)
            self.files.append(file)

    def test_ZP(self):
        for file in self.files:
            try:
                zp = ZPLTestHarness(file)
                self.assertTrue(zp.check_properties(), "Property testing failed for {}".format(zp.filename))
                self.assertTrue(zp.check_cfg_relations(), "Relation testing failed for {}".format(zp.filename))
                self.assertTrue(zp.check_templates_vs_yaml(), "Template (YAML) testing failed for {}".format(zp.filename))
                self.assertTrue(zp.check_templates_vs_specs(), "Template (Spec) testing failed for {}".format(zp.filename))
            except Exception as e:
                print 'Skipping test {} ({})'.format(file, e)


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
