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
from types import NoneType
from ZenPacks.zenoss.ZenPackLib.tests import ZPLBaseTestCase
from DateTime import DateTime

YAML_DOC = """
name: ZenPacks.zenoss.PropertyTest
zProperties:
  zStringProperty:
    type: string
    default: 'TEST'
  zPasswordProperty:
    type: password
    default: TEST
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
    default: 10000000
  zStringPropertyUnset:
    type: string
  zPasswordPropertyUnset:
    type: password
  zBooleanPropertyUnset:
    type: boolean
  zIntPropertyUnset:
    type: int
  zFloatPropertyUnset:
    type: float
  zLinesPropertyUnset:
    type: lines
  zLongPropertyUnset:
    type: long
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
        default: true
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


class TestPropertyTypes(ZPLBaseTestCase):
    """
    Ensure that _properties/zProperties types are respected
    """
    yaml_doc = YAML_DOC
    disableLogging = False

    def test_zProperties(self):
        config = self.configs.get('ZenPacks.zenoss.PropertyTest')
        cfg = config.get('cfg')
        zprops = cfg.zProperties
        self.is_valid(zprops.get('zStringProperty'), str, 'TEST', 'zProperty')
        self.is_valid(zprops.get('zPasswordProperty'), str, 'TEST', 'zProperty')
        self.is_valid(zprops.get('zBooleanProperty'), bool, False, 'zProperty')
        self.is_valid(zprops.get('zIntProperty'), int, 1, 'zProperty')
        self.is_valid(zprops.get('zFloatProperty'), float, 1.0, 'zProperty')
        self.is_valid(zprops.get('zLinesProperty'), list, ['this', 'that'], 'zProperty')
        self.is_valid(zprops.get('zLongProperty'), long, 10000000, 'zProperty')

        self.is_valid(zprops.get('zStringPropertyUnset'), str, '', 'zProperty')
        self.is_valid(zprops.get('zPasswordPropertyUnset'), str, '', 'zProperty')
        self.is_valid(zprops.get('zBooleanPropertyUnset'), bool, False, 'zProperty')
        self.is_valid(zprops.get('zIntPropertyUnset'), NoneType, None, 'zProperty')
        self.is_valid(zprops.get('zFloatPropertyUnset'), NoneType, None, 'zProperty')
        self.is_valid(zprops.get('zLinesPropertyUnset'), list, [], 'zProperty')
        self.is_valid(zprops.get('zLongPropertyUnset'), NoneType, None, 'zProperty')

    def test_properties(self):
        config = self.configs.get('ZenPacks.zenoss.PropertyTest')
        cfg = config.get('cfg')
        spec = cfg.classes.get('BasicDevice')
        props = spec.properties
        self.is_valid(props.get('dateTimeProperty'), DateTime, DateTime('1975/08/21 00:00:00 UTC'), '_property')
        self.is_valid(props.get('stringProperty'), str, '', '_property')
        self.is_valid(props.get('passwordProperty'), str, '', '_property')
        self.is_valid(props.get('booleanProperty'), bool, True, '_property')
        self.is_valid(props.get('intProperty'), int, 1, '_property')
        self.is_valid(props.get('floatProperty'), float, 1.0, '_property')
        self.is_valid(props.get('linesProperty'), list, ['this', 'that'], '_property')
        self.is_valid(props.get('longProperty'), long, 0, '_property')

    def is_valid(self, spec, target_type, target_value, p_type):
        """Validate property type and default value"""
        # verify property type
        self.assertTrue(isinstance(spec.default, target_type),
            '{} ({}) should be {}, got {}'.format(
            p_type, spec.name, target_type.__name__, type(spec.default).__name__))

        # verify default value
        self.assertEquals(spec.default, target_value,
            '{} ({}) should be {}, got {}'.format(
            p_type, spec.name, target_value, spec.default))


def test_suite():
    """Return test suite for this module."""
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestPropertyTypes))
    return suite


if __name__ == "__main__":
    from zope.testrunner.runner import Runner
    runner = Runner(found_suites=[test_suite()])
    runner.run()
