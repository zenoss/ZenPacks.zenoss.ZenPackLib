from Products.ZenModel.Device import Device
from ..factory.DeviceTypeFactory import DeviceTypeFactory


Device = DeviceTypeFactory('Device', (Device,))
