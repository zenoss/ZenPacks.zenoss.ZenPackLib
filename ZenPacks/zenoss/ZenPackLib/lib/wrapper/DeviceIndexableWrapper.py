from zope.component import adapts
from zope.interface import implements
from Products.Zuul.catalog.interfaces import IIndexableWrapper
from Products.Zuul.catalog.global_catalog import DeviceWrapper
from ..base.DeviceBase import DeviceBase


class DeviceIndexableWrapper(DeviceWrapper):

    """Indexing wrapper for ZenPack devices.

    This is required to make sure that key classes are returned by
    objectImplements even if their depth within the inheritence tree
    would otherwise exclude them. Certain searches in Zenoss expect
    objectImplements to contain Device.

    """

    implements(IIndexableWrapper)
    adapts(DeviceBase)

    def objectImplements(self):
        """Return list of implemented interfaces and classes.

        Extends DeviceWrapper by ensuring that Device will always be
        part of the returned list.

        """
        dottednames = super(DeviceIndexableWrapper, self).objectImplements()

        return list(set(dottednames).union([
            'Products.ZenModel.Device.Device',
            ]))
