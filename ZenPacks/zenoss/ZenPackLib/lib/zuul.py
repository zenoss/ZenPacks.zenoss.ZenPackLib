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

from Products.Zuul.facades.processfacade import ProcessFacade
from Products.Zuul.facades.servicefacade import ServiceFacade


schema_map = {
     Device: {'interface': IDeviceInfo, 'info': DeviceInfo, 'facade': None},
     Component: {'interface': IComponentInfo, 'info': ComponentInfo, 'facade': None},
     HWComponent: {'interface': IHWComponentInfo, 'info': HWComponentInfo, 'facade': None},
     HardwareComponent: {'interface': IHWComponentInfo, 'info': HWComponentInfo, 'facade': None},
     CPU: {'interface': ICPUInfo, 'info': CPUInfo, 'facade': None},
     ExpansionCard: {'interface': IExpansionCardInfo, 'info': ExpansionCardInfo, 'facade': None},
     Fan: {'interface': IFanInfo, 'info': FanInfo, 'facade': None},
     HardDisk: {'interface': IHWComponentInfo, 'info': HWComponentInfo, 'facade': None},
     PowerSupply: {'interface': IPowerSupplyInfo, 'info': PowerSupplyInfo, 'facade': None},
     TemperatureSensor: {'interface': ITemperatureSensorInfo, 'info': TemperatureSensorInfo, 'facade': None},
     OSComponent: {'interface': IComponentInfo, 'info': ComponentInfo, 'facade': None},
     FileSystem: {'interface': IFileSystemInfo, 'info': FileSystemInfo, 'facade': None},
     IpInterface: {'interface': IIpInterfaceInfo, 'info': IpInterfaceInfo, 'facade': None},
     IpRouteEntry: {'interface': IIpRouteEntryInfo, 'info': IpRouteEntryInfo, 'facade': None},
     OSProcess: {'interface': IOSProcessInfo, 'info': OSProcessInfo, 'facade': ProcessFacade},
     IpService: {'interface': IIpServiceInfo, 'info': IpServiceInfo, 'facade': ServiceFacade},
     WinService: {'interface': IWinServiceInfo, 'info': WinServiceInfo, 'facade': ServiceFacade},
     Service: {'interface': IServiceInfo, 'info': ServiceInfo, 'facade': ServiceFacade},
     }

