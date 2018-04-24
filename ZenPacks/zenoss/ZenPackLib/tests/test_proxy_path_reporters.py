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
    Ensure that path reporters work correctly for ZPL proxy classes
"""
from ZenPacks.zenoss.ZenPackLib.tests import ZPLBaseTestCase
from ZenPacks.zenoss.ZenPackLib.lib.base.ComponentBase import ComponentBase

YAML_DOC = '''
name: ZenPacks.zenoss.TestPathReporters
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
    base: [zenpacklib.IpService]

class_relationships:
  - MyDev 1:MC SubClass1
  - MyDev 1:MC SubClass2
  - MyDev 1:MC SubClass3
  - MyDev 1:MC SubClass4
  - SubClass1 M:M SubClass2 # works
  - SubClass2 M:M SubClass3 # works
  - SubClass2 M:M SubClass4 # broken
'''


class TestPathReporters(ZPLBaseTestCase):
    """
    Ensure that path reporters work correctly for ZPL proxy classes
    """

    yaml_doc = YAML_DOC
    build = True

    def afterSetUp(self):
        super(TestPathReporters, self).afterSetUp()
        self.location = self.dmd.Locations.createOrganizer('SomePlace')
        self.service = self.dmd.Services.createServiceClass('test')
        self.config = self.configs.get('ZenPacks.zenoss.TestPathReporters')
        self.cfg = self.config.get('cfg')
        self.objects = self.config.get('objects').class_objects

    def test_path_reporters(self):
        """Test that path reporters return paths from 
            both ZPL and proxied platform classes
        """
        from ZenPacks.zenoss.ZenPackLib.lib.gsm import GSM
        from Products.Zuul.catalog.interfaces import IPathReporter
        from ZenPacks.zenoss.ZenPackLib.lib.wrapper.ComponentPathReporter import ComponentPathReporter

        target_path = ('mydev-0', 'subClass2s', 'subclass2-0')
        service_path = ('', 'zport', 'dmd', 'Services', 'serviceclasses', 'test', 'instances', 'subclass4-0')
        location_path = ('', 'zport', 'dmd', 'Locations', 'SomePlace', 'devices', 'mydev-0')

        for cls_name, cls_data in self.objects.iteritems():
            ob = cls_data.get('ob')

            if cls_name not in ['MyDev', 'SubClass3', 'SubClass4']:
                continue

            if cls_name == 'MyDev':
                ob.location._add(self.location)

            if cls_name == 'SubClass4':
                ob.serviceclass._add(self.service)

            spec = self.cfg.classes.get(cls_name)
            # registering ourself but ZPL would normally do this implicitly for basic classes
            GSM.registerAdapter(ComponentPathReporter, (ComponentBase,), IPathReporter)

            # also calling the register_path_adapters method here
            spec.register_path_adapters()

            rpt = IPathReporter(ob)
            paths = rpt.getPaths()

            if cls_name in ['SubClass3', 'SubClass4']:
                # test that the product mixin class reports paths correctly
                if cls_name == 'SubClass4':
                    self.assertTrue(service_path in paths,
                                'Path reporter testing failed for {} ({})'.format(
                                                        ob.__class__.__name__,
                                                        paths))
                # test that the ZPL paths also get reported correctly
                self.assertTrue(target_path in paths,
                                'Path reporter testing failed for {} ({})'.format(
                                                            ob.__class__.__name__,
                                                            paths))
            # test Device class paths
            if cls_name == 'MyDev':
                self.assertTrue(location_path in paths,
                                'Path reporter testing failed for {} ({})'.format(
                                                            ob.__class__.__name__,
                                                            paths))


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
