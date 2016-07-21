from Products.Zuul.form import schema
from Products.Zuul.interfaces.component import IComponentInfo


class IHardwareComponentInfo(IComponentInfo):

    """Info interface for ZenPackHardwareComponent.

    This exists because Zuul has no HWComponent info interface.
    """

    manufacturer = schema.Entity(title=u'Manufacturer')
    product = schema.Entity(title=u'Model')

