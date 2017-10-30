##############################################################################
#
# Copyright (C) Zenoss, Inc. 2010, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

import logging
log = logging.getLogger("zen.zenpacklib")
# Zenoss Imports
import Globals  # noqa
from Products.ZenUtils.Utils import unused
unused(Globals)

from Products.ZenUtils.guid.interfaces import IGlobalIdentifier
from Products.ZenMessaging.queuemessaging.publisher import ModelChangePublisher
from zenoss.protocols.protobufutil import ProtobufEnum
from ZenPacks.zenoss.ZenPackLib.lib.utils import impact_installed

class ImpactTestCase(object):
    ''''''

IMPACT_INSTALLED = impact_installed()
if IMPACT_INSTALLED:
    from ZenPacks.zenoss.Impact.protocols.impact_pb2 import GraphChangeList
    from ZenPacks.zenoss.Impact.impactd.graphchanges import GraphChangeFactory
    from ZenPacks.zenoss.Impact.protocols.policy_pb2 import Trigger as TriggerPb
    from ZenPacks.zenoss.Impact.protocols.states_pb2 import State
    from ZenPacks.zenoss.Impact.tests.ImpactTestCase import ImpactTestCase
    from ZenPacks.zenoss.Impact.DynamicServiceOrganizer import DynamicServiceOrganizer, manage_addRootDynamicServicesOrganizer

from ZenPacks.zenoss.ZenPackLib.tests.ZPLTestBase import ZPLTestMockZenPack
from ZenPacks.zenoss.ZenPackLib.lib.base.BaseTriggers import BaseTriggers


YAML_DOC = """
name: ZenPacks.zenoss.MockZenPack

class_relationships:
- BasicDevice 1:MC BasicComponent
- SubComponent M:M AuxComponent

classes:
  BasicDevice:
    base: [zenpacklib.Device]
    monitoring_templates: [BasicDevice]
    impacts: [basicComponents]
    impacted_by: [basicComponents]
  BasicComponent:
    base: [zenpacklib.Component]
    monitoring_templates: [BasicComponent]
    impacted_by: [basicDevice]
    impact_triggers:
      test_1:
        policy: AVAILABILITY
        trigger: policyPercentageTrigger
        threshold: 25
        state: ATRISK
        dependent_state: DOWN
  SubComponent:
    base: [BasicComponent]
    monitoring_templates: [SubComponent]
    impacted_by: [basicDevice]
    impacts: [auxComponents]
  AuxComponent:
    base: [SubComponent]
    monitoring_templates: [AuxComponent]
    impacted_by: [basicDevice, subComponents]
device_classes:
  /Server/Basic:
    remove: true
    zProperties:
      zPythonClass: ZenPacks.zenoss.MockZenPack.BasicDevice

"""


class TestImpactTriggers(ZPLTestMockZenPack):
    """Test Impact Triggers"""

    yaml_doc = YAML_DOC
    zenpack_name = 'ZenPacks.zenoss.MockZenPack'

    def afterSetUp(self):
        super(TestImpactTriggers, self).afterSetUp()
        self.modelChangePublisher = ModelChangePublisher()
        self.dynamicServicesRoot = manage_addRootDynamicServicesOrganizer(self.dmd)
        self.org = self.dynamicServicesRoot
        self.graphChangeList = GraphChangeList()
        self.factory = GraphChangeFactory(self.dmd, self.graphChangeList)

    def get_guid(self, ob):
        """hackish way to do this"""
        gid = IGlobalIdentifier(ob)
        try:
            gid.create(force=True, update_global_catalog=False)
        except:
            pass

    def find_trigger_spec(self, trigger, spec):
        for t_spec in spec.impact_triggers.values():
            args = t_spec.get_trigger()
            msg = args[0]
            if msg == trigger.triggerId:
                return t_spec
        return None

    def testFillTriggerProtoBuf(self):
        triggerPb = TriggerPb()
        spec = self.z.cfg.classes.get('BasicComponent')
        ob = self.z.obs[1]
        self.get_guid(ob)
        impact_fact = BaseTriggers(ob)
        for trigger in impact_fact.get_triggers():
            t_spec = self.find_trigger_spec(trigger, spec)
            args = t_spec.get_trigger()
            msg = args[0]
            self.factory._fillTriggerProto(triggerPb, trigger)
            self.assertEquals(ob._guid, triggerPb.nodeId)
            self.assertEquals(msg, triggerPb.triggerId)
            self.assertEquals(t_spec.trigger, triggerPb.triggerType)
            self.assertEquals('global', triggerPb.contextId)
            pbe = ProtobufEnum(State, enum='StateType')
            self.assertEquals(pbe.AVAILABILITY, triggerPb.policyType)
            self.assertEquals('AVAILABILITY', pbe.getName(triggerPb.policyType))
            self.assertEquals(3, len(triggerPb.properties))
            self.assertEquals("threshold", triggerPb.properties[0].name)
            self.assertEquals(str(t_spec.threshold), triggerPb.properties[0].value)
            self.assertEquals("dependentState", triggerPb.properties[1].name)
            self.assertEquals(t_spec.dependent_state, triggerPb.properties[1].value)
            self.assertEquals("state", triggerPb.properties[2].name)
            self.assertEquals(t_spec.state, triggerPb.properties[2].value)


def test_suite():
    """Return test suite for this module."""
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    if IMPACT_INSTALLED:
        suite.addTest(makeSuite(TestImpactTriggers))
    return suite


if __name__ == "__main__":
    from zope.testrunner.runner import Runner
    runner = Runner(found_suites=[test_suite()])
    runner.run()
