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
from Products.ZenUtils.Utils import unused
unused(Globals)


from zope.publisher.browser import BrowserView, TestRequest
from Products.ZenUI3.browser.interfaces import IMainSnippetManager
from Products.ZenModel.ZenPack import ZenPack as ZenPackBase
from Products.ZenModel.Device import Device
from Products.ZenModel.DeviceComponent import DeviceComponent
from Products.ZenModel.ManagedEntity import ManagedEntity
from Products.ZenRelations.ToManyRelationship import ToManyRelationship
from Products.ZenRelations.ToManyContRelationship import ToManyContRelationship
from Products.ZenRelations.ToOneRelationship import ToOneRelationship
from Products.ZenRelations.zPropertyCategory import getzPropertyCategory
from Products.Zuul.infos.component import ComponentInfo
from Products.Zuul.infos.device import DeviceInfo
from Products.Zuul.interfaces import IInfo

# zenpacklib Imports
from ZenPacks.zenoss.ZenPackLib import zenpacklib
from ZenPacks.zenoss.ZenPackLib.tests.ZPLTestBase import ZPLTestBase
from ZenPacks.zenoss.ZenPackLib.lib.spec.ZenPackSpec import GSM
from Products.ZenUtils.ZenScriptBase import ZenScriptBase


YAML_DOC = """
name: ZenPacks.zenoss.ZPLTest1
zProperties:
  DEFAULTS:
    category: ZPLTest1
  zZPLTest1HealthInterval:
    type: int
    default: 300
  zZPLTest1Password:
    type: password
    default: ''
  zZPLTest1Port:
    type: int
    default: 443
  zZPLTest1SSL:
    type: boolean
    default: true
  zZPLTest1Username:
    default: admin
class_relationships:
- APIC 1:MC FabricPod
- APIC 1:MC FvTenant
- FabricPod 1:MC FabricNode
- FabricNode 1:MC L1PhysIf
- FvTenant 1:MC FvCtx
- FvTenant 1:MC FvBD
- FvTenant 1:MC VzBrCP
- FvTenant 1:MC FvAp
- FvTenant 1:MC VnsGraphInst
- FvTenant 1:MC VnsLDevVip
- VnsGraphInst 1:MC VnsNodeInst
- VnsLDevVip 1:MC VnsCDev
- FvAp 1:MC FvAEPg
- FvAEPg 1:MC FvRsProv
- FvAEPg 1:MC FvRsCons
- FvCtx 1:M FvBD
- FvBD 1:M FvAEPg
- VzBrCP 1:M FvRsProv
- VzBrCP 1:M FvRsCons
- VzBrCP 1:M VnsGraphInst
- VnsLDevVip 1:M VnsNodeInst
device_classes:
  /Network/ZPLTest1:
    zProperties:
      zPythonClass: "ZenPacks.zenoss.ZPLTest1.APIC"
    templates:
      APIC:
        description: ZPLTest1 fabric monitoring.
        targetPythonClass: ZenPacks.zenoss.ZPLTest1.APIC
        datasources:
          faults:
            type: ZPLTest1 Faults
            cycletime: 300
      FabricNode:
        description: ZPLTest1 fabric node monitoring.
        targetPythonClass: ZenPacks.zenoss.ZPLTest1.FabricNode
        thresholds:
          node overall health below 75:
            dsnames: [fabricNodeHealth_healthAvg]
            eventClass: /Status
            severity: err
            minval: '75'
        datasources:
          fabricNodeHealth:
            type: ZPLTest1 Stats
            datapoints:
              healthAvg:
                rrdmin: 0
                rrdmax: 100
                aliases: {health_avg__pct: null}
              healthMax:
                rrdmin: 0
                rrdmax: 100
                aliases: {health_max__pct: null}
              healthMin:
                rrdmin: 0
                rrdmax: 100
                aliases: {health_min__pct: null}
            classname: topSystem
            object_dn: ${here/apic_dn}/sys
            statistic: fabricNodeHealth
            base_dn: ${here/apic_dn}
        graphs:
          Node Overall Health:
            units: score
            miny: 0
            maxy: 100
            graphpoints:
              Average:
                dpName: fabricNodeHealth_healthAvg
                lineWidth: 2
                format: '%4.0lf'
                color: 00cc00
              Maximum:
                dpName: fabricNodeHealth_healthMax
                format: '%4.0lf'
                color: '666666'
              Minimum:
                dpName: fabricNodeHealth_healthMin
                format: '%4.0lf'
                color: '666666'
      FabricPod:
        description: ZPLTest1 fabric pod monitoring.
        targetPythonClass: ZenPacks.zenoss.ZPLTest1.FabricPod
        thresholds:
          fabric overall health below 75:
            dsnames: [fabricOverallHealth_healthAvg]
            eventClass: /Status
            severity: err
            minval: '75'
        datasources:
          fabricOverallHealth:
            type: ZPLTest1 Stats
            datapoints:
              healthAvg:
                rrdmin: 0
                rrdmax: 100
                aliases: {health_avg__pct: null}
              healthMax:
                rrdmin: 0
                rrdmax: 100
                aliases: {health_max__pct: null}
              healthMin:
                rrdmin: 0
                rrdmax: 100
                aliases: {health_min__pct: null}
            classname: fabricTopology
            object_dn: topology
            statistic: fabricOverallHealth
        graphs:
          Pod Overall Health:
            units: score
            miny: 0
            maxy: 100
            graphpoints:
              Average:
                dpName: fabricOverallHealth_healthAvg
                lineWidth: 2
                format: '%4.0lf'
                color: 00cc00
              Maximum:
                dpName: fabricOverallHealth_healthMax
                format: '%4.0lf'
                color: '666666'
              Minimum:
                dpName: fabricOverallHealth_healthMin
                format: '%4.0lf'
                color: '666666'
      Health:
        description: ZPLTest1 health monitoring.
        targetPythonClass: ZenPacks.zenoss.ZPLTest1.ManagedObject
        thresholds:
          health at 0:
            dsnames: [health_cur]
            eventClass: /Status
            severity: crit
            minval: '0.9'
          health below 90:
            dsnames: [health_cur]
            eventClass: /Status
            severity: err
            minval: '90'
        datasources:
          health:
            type: ZPLTest1 Health
            datapoints:
              cur:
                rrdmin: 0
                rrdmax: 100
                aliases: {health_current__pct: null}
        graphs:
          Health:
            units: score
            miny: 0
            maxy: 100
            graphpoints:
              Current:
                dpName: health_cur
                lineWidth: 2
                format: '%4.0lf'
      L1PhysIf:
        description: ZPLTest1 physical interface monitoring.
        targetPythonClass: ZenPacks.zenoss.ZPLTest1.L1PhysIf
        datasources:
          eqptEgrTotal:
            type: ZPLTest1 Stats
            datapoints:
              bytesRate:
                rrdmin: 0
                aliases: {if_out_bytessec: null, outputOctets__bytes: null}
              pktsRate:
                rrdmin: 0
                aliases: {if_out__pktssec: null}
              utilAvg:
                rrdmin: 0
                rrdmax: 100
                aliases: {if_out__pct: null}
            classname: l1PhysIf
            statistic: eqptEgrTotal
            base_dn: ${here/node_dn}
          eqptIngrTotal:
            type: ZPLTest1 Stats
            datapoints:
              bytesRate:
                rrdmin: 0
                aliases: {if_in__bytessec: null, inputOctets__bytes: null}
              pktsRate:
                rrdmin: 0
                aliases: {if_in__pktssec: null}
              utilAvg:
                rrdmin: 0
                rrdmax: 100
                aliases: {if_in__pct: null}
            classname: l1PhysIf
            statistic: eqptIngrTotal
            base_dn: ${here/node_dn}
        graphs:
          Throughput (bytes):
            units: bytes/sec
            miny: 0
            graphpoints:
              Egress:
                dpName: eqptEgrTotal_bytesRate
                format: '%7.2lf%s'
              Ingress:
                dpName: eqptIngrTotal_bytesRate
                format: '%7.2lf%s'
          Throughput (packets):
            units: packets/sec
            miny: 0
            graphpoints:
              Egress:
                dpName: eqptEgrTotal_pktsRate
                format: '%7.2lf%s'
                rpn: 8,*
              Ingress:
                dpName: eqptIngrTotal_pktsRate
                format: '%7.2lf%s'
                rpn: 8,*
          Utilization:
            units: percent
            miny: 0
            maxy: 100
            graphpoints:
              Egress:
                dpName: eqptEgrTotal_utilAvg
                format: '%7.2lf%%'
              Ingress:
                dpName: eqptIngrTotal_utilAvg
                format: '%7.2lf%%'
classes:
  DEFAULTS:
    base: [ManagedObject]
  APIC:
    base: [zenpacklib.Device]
    meta_type: ZPLTest1
    label: APIC
  FabricNode:
    meta_type: ZPLTest1FabricNode
    label: Fabric Node
    label_width: 65
    content_width: 100
    order: 31
    properties:
      role:
        label: Role
    impacts: [node_impacts]
    impacted_by: [node_impacted_by]
    monitoring_templates: [FabricNode, Health]
  FabricPod:
    meta_type: ZPLTest1FabricPod
    label: Fabric Pod
    order: 30
    properties:
      editable_boolean:
        type: boolean
        label: Editable Boolean
        editable: true
      readonly_boolean:
        type: boolean
        label: Read-Only Boolean
    impacts: [fvCtxs]
    impacted_by: [leaf_nodes]
  FvAEPg:
    meta_type: ZPLTest1ApplicationEndpointGroup
    label: Endpoint Group
    short_label: Endpoint Group
    order: 13
    properties:
      mapped_network:
        type: entity
        label: Mapped Network
        label_width: 85
        content_width: 160
        renderer: Zenoss.render.default_uid_renderer
        order: 4.1
        api_only: true
        api_backendtype: method
      vsphere_dvportgroup_ids:
        type: lines
        label: VMware vSphere dvPortgroup IDs
        index_type: keyword
        grid_display: false
        order: 4.2
    impacts: [fvAp, impacts_fvAEPgs, impacts_vnsGraphInsts]
    impacted_by: [fvBD, impacted_by_fvAEPgs, impacted_by_vnsGraphInsts, vsphere_dvportgroups,
      vsphere_vms, devices]
    monitoring_templates: [Health]
  FvAp:
    meta_type: ZPLTest1Application
    label: Application
    order: 12
    impacts: [fvTenant]
    impacted_by: [fvAEPgs]
    monitoring_templates: [Health]
  FvBD:
    meta_type: ZPLTest1BridgeDomain
    label: Bridge Domain
    order: 16
    impacts: [fvAEPgs]
    impacted_by: [fvCtx]
    monitoring_templates: [Health]
  FvCtx:
    meta_type: ZPLTest1PrivateNetwork
    label: Private Network
    order: 15
    impacts: [fvBDs]
    impacted_by: [fabricPods]
    monitoring_templates: [Health]
  FvRsCons:
    meta_type: ZPLTest1ContractConsumed
    label: Contract Consumed
    plural_label: Contracts Consumed
    short_label: Consumes
    plural_short_label: Consumes
    order: 14.2
  FvRsProv:
    meta_type: ZPLTest1ContractProvided
    label: Contract Provided
    plural_label: Contracts Provided
    short_label: Provides
    plural_short_label: Provides
    order: 14.1
  FvTenant:
    meta_type: ZPLTest1Tenant
    label: Tenant
    order: 11
    impacted_by: [fvAps]
    monitoring_templates: [Health]
  L1PhysIf:
    meta_type: ZPLTest1L1PhysIf
    label: Physical Interface
    label_width: 95
    order: 36
    properties:
      layer:
        label: Layer
        order: 4.3
      portT:
        label: Port Type
        order: 4.2
      speed:
        type: int
        label: Speed
        renderer: Zenoss.render.ZPLTest1_linkSpeed
        order: 4.1
    monitoring_templates: [L1PhysIf, Health]
  ManagedObject:
    base: [zenpacklib.Component]
    properties:
      apic_classname:
        label: ACI Object Class
        grid_display: false
        order: 4.93
      apic_dn:
        label: ACI Distinguished Name (DN)
        index_type: field
        grid_display: false
        order: 4.91
      apic_health_dn:
        label: ACI Health Distinguished Name (DN)
        grid_display: false
        order: 4.92
  VnsCDev:
    meta_type: ZPLTest1VnsCDev
    label: Service Device
    order: 20
    properties:
      cmgmt_host:
        label: Management Address
        index_type: field
        grid_display: false
        order: 4.4
      cmgmt_port:
        label: Management Port
        grid_display: false
        order: 4.5
      devCtxLbl:
        label: Context Label
        order: 4.1
      vcenterName:
        label: vCenter Name
        order: 4.3
      vmName:
        label: VM Name
        order: 4.2
    impacts: [vnsLDevVip]
    impacted_by: [cmgmt_devices]
    monitoring_templates: [Health]
  VnsGraphInst:
    meta_type: ZPLTest1VnsGraphInst
    label: Service Graph
    content_width: 180
    order: 17
    properties:
      graphDn:
        label: Graph DN
        label_width: 55
        content_width: 230
        order: 4.1
    impacts: [impacts_fvAEPgs]
    impacted_by: [impacted_by_fvAEPgs, vnsNodeInsts]
  VnsLDevVip:
    meta_type: ZPLTest1VnsLDevVip
    label: Service Cluster
    order: 19
    properties:
      cmgmt_host:
        label: Management Address
        index_type: field
        grid_display: false
        order: 4.6
      cmgmt_port:
        label: Management Port
        grid_display: false
        order: 4.7
      contextAware:
        label: Context Aware
        order: 4.3
      devtype:
        label: Device Type
        order: 4.1
      funcType:
        label: Function Type
        grid_display: false
        order: 4.5
      mgmtType:
        label: Management Type
        order: 4.2
      mode:
        label: Mode
        order: 4.4
    impacts: [vnsNodeInsts]
    impacted_by: [vnsCDevs]
  VnsNodeInst:
    meta_type: ZPLTest1VnsNodeInst
    label: Service Function Node
    short_label: Function Node
    order: 18
    properties:
      funcType:
        label: Function Type
        order: 4.1
      lbvserver_name:
        label: Load Balancer Virtual Server Name
        index_type: field
        grid_display: false
        order: 4.9
    impacts: [vnsGraphInst]
    impacted_by: [vnsLDevVip, netscaler_virtual_servers]
  VzBrCP:
    meta_type: ZPLTest1Contract
    label: Contract
    order: 14

"""


class TestSchema(ZPLTestBase, ZenScriptBase):

    """Test suite for ZenPack's schema.

    Not all schema classes are tested. The idea is to test at least one
    example of each zenpacklib functionality used.

    """

    disableLogging = False
    yaml_doc = YAML_DOC
    manager = None

    def afterSetUp(self):
        super(TestSchema, self).afterSetUp()
        ZenScriptBase.__init__(self, app=self.app, connect=False)
        self.cfg = self.z.cfg

    def find_viewlet(self, name):
        for v in self.manager.viewlets:
            if str(v.__name__) == name:
                return v
        return None

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
            'zenpacklib' not in self.z.schema.APIC.__module__,
            "{schema.APIC.__module__!r} contains 'zenpacklib'"
            .format(schema=self.z.schema))

    def test_stubclass(self):
        """Assert that a dynamic stub class was created properly."""
        stub = self.z.get_cls('APIC')
        self.assertTrue(
            'zenpacklib' not in stub.__module__,
            "{APIC.__module__!r} contains 'zenpacklib'"
            .format(APIC=stub))

    def test_ZenPack(self):
        """Assert that ZenPack class has been properly created."""

        zenpack = self.z.zp.ZenPack(self.z.zp.__name__)

        self.assert_superclasses(zenpack, (
            self.z.zp.ZenPack,
            self.z.schema.ZenPack,
            ZenPackBase
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
        stub = self.z.get_cls('APIC')
        schema = self.z.schema

        apic1 = stub('apic1')

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
        # z = ZPLTestHarness(YAML_DOC)

        APIC = self.z.zp.APIC.APIC
        APICInfo = self.z.zp.APIC.APICInfo
        FabricNode = self.z.zp.FabricNode.FabricNode
        FabricNodeInfo = self.z.zp.FabricNode.FabricNodeInfo

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

    def register_viewlets(self):
        self.cfg.create_device_js_snippet()
        self.cfg.create_global_js_snippet()

        apic1 = self.z.build_ob('APIC')
        request = TestRequest()
        view = BrowserView(apic1, request)

        self.manager_name = 'jssnippets'
        self.manager = GSM.queryMultiAdapter((apic1, request, view), IMainSnippetManager, name=self.manager_name)
        if self.manager:
            self.manager.update()

    def test_0_Registered(self):
        """Test GSM registration"""
        self.register_viewlets()
        self.assertTrue(
            self.manager is not None,
            "{manager_name!r} viewlet manager not registered"
            .format(
                manager_name=self.manager_name))

        self.check_global()
        self.check_device()

    def check_global(self):
        """Assert that JavaScript registerNames is registered."""

        viewlet_name = 'js-snippet-ZenPacks.zenoss.ZPLTest1-global'
        viewlet = self.find_viewlet(viewlet_name)

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

    def check_device(self):
        """Assert that ComponentGridPanelSnippet is registered."""
        self.assertTrue(
            self.manager is not None,
            "{manager_name!r} viewlet manager not registered"
            .format(manager_name=self.manager_name))

        viewlet_name = 'js-snippet-ZenPacks.zenoss.ZPLTest1-device'
        viewlet = self.find_viewlet(viewlet_name)

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
        pod1 = self.z.build_ob('FabricPod')

        self.assertEquals(pod1.meta_type, 'ZPLTest1FabricPod')

        self.assert_superclasses(pod1, (
            DeviceComponent,
            ManagedEntity,
            self.z.get_cls('ManagedObject'),
            zenpacklib.Component,
            self.z.schema.FabricPod,
            ))

        self.assert_properties(
            pod1,
            ('snmpindex', 'monitor', 'editable_boolean', 'readonly_boolean'))

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
        node1 = self.z.build_ob('FabricNode')
        self.assertEquals(node1.meta_type, 'ZPLTest1FabricNode')

        self.assert_superclasses(node1, (
            DeviceComponent,
            ManagedEntity,
            self.z.get_cls('ManagedObject'),
            zenpacklib.Component,
            self.z.schema.FabricNode,
            ))

        self.assert_properties(node1, ('snmpindex', 'monitor', 'role'))

        self.assert_relationships(node1, (('fabricPod', ToOneRelationship),))


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
