from zope.component import adapts
from zope.interface import implements
from Products.Zuul.catalog.interfaces import IIndexableWrapper
from Products.Zuul.catalog.global_catalog import ComponentWrapper
from ..base.ComponentBase import ComponentBase


class ComponentIndexableWrapper(ComponentWrapper):

    """Indexing wrapper for ZenPack components.

    This is required to make sure that key classes are returned by
    objectImplements even if their depth within the inheritence tree
    would otherwise exclude them. Certain searches in Zenoss expect
    objectImplements to contain DeviceComponent and ManagedEntity where
    applicable.

    """

    implements(IIndexableWrapper)
    adapts(ComponentBase)

    def objectImplements(self):
        """Return list of implemented interfaces and classes.

        Extends ComponentWrapper by ensuring that DeviceComponent will
        always be part of the returned list.

        """
        dottednames = super(ComponentIndexableWrapper, self).objectImplements()

        return list(set(dottednames).union([
            'Products.ZenModel.DeviceComponent.DeviceComponent',
            ]))
