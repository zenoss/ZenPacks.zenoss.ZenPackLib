#!/usr/bin/env python

##############################################################################
#
# Copyright (C) Zenoss, Inc. 2018, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################
"""
    Ensure that zproperty types are respected
"""
from ZenPacks.zenoss.ZenPackLib.tests import ZPLBaseTestCase


YAML_DOC = """
name: ZenPacks.zenoss.ZPropertyTest
zProperties:

  zStringProperty:
    type: string
    default: ''
  zPasswordProperty:
    type: password
  zBooleanProperty:
    default: false
    type: boolean
  zIntProperty:
    default: 1
    type: int
  zFloatProperty:
    default: 1.0
    type: float
  zLinesProperty:
    type: lines
    default: ['this','that']
"""


class TestZenProperties(ZPLBaseTestCase):
    """
    Ensure that zproperty types are respected
    """
    yaml_doc = YAML_DOC

    def test_zProperties(self):
        config = self.configs.get('ZenPacks.zenoss.ZPropertyTest')
        cfg = config.get('cfg')
        zprops = cfg.zProperties
        self.is_valid(zprops.get('zStringProperty'), str, '')
        self.is_valid(zprops.get('zPasswordProperty'), str, '')
        self.is_valid(zprops.get('zBooleanProperty'), bool, False)
        self.is_valid(zprops.get('zIntProperty'), int, 1)
        self.is_valid(zprops.get('zFloatProperty'), float, 1.0)
        self.is_valid(zprops.get('zLinesProperty'), list, ['this', 'that'])

    def is_valid(self, spec, target_type, target_value):
        ''''''
        self.assertTrue(isinstance(spec.default, target_type),
                'zProperty ({}) should be {}, got {}'.format(spec.name,
                                                                      target_type.__name__,
                                                                      type(spec.default).__name__))
        self.assertEquals(spec.default, target_value,
                'zProperty ({}) should be {}, got {}'.format(spec.name,
                                                            target_value,
                                                            spec.default))


def test_suite():
    """Return test suite for this module."""
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestZenProperties))
    return suite

if __name__ == "__main__":
    from zope.testrunner.runner import Runner
    runner = Runner(found_suites=[test_suite()])
    runner.run()
