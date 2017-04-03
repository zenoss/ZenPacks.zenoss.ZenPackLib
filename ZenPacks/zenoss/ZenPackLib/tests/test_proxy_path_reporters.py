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
    Ensure that path reporters work correctly for ZPL proxy classes
"""

from ZenPacks.zenoss.ZenPackLib.tests.ZPLTestBase import ZPLTestBase


YAML_DOC = '''
name: ZenPacks.zenoss.ZenPackLib
classes:
  MyDev:
    base: [zenpacklib.Device]
  BaseClass1:
    base: [zenpacklib.Component]
  BaseClass2:
    base: [zenpacklib.Component]
  SubClass1:
    base: [BaseClass1]
  SubClass2:
    base: [BaseClass1]
  SubClass3:
    base: [BaseClass2]
  SubClass4:
    base: [zenpacklib.HWComponent]
    
class_relationships:
  - MyDev 1:MC SubClass1
  - MyDev 1:MC SubClass2
  - MyDev 1:MC SubClass3
  - MyDev 1:MC SubClass4
  - SubClass1 M:M SubClass2 # works
  - SubClass2 M:M SubClass3 # works
  - SubClass2 M:M SubClass4 # broken
'''


class TestPathReporters(ZPLTestBase):
    """
    Ensure that path reporters work correctly for ZPL proxy classes
    """

    yaml_doc = YAML_DOC

    def test_path_reporters(self):
        ''''''
        target_path = ('mydev-0', 'subClass2s', 'subclass2-0')

        # registering ourself but ZPL would normally do this implicitly for basic classes
        from ZenPacks.zenoss.ZenPackLib.lib.gsm import GSM
        from Products.Zuul.catalog.interfaces import IPathReporter
        from ZenPacks.zenoss.ZenPackLib.lib.wrapper.ComponentPathReporter import ComponentPathReporter
        spec = self.z.cfg.classes.get('SubClass3')
        GSM.registerAdapter(ComponentPathReporter, (spec.model_class,), IPathReporter)

        for ob in self.z.obs:
            if ob.__class__.__name__ not in ['SubClass3', 'SubClass4']:
                continue
            rpt = IPathReporter(ob)
            self.assertTrue(target_path in rpt.getPaths(),
                            'Path reporter testing failed for {} ({})'.format(ob.__class__.__name__, rpt.getPaths()))


def test_suite():
    """Return test suite for this module."""
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestPathReporters))
    return suite

if __name__ == "__main__":
    from zope.testrunner.runner import Runner
    runner = Runner(found_suites=[test_suite()])
    runner.run()
