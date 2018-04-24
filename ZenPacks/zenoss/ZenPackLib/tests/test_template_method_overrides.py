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
    getRRDTemplateName can return label of base class if label is not set in a subclass
    (ZPS-100)
"""
from ZenPacks.zenoss.ZenPackLib.tests import ZPLBaseTestCase


YAML_DOC = '''name: ZenPacks.zenoss.PS.Viptela
class_relationships:
  - ViptelaDevice 1:MC Tunnel
  - ViptelaDevice 1:MC ControlConnection
  - ViptelaDevice 1:MC Interface
classes:
  ViptelaDevice:
    base: [zenpacklib.Device]
  ViptelaComponent:
    base: [zenpacklib.Component]
  VManage:
    base: [ViptelaDevice]
    label: vManage
  VSmart:
    base: [ViptelaDevice]
    label: vSmart
  VEdge:
    base: [ViptelaDevice]
    label: vEdge
  Interface:
    base: [ViptelaComponent]
  Tunnel:
    base: [ViptelaComponent]
  ControlConnection:
    base: [ViptelaComponent]
'''


class TestTemplateMethodOverrides(ZPLBaseTestCase):
    """
    Ensure getRRDTemplateName returns the expected output
    """

    yaml_doc = YAML_DOC
    build = True

    def test_getrrdtemplatename_override(self):
        config = self.configs.get('ZenPacks.zenoss.PS.Viptela')
        cfg = config.get('cfg')
        objects = config.get('objects').class_objects
        
        for spec in cfg.classes.values():
            if spec.is_device:
                continue
            ob = objects.get(spec.name,{}).get('ob')
            rrd_name = ob.getRRDTemplateName()
            self.assertEquals(spec.label, rrd_name,
                              'getRRDTemplateName expected "{}", got "{}"'.format(spec.label, rrd_name))


def test_suite():
    """Return test suite for this module."""
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestTemplateMethodOverrides))
    return suite

if __name__ == "__main__":
    from zope.testrunner.runner import Runner
    runner = Runner(found_suites=[test_suite()])
    runner.run()
