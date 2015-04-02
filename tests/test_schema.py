#!/usr/bin/env python

##############################################################################
#
# Copyright (C) Zenoss, Inc. 2013-2015, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

"""Schema unit tests.

This is primarily testing that zenpacklib is functioning as desired. If
zenpacklib was already mature these kinds of tests would be in its
test suite instead of in the ZenPack's.

"""

import Globals
from Products.ZenModel.Device import Device
from Products.ZenModel.DeviceComponent import DeviceComponent
from Products.ZenModel.ManagedEntity import ManagedEntity
from Products.ZenRelations.ToManyRelationship import ToManyRelationship
from Products.ZenRelations.ToManyContRelationship import ToManyContRelationship
from Products.ZenRelations.ToOneRelationship import ToOneRelationship
from Products.ZenRelations.zPropertyCategory import getzPropertyCategory
from Products.Zuul.interfaces import IInfo
from Products.ZenUtils.Utils import unused

unused(Globals)

import os
import site
import logging
logging.basicConfig(level=logging.INFO)


site.addsitedir(os.path.join(os.path.dirname(__file__), '..'))

from ZenPacks.zenoss.ZPLTest1 import zenpacklib
from ZenPacks.zenoss.ZPLTest1 import schema
from ZenPacks.zenoss.ZPLTest1.ManagedObject import ManagedObject

# Required before zenpacklib.TestCase can be used.
zenpacklib.enableTesting()


class TestSchema(zenpacklib.TestCase):

    """Test suite for ZenPack's schema.

    Not all schema classes are tested. The idea is to test at least one
    example of each zenpacklib functionality used.

    """

    zenpack_module_name = 'ZenPacks.zenoss.ZPLTest1'
    zenpack_path = os.path.join(os.path.dirname(__file__),
                                "data/zenpacks/ZenPacks.zenoss.ZPLTest1")
    disableLogging = False

    def afterSetUp(self):
        try:
            super(TestSchema, self).afterSetUp()
        except ImportError, e:
            self.assertFalse(
                e.message == 'No module named ZPLTest1',
                "ZPLTest1 zenpack is not installed.  You must install it before running this test:\n   zenpack --link --install=%s" % self.zenpack_path
            )

    def assert_superclasses(self, obj, expected_superclasses):
        """Assert that obj is a subclass of all expected_superclasses."""
        for expected_superclass in expected_superclasses:
            self.assertTrue(
                isinstance(obj, expected_superclass),
                "{obj.id!r} is not instance of {expected_superclass!r}"
                .format(
                    obj=obj,
                    expected_superclass=expected_superclass))

    def assert_properties(self, obj, expected_properties):
        """Assert that obj has all expected_properties."""
        for expected_property in expected_properties:
            self.assertTrue(
                hasattr(obj, expected_property),
                "{obj.id!r} has no {expected_property!r} class property"
                .format(
                    obj=obj,
                    expected_property=expected_property))

            self.assertTrue(
                expected_property in obj.propertyIds(),
                "{obj.id!r} has no {expected_property!r} OFS property"
                .format(
                    obj=obj,
                    expected_property=expected_property))

    def assert_relationships(self, obj, expected_relationships):
        """Assert that obj has all expected_relationships."""
        for expected_relname, expected_reltype in expected_relationships:
            relationship = getattr(obj, expected_relname, None)

            self.assertTrue(
                relationship,
                "{obj.id!r} has no {expected_relname!r} relationship"
                .format(
                    obj=obj,
                    expected_relname=expected_relname))

            self.assertTrue(
                isinstance(relationship, expected_reltype),
                "{obj.id!r} {expected_relname!r} not instance of {expected_reltype!r}"
                .format(
                    obj=obj,
                    expected_relname=expected_relname,
                    expected_reltype=expected_reltype))

    def test_schemaclass(self):
        """Assert that a dynamic schema class was created properly."""
        self.assertTrue(
            'zenpacklib' not in schema.APIC.__module__,
            "{schema.APIC.__module__!r} contains 'zenpacklib'"
            .format(schema=schema))

    def test_stubclass(self):
        """Assert that a dynamic stub class was created properly."""
        from ZenPacks.zenoss.ZPLTest1.APIC import APIC

        self.assertTrue(
            'zenpacklib' not in APIC.__module__,
            "{APIC.__module__!r} contains 'zenpacklib'"
            .format(APIC=APIC))

    def test_ZenPack(self):
        """Assert that ZenPack class has been properly created."""
        from ZenPacks.zenoss.ZPLTest1 import ZenPack

        zenpack = ZenPack('ZenPacks.zenoss.ZPLTest1')

        self.assert_superclasses(zenpack, (
            ZenPack,
            schema.ZenPack,
            ))

        expected_zpropnames = {
            'zZPLTest1Port',
            'zZPLTest1Username',
            'zZPLTest1Password',
            }

        zpropnames = {x[0] for x in zenpack.packZProperties}

        self.assertTrue(
            expected_zpropnames.issubset(zpropnames),
            "missing zProperties: {difference!r}"
            .format(
                difference=expected_zpropnames.difference(zpropnames)))

        expected_zproperties = {
            'zZPLTest1Port': (443, 'int'),
            'zZPLTest1SSL': (True, 'boolean'),
            'zZPLTest1Username': ('admin', 'string'),
            'zZPLTest1Password': ('', 'password'),
            'zZPLTest1HealthInterval': (300, 'int'),
            }

        for zpropname, zpdefault, zptype in zenpack.packZProperties:
            self.assertEquals(
                getzPropertyCategory(zpropname), 'ZPLTest1',
                "{zpropname!r} isn't categorized as 'ZPLTest1'"
                .format(
                    zpropname=zpropname))

            expected_zpdefault, expected_zptype = expected_zproperties[zpropname]

            self.assertEquals(
                zpdefault, expected_zpdefault,
                "{zpropname!r} has default of {zpdefault!r} instead of {expected_zpdefault!r}"
                .format(
                    zpropname=zpropname,
                    zpdefault=zpdefault,
                    expected_zpdefault=expected_zpdefault))

            self.assertEquals(
                zptype, expected_zptype,
                "{zpropname!r} has type of {zptype!r} instead of {expected_zptype!r}"
                .format(
                    zpropname=zpropname,
                    zptype=zptype,
                    expected_zptype=expected_zptype))

    def test_APIC(self):
        """Assert that APIC class has been properly created.

        Tests an example of creating a Device type with a stub
        implementation.

        """
        from ZenPacks.zenoss.ZPLTest1.APIC import APIC

        apic1 = APIC('apic1')

        self.assertEquals(apic1.meta_type, 'ZPLTest1')

        self.assert_superclasses(apic1, (
            Device,
            zenpacklib.Device,
            schema.APIC,
            ))

        self.assert_properties(apic1, ('manageIp', 'priority'))

        self.assert_relationships(apic1, (
            ('dependencies', ToManyRelationship),  # from ManagedEntity
            ('deviceClass', ToOneRelationship),  # from Device
            ('fabricPods', ToManyContRelationship),
            ('fvTenants', ToManyContRelationship),
            ))

    def test_Info(self):
        """Assert that API Info are functioning."""
        from Products.Zuul.infos.component import ComponentInfo
        from Products.Zuul.infos.device import DeviceInfo

        from ZenPacks.zenoss.ZPLTest1.APIC import APIC, APICInfo
        from ZenPacks.zenoss.ZPLTest1.FabricNode import FabricNode, FabricNodeInfo

        apic1 = APIC('apic1')
        apic1_info = IInfo(apic1)

        self.assert_superclasses(apic1_info, (
            DeviceInfo,
            APICInfo,
            ))

        node1 = FabricNode('node1')
        node1.role = 'controller'
        node1_info = IInfo(node1)

        self.assert_superclasses(node1_info, (
            ComponentInfo,
            FabricNodeInfo,
            ))

        self.assertTrue(
            hasattr(node1_info, 'role'),
            "{info!r} has no {attribute!r} attribute"
            .format(
                info=node1_info,
                attribute='role'))

        self.assertTrue(
            node1_info.role == 'controller',
            "{info!r}.{attribute!r} != {value!r}"
            .format(
                info=node1_info,
                attribute='role',
                value='controller'))

    def test_registerNames(self):
        """Assert that JavaScript registerNames is registered."""
        import zope.component
        import zope.interface

        from zope.publisher.browser import BrowserView, TestRequest

        from Products.ZenUI3.browser.interfaces import IMainSnippetManager

        request = TestRequest()
        view = BrowserView(self.dmd, request)

        manager_name = 'jssnippets'

        manager = zope.component.queryMultiAdapter(
            (self.dmd, request, view),
            IMainSnippetManager,
            name=manager_name)

        self.assertTrue(
            manager is not None,
            "{manager_name!r} viewlet manager not registered"
            .format(
                manager_name=manager_name))

        manager.update()

        viewlet_name = 'js-snippet-ZenPacks.zenoss.ZPLTest1-global'
        viewlet = manager.get(viewlet_name)

        self.assertTrue(
            viewlet is not None,
            "{viewlet_name!r} viewlet not registered"
            .format(
                viewlet_name=viewlet_name))

        viewlet_substr = 'ZC.registerName('

        self.assertTrue(
            viewlet_substr in viewlet.render(),
            "{viewlet_substr!r} not in global JavaScript snippet"
            .format(
                viewlet_substr=viewlet_substr))

    def test_ComponentGridPanels(self):
        """Assert that ComponentGridPanelSnippet is registered."""
        import zope.component
        import zope.interface

        from zope.publisher.browser import BrowserView, TestRequest

        from Products.ZenUI3.browser.interfaces import IMainSnippetManager

        from ZenPacks.zenoss.ZPLTest1.APIC import APIC

        apic1 = APIC('apic1')
        request = TestRequest()
        view = BrowserView(apic1, request)

        manager_name = 'jssnippets'

        manager = zope.component.queryMultiAdapter(
            (apic1, request, view),
            IMainSnippetManager,
            name=manager_name)

        self.assertTrue(
            manager is not None,
            "{manager_name!r} viewlet manager not registered"
            .format(
                manager_name=manager_name))

        manager.update()

        viewlet_name = 'js-snippet-ZenPacks.zenoss.ZPLTest1-device'
        viewlet = manager.get(viewlet_name)

        self.assertTrue(
            viewlet is not None,
            "{viewlet_name!r} viewlet not registered"
            .format(
                viewlet_name=viewlet_name))

        viewlet_substr = 'ZPLTest1FabricNodePanel'

        self.assertTrue(
            viewlet_substr in viewlet.render(),
            "{viewlet_substr!r} not in APIC JavaScript snippet"
            .format(
                viewlet_substr=viewlet_substr))

    def test_FabricPod(self):
        """Assert that FabricPod has been properly created.

        Tests an example of creating a DeviceComponent type with a stub
        implementation.

        """
        from ZenPacks.zenoss.ZPLTest1.FabricPod import FabricPod

        pod1 = FabricPod('pod1')

        self.assertEquals(pod1.meta_type, 'ZPLTest1FabricPod')

        self.assert_superclasses(pod1, (
            DeviceComponent,
            ManagedEntity,
            ManagedObject,
            zenpacklib.Component,
            schema.FabricPod,
            ))

        self.assert_properties(pod1, ('snmpindex', 'monitor'))

        self.assert_relationships(pod1, (
            ('dependencies', ToManyRelationship),  # from ManagedEntity
            ('apic', ToOneRelationship),
            ('fabricNodes', ToManyContRelationship),
            ))

    def test_FabricNode(self):
        """Assert that FabricNode has been properly created.

        Tests an example of creating a DeviceComponent type with a
        user implementation.

        """
        from ZenPacks.zenoss.ZPLTest1.FabricNode import FabricNode

        node1 = FabricNode('node1')

        self.assertEquals(node1.meta_type, 'ZPLTest1FabricNode')

        self.assert_superclasses(node1, (
            DeviceComponent,
            ManagedEntity,
            ManagedObject,
            zenpacklib.Component,
            schema.FabricNode,
            ))

        self.assert_properties(node1, ('snmpindex', 'monitor'))

        self.assert_relationships(node1, (
            ('fabricPod', ToOneRelationship),
            ))


def test_suite():
    """Return test suite for this module."""
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestSchema))
    return suite


if __name__ == "__main__":
    from zope.testrunner.runner import Runner
    runner = Runner(found_suites=[test_suite()])
    runner.run()
