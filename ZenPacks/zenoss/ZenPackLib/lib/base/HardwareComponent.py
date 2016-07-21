from Products.ZenModel.HWComponent import HWComponent
from ..factory.ComponentTypeFactory import ComponentTypeFactory


HardwareComponent = ComponentTypeFactory('HardwareComponent', (HWComponent,))
