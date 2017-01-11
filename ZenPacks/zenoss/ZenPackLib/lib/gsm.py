##############################################################################
#
# Copyright (C) Zenoss, Inc. 2016, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################
from zope.component import getGlobalSiteManager
from Products.Zuul.catalog.interfaces import IIndexableWrapper, IPathReporter
from .wrapper.DeviceIndexableWrapper import DeviceIndexableWrapper
from .wrapper.ComponentIndexableWrapper import ComponentIndexableWrapper
from .wrapper.ComponentPathReporter import ComponentPathReporter
from .base.ComponentBase import ComponentBase
from .base.DeviceBase import DeviceBase

GSM = getGlobalSiteManager()

GSM.registerAdapter(DeviceIndexableWrapper, (DeviceBase,), IIndexableWrapper)
GSM.registerAdapter(ComponentIndexableWrapper, (ComponentBase,), IIndexableWrapper)
GSM.registerAdapter(ComponentPathReporter, (ComponentBase,), IPathReporter)

def get_gsm():
    ''''''
    GSM = getGlobalSiteManager()
    GSM.registerAdapter(DeviceIndexableWrapper, (DeviceBase,), IIndexableWrapper)
    GSM.registerAdapter(ComponentIndexableWrapper, (ComponentBase,), IIndexableWrapper)
    GSM.registerAdapter(ComponentPathReporter, (ComponentBase,), IPathReporter)
    return GSM