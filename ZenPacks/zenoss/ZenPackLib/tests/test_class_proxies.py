#!/usr/bin/env python

##############################################################################
#
# Copyright (C) Zenoss, Inc. 2016, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

"""Class proxy tests."""

# stdlib Imports
import os
import site
import tempfile
import traceback

# Zope Imports
from zope.event import notify

# Zenoss Imports
import Globals  # noqa

from Products.DataCollector.ApplyDataMap import ApplyDataMap
from Products.DataCollector.plugins.DataMaps import ObjectMap, RelationshipMap
from Products.ZenTestCase.BaseTestCase import BaseTestCase
from Products.Zuul.interfaces import ICatalogTool
from Products.Zuul.catalog.events import IndexingEvent

# zenpacklib Imports
from ZenPacks.zenoss.ZenPackLib import zenpacklib


YAML = """
name: ZenPacks.test.ClassProxies

class_relationships:
  - MyDevice 1:MC MyComponent
  - MyDevice 1:MC MyHardwareComponent
  - MyDevice 1:MC MyHWComponent
  - MyDevice 1:MC MyOSComponent
  - MyDevice 1:MC MyService

classes:
  MyDevice:
    base: [zenpacklib.Device]

  MyComponent:
    base: [zenpacklib.Component]
    properties:
      idx_device:
        index_type: field

      idx_global:
        index_type: field
        index_scope: global

  MyComponentSub1:
    base: [MyComponent]
    properties:
      idx_device_sub1:
        index_type: field

      idx_global_sub1:
        index_type: field
        index_scope: global

  MyComponentSub2:
    base: [MyComponent]
    properties:
      idx_device_sub2:
        index_type: field

      idx_global_sub2:
        index_type: field
        index_scope: global

  MyCPU:
    base: [zenpacklib.CPU]

  MyDevice:
    base: [zenpacklib.Device]

  MyExpansionCard:
    base: [zenpacklib.ExpansionCard]

  MyFan:
    base: [zenpacklib.Fan]

  MyFileSystem:
    base: [zenpacklib.FileSystem]

  MyHardDisk:
    base: [zenpacklib.HardDisk]

  MyHardwareComponent:
    base: [zenpacklib.HardwareComponent]

  MyHWComponent:
    base: [zenpacklib.HWComponent]

  MyIpInterface:
    base: [zenpacklib.IpInterface]

  MyIpRouteEntry:
    base: [zenpacklib.IpRouteEntry]

  MyIpService:
    base: [zenpacklib.IpService]

  MyOSComponent:
    base: [zenpacklib.OSComponent]

  MyOSProcess:
    base: [zenpacklib.OSProcess]

  MyPowerSupply:
    base: [zenpacklib.PowerSupply]

  MyService:
    base: [zenpacklib.Service]

  MyTemperatureSensor:
    base: [zenpacklib.TemperatureSensor]

  MyWinService:
    base: [zenpacklib.WinService]
"""

def create_device(dmd, zPythonClass, device_id, datamaps):
    deviceclass = dmd.Devices.createOrganizer("/Test")
    deviceclass.setZenProperty("zPythonClass", zPythonClass)
    device = deviceclass.createInstance(device_id)
    device.setPerformanceMonitor("localhost")
    device.setManageIp("127.1.2.3")
    device.index_object()
    notify(IndexingEvent(device))

    adm = ApplyDataMap()._applyDataMap

    [adm(device, datamap) for datamap in datamaps]

    for component in device.getDeviceComponentsNoIndexGen():
        component.index_object()
        notify(IndexingEvent(component))

    return device


class TestClassProxies(BaseTestCase):
    """Class proxy tests."""

    def afterSetUp(self):
        super(TestClassProxies, self).afterSetUp()
        try:
            zenpacklib.load_yaml(YAML)
        except Exception:
            self.fail(traceback.format_exc(limit=0))

    def test_standard_catalogs(self):
        datamaps = [
            RelationshipMap(
                modname="ZenPacks.test.ClassProxies.MyComponent",
                relname="myComponents",
                objmaps=[ObjectMap({"id": "myComponent-1"})]),

            RelationshipMap(
                modname="ZenPacks.test.ClassProxies.MyCPU",
                compname="hw",
                relname="cpus",
                objmaps=[ObjectMap({"id": "myCPU-1"})]),

            RelationshipMap(
                modname="ZenPacks.test.ClassProxies.MyExpansionCard",
                compname="hw",
                relname="cards",
                objmaps=[ObjectMap({"id": "myExpansionCard-1"})]),

            RelationshipMap(
                modname="ZenPacks.test.ClassProxies.MyFan",
                compname="hw",
                relname="fans",
                objmaps=[ObjectMap({"id": "myFan-1"})]),

            RelationshipMap(
                modname="ZenPacks.test.ClassProxies.MyFileSystem",
                compname="os",
                relname="filesystems",
                objmaps=[ObjectMap({"id": "myFileSystem-1"})]),

            RelationshipMap(
                modname="ZenPacks.test.ClassProxies.MyHardDisk",
                compname="hw",
                relname="harddisks",
                objmaps=[ObjectMap({"id": "myHardDisk-1"})]),

            RelationshipMap(
                modname="ZenPacks.test.ClassProxies.MyHardwareComponent",
                relname="myHardwareComponents",
                objmaps=[ObjectMap({"id": "myHardwareComponent-1"})]),

            RelationshipMap(
                modname="ZenPacks.test.ClassProxies.MyHWComponent",
                relname="myHWComponents",
                objmaps=[ObjectMap({"id": "myHWComponent-1"})]),

            RelationshipMap(
                modname="ZenPacks.test.ClassProxies.MyIpInterface",
                compname="os",
                relname="interfaces",
                objmaps=[ObjectMap({"id": "myIpInterface-1"})]),

            RelationshipMap(
                modname="ZenPacks.test.ClassProxies.MyIpRouteEntry",
                compname="os",
                relname="routes",
                objmaps=[ObjectMap({"id": "myIpRouteEntry-1"})]),

            RelationshipMap(
                modname="ZenPacks.test.ClassProxies.MyIpService",
                compname="os",
                relname="ipservices",
                objmaps=[ObjectMap({"id": "myIpService-1"})]),

            RelationshipMap(
                modname="ZenPacks.test.ClassProxies.MyOSComponent",
                relname="myOSComponents",
                objmaps=[ObjectMap({"id": "myOSComponent-1"})]),

            RelationshipMap(
                modname="ZenPacks.test.ClassProxies.MyOSProcess",
                compname="os",
                relname="processes",
                objmaps=[ObjectMap({"id": "myOSProcess-1"})]),

            RelationshipMap(
                modname="ZenPacks.test.ClassProxies.MyPowerSupply",
                compname="hw",
                relname="powersupplies",
                objmaps=[ObjectMap({"id": "myPowerSupply-1"})]),

            RelationshipMap(
                modname="ZenPacks.test.ClassProxies.MyService",
                relname="myServices",
                objmaps=[ObjectMap({"id": "myService-1"})]),

            RelationshipMap(
                modname="ZenPacks.test.ClassProxies.MyTemperatureSensor",
                compname="hw",
                relname="temperaturesensors",
                objmaps=[ObjectMap({"id": "myTemperatureSensor-1"})]),

            RelationshipMap(
                modname="ZenPacks.test.ClassProxies.MyWinService",
                compname="os",
                relname="winservices",
                objmaps=[ObjectMap({"id": "myWinService-1"})]),
            ]

        device = create_device(
            self.dmd,
            zPythonClass="ZenPacks.test.ClassProxies.MyDevice",
            device_id="test-device",
            datamaps=datamaps)

        all_classnames = {
            'MyDevice',
            'MyComponent',
            'MyCPU',
            'MyDevice',
            'MyExpansionCard',
            'MyFan',
            'MyFileSystem',
            'MyHardDisk',
            'MyHardwareComponent',
            'MyHWComponent',
            'MyIpInterface',
            'MyIpRouteEntry',
            'MyIpService',
            'MyOSComponent',
            'MyOSProcess',
            'MyPowerSupply',
            'MyService',
            'MyTemperatureSensor',
            'MyWinService',
            }

        # global_catalog: Should be one instance of each class.
        global_catalog = ICatalogTool(device)
        fq_classnames = {
            "ZenPacks.test.ClassProxies.{0}.{0}".format(x)
            for x in all_classnames}

        for fq_classname in fq_classnames:
            results = global_catalog.search(types=[fq_classname])
            self.assertTrue(
                results.total == 1,
                "{} not found in global catalog".format(fq_classname))

        # componentSearch: Should be one instance of each component class.
        meta_types = all_classnames - {"MyDevice"}
        for meta_type in meta_types:
            results = device.componentSearch(meta_type=meta_type)
            self.assertTrue(
                len(results) == 1,
                "{} not found in componentSearch catalog".format(meta_type))

        # ComponentBaseSearch: Should be one instance of each component class.
        ids = {
            "{}{}-1".format(x[:1].lower(), x[1:])
            for x in all_classnames - {"MyDevice"}}

        for id_ in ids:
            results = device.ComponentBaseSearch(id=id_)
            self.assertTrue(
                len(results) == 1,
                "{} not found in ComponentBaseSearch catalog".format(id_))

    def test_subclass_catalogs(self):
        rm = RelationshipMap(
            modname="ZenPacks.test.ClassProxies.MyComponent",
            relname="myComponents")

        rm.extend([
            ObjectMap(
                modname="ZenPacks.test.ClassProxies.MyComponent",
                data={
                    "id": "myComponent-1",
                    "idx_device": "myComponent-1",
                    "idx_global": "myComponent-1"}),

            ObjectMap(
                modname="ZenPacks.test.ClassProxies.MyComponent",
                data={
                    "id": "myComponent-2",
                    "idx_device": "myComponent-2",
                    "idx_global": "myComponent-2"}),

            ObjectMap(
                modname="ZenPacks.test.ClassProxies.MyComponentSub1",
                data={
                    "id": "myComponent1-1",
                    "idx_device": "myComponent1-1",
                    "idx_global": "myComponent1-1",
                    "idx_device_sub1": "myComponent1-1",
                    "idx_global_sub1": "myComponent1-1"}),

            ObjectMap(
                modname="ZenPacks.test.ClassProxies.MyComponentSub1",
                data={
                    "id": "myComponent1-2",
                    "idx_device": "myComponent1-2",
                    "idx_global": "myComponent1-2",
                    "idx_device_sub1": "myComponent1-2",
                    "idx_global_sub1": "myComponent1-2"}),

            ObjectMap(
                modname="ZenPacks.test.ClassProxies.MyComponentSub2",
                data={
                    "id": "myComponent2-1",
                    "idx_device": "myComponent2-1",
                    "idx_global": "myComponent2-1",
                    "idx_device_sub2": "myComponent2-1",
                    "idx_global_sub2": "myComponent2-1"}),

            ObjectMap(
                modname="ZenPacks.test.ClassProxies.MyComponentSub2",
                data={
                    "id": "myComponent2-2",
                    "idx_device": "myComponent2-2",
                    "idx_global": "myComponent2-2",
                    "idx_device_sub2": "myComponent2-2",
                    "idx_global_sub2": "myComponent2-2"})])

        # Describe what all of the catalogs should look like.
        component_ids = [
            "myComponent-1", "myComponent1-1", "myComponent2-1",
            "myComponent-2", "myComponent1-2", "myComponent2-2",
            ]

        device_expected = {
            "MyComponent": {"idx_device": component_ids},
            "MyComponentSub1": {"idx_device_sub1": ["myComponent1-1", "myComponent1-2"]},
            "MyComponentSub2": {"idx_device_sub2": ["myComponent2-1", "myComponent2-2"]}}

        from ZenPacks.test.ClassProxies.MyComponent import MyComponent
        from ZenPacks.test.ClassProxies.MyComponentSub1 import MyComponentSub1
        from ZenPacks.test.ClassProxies.MyComponentSub2 import MyComponentSub2

        global_expected = {
            MyComponent: {"idx_global": component_ids * 2},
            MyComponentSub1: {"idx_global_sub1": ["myComponent1-1", "myComponent1-2"] * 2},
            MyComponentSub2: {"idx_global_sub2": ["myComponent2-1", "myComponent2-2"] * 2}}

        def verify_all_catalogs():
            for device in devices:
                for catalog_name, indexes in device_expected.items():
                    for index_name, expected_values in indexes.items():
                        self.assertItemsEqual(
                            expected_values,
                            [getattr(x, index_name) for x in device.search(catalog_name)])

            for class_, indexes in global_expected.items():
                for index_name, expected_values in indexes.items():
                    self.assertItemsEqual(
                        expected_values,
                        [getattr(x, index_name) for x in class_.class_search(self.dmd)])

        # Create devices and components
        devices = [
            create_device(
                self.dmd,
                zPythonClass="ZenPacks.test.ClassProxies.MyDevice",
                device_id="test-device{}".format(x),
                datamaps=[rm])
            for x in (1, 2)]

        # Verify that all catalogs are correct after initial modeling.
        verify_all_catalogs()

        # Delete catalogs.
        self.dmd.Devices._delObject("ZenPacks_test_ClassProxies_MyComponentSearch")
        self.dmd.Devices._delObject("ZenPacks_test_ClassProxies_MyComponentSub1Search")
        self.dmd.Devices._delObject("ZenPacks_test_ClassProxies_MyComponentSub2Search")

        for device in devices:
            device._delObject("ComponentBaseSearch")
            device._delObject("MyComponentSearch")
            device._delObject("MyComponentSub1Search")
            device._delObject("MyComponentSub2Search")

        # Index single component of one of the subclasses.
        devices[0].myComponents._getOb("myComponent1-1").index_object()

        # All components of superclasseses should now be indexed in
        # device and global catalogs.
        self.assertItemsEqual(
            component_ids,
            [x.id for x in devices[0].search("MyComponent")])

        self.assertItemsEqual(
            component_ids * 2,
            [x.id for x in MyComponent.class_search(self.dmd)])

        # All components of the same class should be indexed in device
        # and global catalogs.
        self.assertItemsEqual(
            ["myComponent1-1", "myComponent1-2"],
            [x.id for x in devices[0].search("MyComponentSub1")])

        self.assertItemsEqual(
            ["myComponent1-1", "myComponent1-2"] * 2,
            [x.id for x in MyComponentSub1.class_search(self.dmd)])

        # All components of classes not in the inheritence hierarchy
        # should not yet be indexed in device or global catalogs.
        self.assertItemsEqual(
            [],
            [x.id for x in devices[0].search("MyComponentSub2")])

        self.assertItemsEqual(
            [],
            [x.id for x in MyComponentSub2.class_search(self.dmd)])

        # Index remaining unique device/subclass combinations.
        devices[0].myComponents._getOb("myComponent2-1").index_object()
        devices[1].myComponents._getOb("myComponent1-1").index_object()
        devices[1].myComponents._getOb("myComponent2-1").index_object()

        # Now all catalogs should be complete.
        verify_all_catalogs()

    def test_ipinterface_indexing(self):
        datamaps = RelationshipMap(
            modname="ZenPacks.test.ClassProxies.MyIpInterface",
            compname="os",
            relname="interfaces",
            objmaps=[
                ObjectMap({"id": "eth0", "macaddress": "01:23:45:67:89:ab"}),
                ObjectMap({"id": "eth1", "macaddress": "01:23:45:67:89:ac"})])

        device = create_device(
            self.dmd,
            zPythonClass="ZenPacks.test.ClassProxies.MyDevice",
            device_id="test-device",
            datamaps=[datamaps])

        self.assertItemsEqual(
            ["01:23:45:67:89:ab", "01:23:45:67:89:ac"],
            device.getMacAddresses())


def test_suite():
    """Return test suite for this module."""
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestClassProxies))
    return suite

if __name__ == "__main__":
    from zope.testrunner.runner import Runner
    runner = Runner(found_suites=[test_suite()])
    runner.run()
