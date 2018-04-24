#!/usr/bin/env python

##############################################################################
#
# Copyright (C) Zenoss, Inc. 2018, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

""" Multi-YAML import load

Tests YAML loading from multiple files

"""
# zenpacklib Imports
from ZenPacks.zenoss.ZenPackLib import zenpacklib
import yaml
from ZenPacks.zenoss.ZenPackLib.lib.helpers.Dumper import Dumper
from ZenPacks.zenoss.ZenPackLib.lib.helpers.utils import compare_zenpackspecs
from ZenPacks.zenoss.ZenPackLib.lib.base.ZenPack import ZenPack

# Zenoss Imports
import Globals  # noqa
from Products.ZenUtils.Utils import unused
unused(Globals)
from Products.ZenTestCase.BaseTestCase import BaseTestCase

YAML_DOC = """
name: ZenPacks.zenoss.BasicZenPack

zProperties:
  DEFAULTS:
    category: BasicZenPack
  zBasicString:
    default: ''
  zBasicNumeric:
    default: 0

class_relationships:
- BasicDevice 1:MC BasicComponent
- SubComponent M:M AuxComponent

classes:
  BasicDevice:
    base: [zenpacklib.Device]
    monitoring_templates: [BasicDevice]
  BasicComponent:
    base: [zenpacklib.Component]
    monitoring_templates: [BasicComponent]
  SubComponent:
    base: [BasicComponent]
    monitoring_templates: [SubComponent]
  AuxComponent:
    base: [SubComponent]
    monitoring_templates: [AuxComponent]

device_classes:
  /Device:
    templates:
      BasicDevice:
        datasources:
          B:
            type: SNMP
            severity: 5
            datapoints:
              B: {}
            oid: .1.3.6.1.4.1.232.6.2.6.8.1.5
          A:
            type: SNMP
            severity: 5
            datapoints:
              A: {}
            oid: .1.3.6.1.4.1.232.6.2.6.8.1.4
        thresholds:
          a:
            type: MinMaxThreshold
            dsnames: [A_A]
        graphs:
          Basic Device:
            graphpoints:
              B:
                dpName: B_B
              A:
                dpName: A_A
                includeThresholds: true
      BasicComponent:
        datasources:
          A:
            type: SNMP
            severity: 5
            datapoints:
              A: {}
            oid: .1.3.6.1.4.1.232.6.2.6.8.1.4
        thresholds:
          a:
            type: MinMaxThreshold
            dsnames: [A_A]
        graphs:
          Basic Component:
            graphpoints:
              A:
                dpName: A_A
                includeThresholds: true
      SubComponent:
        datasources:
          A:
            type: SNMP
            severity: 5
            datapoints:
              A: {}
            oid: .1.3.6.1.4.1.232.6.2.6.8.1.4
        thresholds:
          a:
            type: MinMaxThreshold
            dsnames: [A_A]
        graphs:
          Sub Component:
            graphpoints:
              A:
                dpName: A_A
                includeThresholds: true
      AuxComponent:
        datasources:
          A:
            type: SNMP
            severity: 5
            datapoints:
              A: {}
            oid: .1.3.6.1.4.1.232.6.2.6.8.1.4
        thresholds:
          a:
            type: MinMaxThreshold
            dsnames: [A_A]
        graphs:
          Aux Component:
            graphpoints:
              A:
                dpName: A_A
                includeThresholds: true
"""


YAML_DOC_1 = """
name: ZenPacks.zenoss.BasicZenPack

zProperties:
  DEFAULTS:
    category: BasicZenPack
  zBasicString:
    default: ''

class_relationships:
- BasicDevice 1:MC BasicComponent

classes:
  BasicDevice:
    base: [zenpacklib.Device]
    monitoring_templates: [BasicDevice]
  BasicComponent:
    base: [zenpacklib.Component]
    monitoring_templates: [BasicComponent]
"""

YAML_DOC_2 = """
classes:

  SubComponent:
    base: [BasicComponent]
    monitoring_templates: [SubComponent]
  AuxComponent:
    base: [SubComponent]
    monitoring_templates: [AuxComponent]
"""

YAML_DOC_3 = """
device_classes:
  /Device:
    templates:
      BasicDevice:
        datasources:
          B:
            type: SNMP
            severity: 5
            datapoints:
              B: {}
            oid: .1.3.6.1.4.1.232.6.2.6.8.1.5
          A:
            type: SNMP
            severity: 5
            datapoints:
              A: {}
            oid: .1.3.6.1.4.1.232.6.2.6.8.1.4
        thresholds:
          a:
            type: MinMaxThreshold
            dsnames: [A_A]
        graphs:
          Basic Device:
            graphpoints:
              B:
                dpName: B_B
              A:
                dpName: A_A
                includeThresholds: true
"""

YAML_DOC_4 = """
device_classes:
  /Device:
    templates:
      BasicComponent:
        datasources:
          A:
            type: SNMP
            severity: 5
            datapoints:
              A: {}
            oid: .1.3.6.1.4.1.232.6.2.6.8.1.4
        thresholds:
          a:
            type: MinMaxThreshold
            dsnames: [A_A]
        graphs:
          Basic Component:
            graphpoints:
              A:
                dpName: A_A
                includeThresholds: true
      SubComponent:
        datasources:
          A:
            type: SNMP
            severity: 5
            datapoints:
              A: {}
            oid: .1.3.6.1.4.1.232.6.2.6.8.1.4
        thresholds:
          a:
            type: MinMaxThreshold
            dsnames: [A_A]
        graphs:
          Sub Component:
            graphpoints:
              A:
                dpName: A_A
                includeThresholds: true
      AuxComponent:
        datasources:
          A:
            type: SNMP
            severity: 5
            datapoints:
              A: {}
            oid: .1.3.6.1.4.1.232.6.2.6.8.1.4
        thresholds:
          a:
            type: MinMaxThreshold
            dsnames: [A_A]
        graphs:
          Aux Component:
            graphpoints:
              A:
                dpName: A_A
                includeThresholds: true
"""

YAML_DOC_5 = """
class_relationships:
- SubComponent M:M AuxComponent
"""

YAML_DOC_6 = """
zProperties:
  zBasicNumeric:
    default: 0
"""

class TestMultiYAML(BaseTestCase):
    """Test removal of undefined relations"""

    def test_multi_yaml(self):
        ''''''

        # reference yaml (all in one
        cfg_whole = zenpacklib.load_yaml(YAML_DOC)

        # reference yaml split across multiple files
        cfg_multi = zenpacklib.load_yaml([YAML_DOC_1, YAML_DOC_2, YAML_DOC_3, YAML_DOC_4, YAML_DOC_5, YAML_DOC_6])

        # dump both back to YAML
        whole_yaml = yaml.dump(cfg_whole.specparams, Dumper=Dumper)
        multi_yaml = yaml.dump(cfg_multi.specparams, Dumper=Dumper)

        compare_equals = compare_zenpackspecs(whole_yaml, multi_yaml)

        diff = ZenPack.get_yaml_diff(whole_yaml, multi_yaml)
        self.assertTrue(compare_equals,
                        'YAML merged dictionary test failed:\n{}'.format(diff))


def test_suite():
    """Return test suite for this module."""
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestMultiYAML))
    return suite

if __name__ == "__main__":
    from zope.testrunner.runner import Runner
    runner = Runner(found_suites=[test_suite()])
    runner.run()
