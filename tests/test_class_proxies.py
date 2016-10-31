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
site.addsitedir(os.path.join(os.path.dirname(__file__), '..'))
import zenpacklib


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


def add_contained(rel, obj):
    rel._setObject(obj.id, obj)
    p = rel._getOb(obj.id)
    p.index_object()
    notify(IndexingEvent(p))
    return p


class TestClassProxies(BaseTestCase):
    """Class proxy tests."""

    def afterSetUp(self):
        super(TestClassProxies, self).afterSetUp()

        with tempfile.NamedTemporaryFile() as f:
            f.write(YAML.strip())
            f.flush()
            try:
                zenpacklib.load_yaml(f.name)
            except Exception:
                self.fail(traceback.format_exc(limit=0))

    def test_class_proxies(self):
        dc = self.dmd.Devices.createOrganizer("/Test")
        dc.setZenProperty("zPythonClass", "ZenPacks.test.ClassProxies.MyDevice")
        device = dc.createInstance("test-device")
        device.setPerformanceMonitor("localhost")
        device.setManageIp("127.1.2.3")
        device.index_object()
        notify(IndexingEvent(device))

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

        adm = ApplyDataMap()._applyDataMap
        [adm(device, datamap) for datamap in datamaps]

        # ZEN-4087: Workaround issue where first indexed component may
        # not be properly indexed.
        device.componentSearch()[0].getObject().index_object()

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
