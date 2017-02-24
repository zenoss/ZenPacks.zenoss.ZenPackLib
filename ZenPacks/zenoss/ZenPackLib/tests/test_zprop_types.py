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
    Ensure that zproperty types are respected
"""
from ZenPacks.zenoss.ZenPackLib.tests.ZPLTestBase import ZPLTestBase


YAML_DOC = """
name: ZenPacks.zenoss.ZenPackLib
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
  zLongProperty:
    type: long
    default: 0
classes:
  BasicDevice:
    base: [zenpacklib.Device]
    properties:
      dateTimeProperty:
        type: date
        default: 1975/08/21 00:00:00 UTC
      stringProperty:
        type: string
        default: ''
      passwordProperty:
        type: password
      booleanProperty:
        default: false
        type: boolean
      intProperty:
        default: 1
        type: int
      floatProperty:
        default: 1.0
        type: float
      longProperty:
        default: 0
        type: long
      linesProperty:
        type: lines
        default: ['this','that']
"""


class TestZenProperties(ZPLTestBase):
    """
    Ensure that property/zproperty types are respected
    """

    yaml_doc = YAML_DOC

    def test_zProperties(self):
        for spec in self.z.cfg.zProperties.values():
            prop = spec._property
            prop_cls = prop.property_class
            prop_val = prop.default
            self.is_valid(prop, prop_cls, prop_val)

    def test_properties(self):
        spec = self.z.cfg.classes.get('BasicDevice')
        for p_spec in spec.properties.values():
            prop = p_spec._property
            prop_cls = prop.property_class
            prop_val = prop.default
            self.is_valid(prop, prop_cls, prop_val)

    def is_valid(self, spec, target_type, target_value):
        ''''''
        self.assertTrue(isinstance(spec.default, target_type),
                'Property ({}) should be {}, got {}'.format(spec.name,
                                                            target_type.__name__,
                                                            type(spec.default).__name__))
        self.assertEquals(spec.default, target_value,
                'Property ({}) should be {}, got {}'.format(spec.name,
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
