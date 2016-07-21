from Products.ZenModel.DeviceComponent import DeviceComponent
from Products.ZenModel.ManagedEntity import ManagedEntity
from ..factory.ComponentTypeFactory import ComponentTypeFactory


Component = ComponentTypeFactory('Component', (DeviceComponent, ManagedEntity))
