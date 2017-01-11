##############################################################################
#
# Copyright (C) Zenoss, Inc. 2016, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################
from Products.ZenModel.CPU import CPU as BaseCPU
from Products.ZenModel.DeviceComponent import DeviceComponent as BaseDeviceComponent
from Products.ZenModel.ExpansionCard import ExpansionCard as BaseExpansionCard
from Products.ZenModel.Fan import Fan as BaseFan
from Products.ZenModel.FileSystem import FileSystem as BaseFileSystem
from Products.ZenModel.HardDisk import HardDisk as BaseHardDisk
from Products.ZenModel.HWComponent import HWComponent as BaseHWComponent
from Products.ZenModel.IpInterface import IpInterface as BaseIpInterface
from Products.ZenModel.IpRouteEntry import IpRouteEntry as BaseIpRouteEntry
from Products.ZenModel.IpService import IpService as BaseIpService
from Products.ZenModel.ManagedEntity import ManagedEntity as BaseManagedEntity
from Products.ZenModel.OSComponent import OSComponent as BaseOSComponent
from Products.ZenModel.OSProcess import OSProcess as BaseOSProcess
from Products.ZenModel.PowerSupply import PowerSupply as BasePowerSupply
from Products.ZenModel.Service import Service as BaseService
from Products.ZenModel.TemperatureSensor import TemperatureSensor as BaseTemperatureSensor
from Products.ZenModel.WinService import WinService as BaseWinService

from ..factory.ComponentTypeFactory import ComponentTypeFactory


Component = ComponentTypeFactory('Component', (BaseDeviceComponent, BaseManagedEntity))
HWComponent = ComponentTypeFactory('HWComponent', (BaseHWComponent,))

CPU = ComponentTypeFactory('CPU', (BaseCPU,))
ExpansionCard = ComponentTypeFactory('ExpansionCard', (BaseExpansionCard,))
Fan = ComponentTypeFactory('Fan', (BaseFan,))
HardDisk = ComponentTypeFactory('HardDisk', (BaseHardDisk,))
PowerSupply = ComponentTypeFactory('PowerSupply', (BasePowerSupply,))
TemperatureSensor = ComponentTypeFactory('TemperatureSensor', (BaseTemperatureSensor,))

OSComponent = ComponentTypeFactory('OSComponent', (BaseOSComponent,))
FileSystem = ComponentTypeFactory('FileSystem', (BaseFileSystem,))
IpInterface = ComponentTypeFactory('IpInterface', (BaseIpInterface,))
IpRouteEntry = ComponentTypeFactory('IpRouteEntry', (BaseIpRouteEntry,))
OSProcess = ComponentTypeFactory('OSProcess', (BaseOSProcess,))

Service = ComponentTypeFactory('Service', (BaseService,))
IpService = ComponentTypeFactory('IpService', (BaseIpService,))
WinService = ComponentTypeFactory('WinService', (BaseWinService,))

# Backwards-compatibility aliases.
HardwareComponent = HWComponent