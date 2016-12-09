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
    getRRDTemplateName can return label of base class if label is not set in a subclass
    (ZPS-100)
"""
# Zenoss Imports
import Globals  # noqa
from Products.ZenUtils.Utils import unused
unused(Globals)


# stdlib Imports
from Products.ZenTestCase.BaseTestCase import BaseTestCase

# zenpacklib Imports
from ZenPacks.zenoss.ZenPackLib.tests.ZPLTestHarness import ZPLTestHarness


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


class TestTemplateMethodOverrides(BaseTestCase):
    """
    Ensure getRRDTemplateName returns the expected output
    """

    def test_zProperties(self):
        z = ZPLTestHarness(YAML_DOC)
        for spec in z.cfg.classes.values():
            if spec.is_device:
                continue
            ob = spec.model_class('test')
            self.assertEquals(spec.label, ob.getRRDTemplateName(),
                              'getRRDTemplateName expected "{}", got "{}"'.format(spec.label, ob.getRRDTemplateName()))

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
