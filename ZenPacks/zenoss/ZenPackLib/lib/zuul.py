from .base.Device import Device
from .base.Component import (
    Component,
    HWComponent,
    HardwareComponent,
    CPU,
    ExpansionCard,
    Fan,
    HardDisk,
    PowerSupply,
    TemperatureSensor,
    OSComponent,
    FileSystem,
    IpInterface,
    IpRouteEntry,
    OSProcess,
    Service,
    IpService,
    WinService
    )

from Products.Zuul.infos.device import DeviceInfo
from Products.Zuul.interfaces.device import IDeviceInfo

from Products.Zuul.infos.component import ComponentInfo
from Products.Zuul.infos.component.cpu import CPUInfo
from Products.Zuul.infos.component.expansioncard import ExpansionCardInfo
from Products.Zuul.infos.component.fan import FanInfo
from Products.Zuul.infos.component.powersupply import PowerSupplyInfo
from Products.Zuul.infos.component.temperaturesensor import TemperatureSensorInfo
from Products.Zuul.infos.component.filesystem import FileSystemInfo
from Products.Zuul.infos.component.ipinterface import IpInterfaceInfo
from Products.Zuul.infos.component.iprouteentry import IpRouteEntryInfo
from Products.Zuul.infos.component.osprocess import OSProcessInfo
from Products.Zuul.infos.component.ipservice import IpServiceInfo
from Products.Zuul.infos.component.winservice import WinServiceInfo
from Products.Zuul.interfaces.component import (
    IComponentInfo,
    ICPUInfo,
    IExpansionCardInfo,
    IFanInfo,
    IPowerSupplyInfo,
    ITemperatureSensorInfo,
    IFileSystemInfo,
    IIpInterfaceInfo,
    IIpRouteEntryInfo,
    IOSProcessInfo,
    IIpServiceInfo,
    IWinServiceInfo
    )

from Products.Zuul.infos.service import ServiceInfo
from Products.Zuul.interfaces.service import IServiceInfo

from .info import HWComponentInfo
from .interfaces import IHWComponentInfo


schema_map = {
     Device: {'interface': IDeviceInfo, 'info': DeviceInfo},
     Component: {'interface': IComponentInfo, 'info': ComponentInfo},
     HWComponent: {'interface': IHWComponentInfo, 'info': HWComponentInfo},
     HardwareComponent: {'interface': IHWComponentInfo, 'info': HWComponentInfo},
     CPU: {'interface': ICPUInfo, 'info': CPUInfo},
     ExpansionCard: {'interface': IExpansionCardInfo, 'info': ExpansionCardInfo},
     Fan: {'interface': IFanInfo, 'info': FanInfo},
     HardDisk: {'interface': IHWComponentInfo, 'info': HWComponentInfo},
     PowerSupply: {'interface': IPowerSupplyInfo, 'info': PowerSupplyInfo},
     TemperatureSensor: {'interface': ITemperatureSensorInfo, 'info': TemperatureSensorInfo},
     OSComponent: {'interface': IComponentInfo, 'info': ComponentInfo},
     FileSystem: {'interface': IFileSystemInfo, 'info': FileSystemInfo},
     IpInterface: {'interface': IIpInterfaceInfo, 'info': IpInterfaceInfo},
     IpRouteEntry: {'interface': IIpRouteEntryInfo, 'info': IpRouteEntryInfo},
     OSProcess: {'interface': IOSProcessInfo, 'info': OSProcessInfo},
     Service: {'interface': IServiceInfo, 'info': ServiceInfo},
     IpService: {'interface': IIpServiceInfo, 'info': IpServiceInfo},
     WinService: {'interface': IWinServiceInfo, 'info': WinServiceInfo},
     }

