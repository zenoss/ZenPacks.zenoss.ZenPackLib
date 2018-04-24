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
    Test fix for ZEN-24108
    Device relations between ZPL-based ZenPacks overwrite inherited Device relations
"""

from ZenPacks.zenoss.ZenPackLib.tests import ZPLBaseTestCase

RELATION_YAML = """
name: ZenPacks.zenoss.PatchedRelations
classes:
  BasicDeviceComponent:
    base: [zenpacklib.Component]
    properties:
      something:
        label: Something
  SubClassComponent:
    base: [zenpacklib.Component]

class_relationships:
  - Products.ZenModel.Device.Device 1:MC BasicDeviceComponent
  - ZenPacks.zenoss.ZPLDevice.NormDevice.NormDevice 1:MC SubClassComponent
"""

SUBCLASS_YAML = """
name: ZenPacks.zenoss.ZPLDevice
classes:
  BaseDevice:
    base: [zenpacklib.Device]
  NormDevice:
    base: [BaseDevice]
  ClusterDevice:
    base: [NormDevice]
"""


class TestImportedRelations(ZPLBaseTestCase):
    """Test fix for ZEN-24108

       Device relations between ZPL-based ZenPacks overwrite inherited Device relations
    """
    yaml_doc = [SUBCLASS_YAML, RELATION_YAML]
    build = True

    def test_inherited_relations(self):
        from Products.ZenModel.Device import Device as ZenDevice
        config_sub = self.configs.get('ZenPacks.zenoss.ZPLDevice')
        sub_objects = config_sub.get('objects').class_objects

        # all ZenModel.Device subclasses should have this relation
        for x in [ZenDevice]:
            # should be True
            self.assertTrue(self.has_relation(x, 'basicDeviceComponents'),
                            '%s is missing relation: basicDeviceComponents' % x.__name__)
            self.assertFalse(self.has_relation(x, 'subClassComponents'),
                            '%s has unneeded relation: subClassComponents' % x.__name__)

        # all ZenModel.Device subclasses should have this relation
        for x in ['BaseDevice', 'NormDevice', 'ClusterDevice']:
            cls = sub_objects.get(x).get('cls')
            # should be True
            self.assertTrue(self.has_relation(cls, 'basicDeviceComponents'),
                            '%s is missing relation: basicDeviceComponents' % cls.__name__)

        # these should have subClassComponents
        for x in ['NormDevice', 'ClusterDevice']:
            cls = sub_objects.get(x).get('cls')
            self.assertTrue(self.has_relation(cls, 'subClassComponents'),
                            '%s is missing relation: subClassComponents' % cls.__name__)

        # these should not have subClassComponents
        for x in ['BaseDevice']:
            cls = sub_objects.get(x).get('cls')
            self.assertFalse(self.has_relation(cls, 'subClassComponents'),
                            '%s has unneeded relation: subClassComponents' % cls.__name__)

    def has_relation(self, cls, relname):
        if relname in dict(cls._relations).keys():
            return True
        return False


def test_suite():
    """Return test suite for this module."""
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestImportedRelations))
    return suite


if __name__ == "__main__":
    from zope.testrunner.runner import Runner
    runner = Runner(found_suites=[test_suite()])
    runner.run()
