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