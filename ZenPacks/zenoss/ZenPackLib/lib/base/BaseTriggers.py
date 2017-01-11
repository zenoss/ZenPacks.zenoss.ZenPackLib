##############################################################################
#
# Copyright (C) Zenoss, Inc. 2016, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################
from zope.interface import implements
from zope.component import adapts
from Products.ZenUtils.guid.interfaces import IGlobalIdentifier
from ..helpers.ZenPackLibLog import DEFAULTLOG
from .ComponentBase import ComponentBase
from .DeviceBase import DeviceBase


def guid(obj):
    """Return GUID for obj."""
    return IGlobalIdentifier(obj).getGUID()


class BaseImpactAdapterFactory(object):

    """Abstract base for Impact adapter factories."""

    adapts(DeviceBase, ComponentBase)

    def __init__(self, adapted):
        self.adapted = adapted

    def guid(self):
        if not hasattr(self, '_guid'):
            self._guid = guid(self.adapted)

        return self._guid


# Lazy imports to make this module not require Impact.
Trigger = None

class BaseTriggers(BaseImpactAdapterFactory):

    """Abstract base for INodeTriggers adapter factories."""

    triggers = []

    def get_triggers(self):
        '''
        Return list of triggers defined by subclass' triggers property.
        '''
        # Lazy import without incurring import overhead.
        # http://wiki.python.org/moin/PythonSpeed/PerformanceTips#Import_Statement_Overhead
        global Trigger
        if not Trigger:
            from ZenPacks.zenoss.Impact.impactd import Trigger

        impact_triggers = getattr(self.adapted, 'impact_triggers', [])
        for trigger_args in impact_triggers:
            yield Trigger(self.guid(), *trigger_args)

