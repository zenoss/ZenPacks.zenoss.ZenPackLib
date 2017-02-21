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

from Products.Zuul.facades.devicefacade import DeviceFacade
from Products.Zuul.facades.processfacade import ProcessFacade
from Products.Zuul.facades.servicefacade import ServiceFacade

from Products.Zuul.catalog.paths import (
     DevicePathReporter,
     ServicePathReporter,
     InterfacePathReporter,
     ProcessPathReporter,
     ProductPathReporter
     )

schema_map = {
    Device: {'interface': IDeviceInfo, 'info': DeviceInfo, 'reporter': DevicePathReporter, 'facade': DeviceFacade},
    Component: {'interface': IComponentInfo, 'info': ComponentInfo, 'reporter': None, 'facade': None},
    HWComponent: {'interface': IHWComponentInfo, 'info': HWComponentInfo, 'reporter': ProductPathReporter, 'facade': None},
    HardwareComponent: {'interface': IHWComponentInfo, 'info': HWComponentInfo, 'reporter': ProductPathReporter, 'facade': None},
    CPU: {'interface': ICPUInfo, 'info': CPUInfo, 'reporter': None, 'facade': None},
    ExpansionCard: {'interface': IExpansionCardInfo, 'info': ExpansionCardInfo, 'reporter': None, 'facade': None},
    Fan: {'interface': IFanInfo, 'info': FanInfo, 'reporter': None, 'facade': None},
    HardDisk: {'interface': IHWComponentInfo, 'info': HWComponentInfo, 'reporter': ProductPathReporter, 'facade': None},
    PowerSupply: {'interface': IPowerSupplyInfo, 'info': PowerSupplyInfo, 'reporter': None, 'facade': None},
    TemperatureSensor: {'interface': ITemperatureSensorInfo, 'info': TemperatureSensorInfo, 'reporter': None, 'facade': None},
    OSComponent: {'interface': IComponentInfo, 'info': ComponentInfo, 'reporter': None, 'facade': None},
    FileSystem: {'interface': IFileSystemInfo, 'info': FileSystemInfo, 'reporter': None, 'facade': None},
    IpInterface: {'interface': IIpInterfaceInfo, 'info': IpInterfaceInfo, 'reporter': InterfacePathReporter, 'facade': None},
    IpRouteEntry: {'interface': IIpRouteEntryInfo, 'info': IpRouteEntryInfo, 'reporter': None, 'facade': None},
    OSProcess: {'interface': IOSProcessInfo, 'info': OSProcessInfo, 'reporter': ProcessPathReporter, 'facade': ProcessFacade},
    Service: {'interface': IServiceInfo, 'info': ServiceInfo, 'reporter': ServicePathReporter, 'facade': ServiceFacade},
    IpService: {'interface': IIpServiceInfo, 'info': IpServiceInfo, 'reporter': ServicePathReporter, 'facade': ServiceFacade},
    WinService: {'interface': IWinServiceInfo, 'info': WinServiceInfo, 'reporter': ServicePathReporter, 'facade': ServiceFacade},
    }

@property
def get_instance_class(ob):
    return ob._types

DeviceFacade._types = ('Products.ZenModel.Device.Device',)
DeviceFacade._instanceClass = get_instance_class

ProcessFacade._types = ('Products.ZenModel.OSProcess.OSProcess',)
ProcessFacade._instanceClass = get_instance_class

ServiceFacade._types = ('Products.ZenModel.Service.Service',)
ServiceFacade._instanceClass = get_instance_class
