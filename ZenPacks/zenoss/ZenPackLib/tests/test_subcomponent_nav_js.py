#!/usr/bin/env python

##############################################################################
#
# Copyright (C) Zenoss, Inc. 2016, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

""" Test subcomponent_nav_js_snippet

    Validate fix for ZEN-25847
        ZPL creating doubled number of subpanels for same-named relations

"""
# Zenoss Imports
import Globals  # noqa
from Products.ZenUtils.Utils import unused
unused(Globals)

# stdlib Imports
from Products.ZenTestCase.BaseTestCase import BaseTestCase
# zenpacklib Imports
from ZenPacks.zenoss.ZenPackLib.tests.ZPLTestHarness import ZPLTestHarness


YAML_DOC = """name: ZenPacks.zenoss.vSphere
class_relationships:
  - Endpoint 1:MC Datacenter
  - Endpoint 1:MC Folder
  - Endpoint 1:1 (r_endpoint)RootFolder
  - Endpoint(vms) 1:MC VirtualMachine
  - ComputeResource(resourcePools) 1:M (owner)ResourcePool
  - Cluster(hosts) 1:M HostSystem
  - Datacenter 1:MC ComputeResource
  - Datacenter 1:MC ResourcePool
  - Datacenter(hosts) 1:MC HostSystem
  - Datacenter(vms) 1:M VirtualMachine
  - Datacenter 1:MC Network
  - Datacenter(dvSwitches) 1:MC DistributedVirtualSwitch
  - Datacenter 1:MC Datastore
  - Datacenter 1:1 HostFolder
  - Datacenter(vmFolder) 1:1 VMFolder
  - Datacenter 1:1 HostFolder
  - Datacenter 1:1 NetworkFolder
  - Datacenter 1:1 DatastoreFolder
  - Datastore(attachedVms) M:M VirtualMachine
  - Datastore(attachedHostSystems) M:M HostSystem
  - Datastore(luns) M:M LUN
  - DistributedVirtualSwitch(portgroups) 1:M (dvSwitch)DistributedVirtualPortgroup
  - DistributedVirtualSwitch(hosts) M:M HostSystem(dvSwitches)
  - Folder(childEntities) 1:M (containingFolder)VMwareEntity
  - Folder(childFolders) 1:M (parentFolder)Folder
  - HostSystem(vms) 1:M (host)VirtualMachine
  - HostSystem 1:1 (host)Standalone
  - HostSystem 1:MC (host)Pnic
  - HostSystem(luns) 1:MC (host)LUN
  - LUN(rdms) 1:M (lun)RDM
  - Network(attachedVms) M:M VirtualMachine
  - Network(attachedVnics) 1:M Vnic
  - VirtualMachine(rdms) 1:MC (vm)RDM
  - VirtualMachine(vnics) 1:MC (vm)Vnic
  - ResourcePool(childResourcePools) 1:M (parentResourcePool)ResourcePool
  - ResourcePool(vms) 1:M VirtualMachine
classes:
  # Note that the class order is in some cases significant, because
  # one class's .py file may do an import from another, and so they need
  # to already have been processed for that to work under current versions
  # of zenpacklib, which process this file in one pass.
  Endpoint:
    base: [zenpacklib.Device]
    meta_type: vSphereEndpoint
    label: vSphere Endpoint
  VMwareEntity:
    base: [zenpacklib.Component]
    meta_type: vSphereEntity
    relationships:
      containingFolder:
        grid_display: false
  VMwareComponent:
    base: [VMwareEntity]
    meta_type: vSphereComponent
  ComputeResource:
    base: [VMwareComponent]
    meta_type: vSphereComputeResource
    filter_display: false
    properties:
      numEffectiveHosts:
        type: int
        default: 0
        label: Effective Host Count
        grid_display: false
        order: 1.32
      numHosts:
        type: int
        default: 0
        label: Host Count
        grid_display: false
        order: 1.35
      numCpuCores:
        type: int
        default: 0
        label: CPU Core Count
        grid_display: false
        order: 1.42
      numCpuThreads:
        type: int
        default: 0
        label: CPU Thread Count
        grid_display: false
        order: 1.45
      effectiveCpu:
        type: int
        default: 0
        label: Effective CPU
        grid_display: false
        order: 1.52
      totalCpu:
        type: int
        default: 0
        label: Total CPU
        grid_display: false
        order: 1.55
      effectiveMemory:
        type: int
        default: 0
        label: Effective Memory
        order: 1.62
        grid_display: false
        renderer: Zenoss.render.bytesString
      totalMemory:
        type: int
        default: 0
        label: Total Memory
        order: 1.65
        renderer: Zenoss.render.bytesString
        grid_display: false
      overallStatus:
        type: string
        label: Overall Status
        api_only: true
        api_backendtype: method
        grid_display: false
      resourcePools_combined:
        label: Resource Pools
        api_only: true
        api_backendtype: method
        renderer: Zenoss.render.vsphere_resourcePools_combined
        order: 1.2
        details_display: false
        label_width: 80
      hosts_combined:
        label: Hosts
        api_only: true
        api_backendtype: method
        renderer: Zenoss.render.vsphere_hosts_combined
        order: 1.3
        details_display: false
        label_width: 50
      cores_combined:
        label: Cores
        api_only: true
        api_backendtype: method
        renderer: Zenoss.render.vsphere_cores_combined
        order: 1.4
        details_display: false
        label_width: 50
      cpu_combined:
        label: CPU
        api_only: true
        api_backendtype: method
        renderer: Zenoss.render.vsphere_cpu_combined
        order: 1.5
        details_display: false
        label_width: 145
      memory_combined:
        label: Memory
        api_only: true
        api_backendtype: method
        renderer: Zenoss.render.vsphere_memory_combined
        order: 1.6
        details_display: false
        label_width: 130
    relationships:
      datacenter:
        order: 1.1
        label_width: 140
      resourcePools:
        grid_display: false
  Cluster:
    base: [ComputeResource]
    meta_type: vSphereCluster
    label: Cluster
    relationships:
      hosts:
        grid_display: false
  DistributedVirtualPortgroup:
    base: [Network]
    meta_type: vSphereDistributedVirtualPortgroup
    label: dvPortgroup
    properties:
      keyUuid:
        type: string
        default: ""
        label: Key UUID
        grid_display: false
      nsx_vSwitch:
        label: NSX Virtual Switch
        api_only: true
        api_backendtype: method
        type: entity
        renderer: Zenoss.render.zenpacklib_ZenPacks_zenoss_vSphere_entityTypeLinkFromGrid
        label_width: 140
        grid_display: false
    relationships:
      dvSwitch:
        order: 1.2
        label_width: 140
  DistributedVirtualSwitch:
    base: [VMwareComponent]
    meta_type: vSphereDistributedVirtualSwitch
    label: dvSwitch
    plural_label: dvSwitches
    properties:
      dvsUUID:
        type: string
        label: UUID
        grid_display: false
      switchType:
        type: string
        label: Type
        label_width: 150
    relationships:
      portgroups:
        grid_display: false
      hosts:
        label_width: 55
  Folder:
    base: [VMwareEntity]
    meta_type: vSphereFolder
    label: Folder
  DatastoreFolder:
    base: [Folder]
    meta_type: vSphereDatastoreFolder
    label: Datastore Folder
  HostFolder:
    base: [Folder]
    meta_type: vSphereHostFolder
    label: Host Folder
  NetworkFolder:
    base: [Folder]
    meta_type: vSphereNetworkFolder
    label: Network Folder
  RootFolder:
    base: [Folder]
    meta_type: vSphereRootFolder
    label: Root Folder
  VMFolder:
    base: [Folder]
    meta_type: vSphereVMFolder
    label: VM Folder
  Pnic:
    base: [VMwareComponent]
    meta_type: vSpherePnic
    label: pNIC
    properties:
      macaddress:
        type: string
        label: MAC Address
        label_width: 115
        order: 1.2
      linkStatus:
        type: string
        label: Link Status
        label_width: 50
        renderer: Zenoss.render.vsphere_ManagedEntityStatus
      linkSpeed:
        # Mbit
        type: string
        label: Link Speed
        grid_display: false
        details_display: true
      linkDuplex:
        type: string
        label: Link Duplex
        grid_display: false
        details_display: true
      linkSpeed_combined:
        label: Link Speed
        api_only: true
        api_backendtype: method
        renderer: Zenoss.render.vsphere_linkSpeed_combined
        order: 1.3
        label_width: 70
        details_display: false
    relationships:
      host:
        order: 1.1
  LUN:
    base: [VMwareComponent]
    meta_type: vSphereLUN
    label: LUN
    properties:
      diskName:
        type: string
        label: LUN Name
        grid_display: false
      lunId:
        type: string
        label: LUN ID
        order: 1.2
      diskKey:
        type: string
        label: LUN Key
        grid_display: false
      operStatus:
        type: string
        label: Operational Status
        grid_display: false
      deviceName:
        type: string
        label: DeviceName
        grid_display: false
      lunType:
        type: string
        label: Type
        grid_display: false
      vendor:
        type: string
        label: Vendor
        grid_display: false
      model:
        type: string
        label: Model
        grid_display: false
      lunUUID:
        type: string
        label: LUN UUID
        grid_display: false
      storageProvider:
        label: Storage Provider
        api_only: true
        api_backendtype: method
        type: entity
        renderer: Zenoss.render.zenpacklib_ZenPacks_zenoss_vSphere_entityTypeLinkFromGrid
        label_width: 140
        order: 1.3
    relationships:
      host:
        label_width: 140
        order: 1.1
      datastores:
        grid_display: false
      rdms:
        grid_display: false
  HostSystem:
    base: [VMwareComponent]
    meta_type: vSphereHostSystem
    label: Host
    properties:
      hostname:
        type: string
        label: Hostname
        grid_display: false
      manageIps:
        type: lines
        default: []
        label: Management IP Addresses
        grid_display: false
      totalMemory:
        type: int
        label: Total Memory
        order: 1.3
        label_width: 75
        renderer: Zenoss.render.bytesString
      connectionState:
        type: string
        label: Connection State
        grid_display: false
      powerState:
        type: string
        label: Power State
        grid_display: false
      inMaintenanceMode:
        type: boolean
        label: In Maintenance Mode
        grid_display: false
      hypervisorVersion:
        type: string
        label: Hypervisor Version
        short_label: Version
        order: 1.2
        label_width: 200
        grid_display: false
      hardwareVendor:
        type: string
        label: Vendor
        grid_display: false
      hardwareModel:
        type: string
        label: Model
        grid_display: false
      hardwareUUID:
        type: string
        label: UUID
        grid_display: false
      cpuModel:
        type: string
        label: CPU Model
        grid_display: false
      cpuMhz:
        type: int
        label: CPU MHz
        grid_display: false
        renderer: Zenoss.render.vsphere_cpuSpeed
      numCpuPkgs:
        type: int
        label: CPU Package Count
        grid_display: false
      numCpuCores:
        type: int
        label: CPU Core Count
        grid_display: false
      cluster_or_standalone:
        label: Cluster
        api_only: true
        api_backendtype: method
        type: entity
        renderer: Zenoss.render.zenpacklib_ZenPacks_zenoss_vSphere_entityTypeLinkFromGrid
        label_width: 140
      powered_vm_count:
        label: Powered On VM Count
        api_only: true
        api_backendtype: method
        grid_display: false
      suspended_vm_count:
        label: Suspended VM Count
        api_only: true
        api_backendtype: method
        grid_display: false
      unpowered_vm_count:
        label: Powered Off VM Count
        api_only: true
        api_backendtype: method
        grid_display: false
      vms_combined:
        label: VMs
        api_only: true
        api_backendtype: method
        renderer: Zenoss.render.vsphere_vms_combined
        order: 1.4
        label_width: 110
        details_display: false
      overallStatus:
        type: string
        label: Overall Status
        api_only: true
        api_backendtype: method
        grid_display: false
      vxlanInstallDate:
        type: string
        label: VXLAN VIB Install Date
        grid_display: false
      vxlanVersion:
        type: string
        label: VXLAN VIB Version
        grid_display: false
      vsipInstallDate:
        type: string
        label: VSIP VIB Install Date
        grid_display: false
      vsipVersion:
        type: string
        label: VSIP VIB Version
        grid_display: false
      dvfilterSwitchSecurityInstallDate:
        type: string
        label: DVFilter Switch Security VIB Install Date
        grid_display: false
      dvfilterSwitchSecurityVersion:
        type: string
        label: DVFilter Switch Security VIB Version
        grid_display: false
      vdsConfigured:
        type: boolean
        label: VDS Config Present
        grid_display: false
    relationships:
      datacenter:
        label_width: 140
        order: 1.1
      datastores:
        grid_display: false
      cluster:
        grid_display: false
      standalone:
        grid_display: false
      pnics:
        grid_display: false
      vms:
        grid_display: false
      luns:
        grid_display: false
      dvSwitches:
        grid_display: false
  Datastore:
    base: [VMwareComponent]
    meta_type: vSphereDatastore
    label: Datastore
    properties:
      type:
        type: string
        label: Datastore Type
        short_label: Type
        order: 1.2
      storageProvider:
        label: Provider
        api_only: true
        api_backendtype: method
        type: entity
        renderer: Zenoss.render.zenpacklib_ZenPacks_zenoss_vSphere_entityTypeLinkFromGrid
        order: 1.3
      capacity:
        type: int
        label: Capacity
        order: 1.4
        renderer: Zenoss.render.bytesString
        default: 0
      used_pct:
        label: Used Percent
        short_label: Used
        api_only: true
        api_backendtype: method
        renderer: Zenoss.render.vsphere_percent
        order: 1.5
        label_width: 55
      allocated_pct:
        label: Allocated
        api_only: true
        api_backendtype: method
        renderer: Zenoss.render.vsphere_percent
        order: 1.6
        label_width: 75
      freeSpace:
        type: int
        label: Free Space
        grid_display: false
        renderer: Zenoss.render.bytesString
        default: 0
      uncommitted:
        type: int
        label: Uncommitted Space
        grid_display: false
        renderer: Zenoss.render.bytesString
        default: 0
      uncommitted_pct:
        type: int
        label: Uncommitted Percent
        short_label: Uncommitted
        grid_display: false
        renderer: Zenoss.render.vsphere_percent
      url:
        type: string
        label: URL
        grid_display: false
      nasRemoteHost:
        type: string
        label: NAS Remote Host
        grid_display: false
      nasRemotePath:
        type: string
        label: NAS Remote Path
        grid_display: false
      nasUserName:
        type: string
        label: NAS Username
        grid_display: false
      localPath:
        type: string
        label: Local Filesystem Path
        grid_display: false
      utilizationPercent:
        api_only: true
        api_backendtype: method
        grid_display: false
        details_display: false
      utilizationDisplay:
        api_only: true
        api_backendtype: method
        grid_display: false
        details_display: false
    relationships:
      datacenter:
        order: 1.1
        label_width: 140
      luns:
        grid_display: false
      attachedVms:
        grid_display: false
      attachedHostSystems:
        grid_display: false
  Network:
    base: [VMwareComponent]
    meta_type: vSphereNetwork
    label: Network
    properties:
      accessible:
        type: boolean
        label: Accessible
        order: 1.5
        label_width: 70
      ipPoolName:
        type: string
        label: IP Pool Name
        short_label: IP Pool
        order: 1.3
        label_width: 140
    relationships:
      datacenter:
        order: 1.1
        label_width: 140
      attachedVms:
        order: 1.4
        label_width: 55
      attachedVnics:
        grid_display: false
  RDM:
    base: [VMwareComponent]
    meta_type: vSphereRDM
    label: RDM
    properties:
      lunUuid:
        type: string
        label: LUN UUID
        grid_display: false
      host:
        label: Host
        api_only: true
        api_backendtype: method
        type: entity
        label_width: 140
        order: 1.3
      storageProvider:
        label: Storage Provider
        api_only: true
        api_backendtype: method
        type: entity
        renderer: Zenoss.render.zenpacklib_ZenPacks_zenoss_vSphere_entityTypeLinkFromGrid
        label_width: 140
        order: 1.3
    relationships:
      vm:
        order: 1.1
        label_width: 140
      lun:
        order: 1.2
        label_width: 140
  ResourcePool:
    base: [VMwareComponent]
    meta_type: vSphereResourcePool
    label: Resource Pool
    extra_paths:
      # pools are reachable from all of their parents
      - ['(parentResourcePool)+']
    properties:
      cpuLimit:
        type: int
        label: CPU Limit
        renderer: Zenoss.render.vsphere_cpuLimit
        label_width: 75
        order: 1.3
      cpuReservation:
        type: int
        label: CPU Reservation
        renderer: Zenoss.render.vsphere_cpuReservation
        label_width: 80
        order: 1.4
      memoryLimit:
        type: int
        label: Memory Limit
        renderer: Zenoss.render.vsphere_memoryLimit
        label_width: 75
        order: 1.5
      memoryReservation:
        type: int
        label: Memory Reservation
        renderer: Zenoss.render.vsphere_memoryReservation
        label_width: 90
        order: 1.6
      vm_count:
        type: int
        label: VMs
        api_only: true
        api_backendtype: method
        label_width: 35
        order: 1.7
      overallStatus:
        type: string
        label: Overall Status
        api_only: true
        api_backendtype: method
        grid_display: false
    relationships:
      datacenter:
        order: 1.1
        label_width: 125
      owner:
        label: Owner
        order: 1.2
        label_width: 125
      vms:
        grid_display: false
        details_display: false
      parentResourcePool:
        grid_display: false
        label: "Parent Resource Pool"
      childResourcePools:
        grid_display: false
        label: "Child Resource Pools"
  Standalone:
    base: [ComputeResource]
    meta_type: vSphereStandalone
    label: Standalone Resource
    relationships:
      host:
        grid_display: false
  VirtualApp:
    base: [ResourcePool]
    meta_type: vSphereVirtualApp
    label: vApp
    relationships:
      owner:
        grid_display: false
      # Not currently working (ZEN-24302)
      parentResourcePool:
        grid_display: false
        label: "Parent vApp"
      childResourcePools:
        grid_display: false
        label: "Child vApps"
  Datacenter:
    base: [VMwareComponent]
    meta_type: vSphereDatacenter
    label: Datacenter
    properties:
      resourcePools_combined:
        label: Resource Pools
        api_only: true
        api_backendtype: method
        renderer: Zenoss.render.vsphere_resourcePools_combined
        order: 1.2
        label_width: 80
        details_display: false
      computeResources_combined:
        label: Resources
        api_only: true
        api_backendtype: method
        renderer: Zenoss.render.vsphere_computeResources_combined
        order: 1.3
        label_width: 80
        details_display: false
      networks_combined:
        label: Networks
        api_only: true
        api_backendtype: method
        renderer: Zenoss.render.vsphere_networks_combined
        order: 1.6
        label_width: 75
        details_display: false
      vapp_count:
        label: vApp Count
        api_only: true
        api_backendtype: method
        grid_display: false
      cluster_count:
        label: Cluster Count
        api_only: true
        api_backendtype: method
        grid_display: false
      standalone_count:
        label: Standalone Resource Count
        api_only: true
        api_backendtype: method
        grid_display: false
      network_count:
        label: Network Count
        api_only: true
        api_backendtype: method
        grid_display: false
      dvportgroup_count:
        label: dvPortgroup Count
        api_only: true
        api_backendtype: method
        grid_display: false
    relationships:
      hosts:
        order: 1.4
        label_width: 55
      vms:
        order: 1.5
        label_width: 65
      dvSwitches:
        order: 1.7
        label_width: 80
      computeResources:
        grid_display: false
        details_display: false
      resourcePools:
        grid_display: false
      networks:
        grid_display: false
      datastores:
        grid_display: false
      hostFolder:
        grid_display: false
        details_display: false
      vmFolder:
        grid_display: false
        details_display: false
      networkFolder:
        grid_display: false
        details_display: false
      datastoreFolder:
        grid_display: false
        details_display: false
  Vnic:
    base: [VMwareComponent]
    meta_type: vSphereVnic
    label: vNIC
    properties:
      macaddress:
        type: string
        label: MAC Address
        label_width: 115
        order: 1.3
      deviceKey:
        type: string
        grid_display: false
        details_display: false
    relationships:
      vm:
        label_width: 220
        order: 1.1
      network:
        label_width: 140
        order: 1.2
  VirtualMachine:
    base: [VMwareComponent]
    meta_type: vSphereVirtualMachine
    label: Virtual Machine
    short_label: VM
    plural_label: VMs
    extra_paths:
      - ['resourcePool', 'owner']  # from cluster or standalone
      - ['resourcePool', '(parentResourcePool)+']   # from all parent resource pools, recursively.
    properties:
      overallStatus:
        type: string
        label: Overall Status
        api_only: true
        api_backendtype: method
        grid_display: false
      connectionState:
        type: string
        default: ''
        label: Connection State
        grid_display: false
      guestname:
        type: string
        default: ''
        label: Guest Name
        grid_display: false
      vmUUID:
        type: string
        label: UUID
        grid_display: false
      isTemplate:
        type: boolean
        label: Is Template
        grid_display: false
      macAddresses:
        type: lines
        details_display: false
        grid_display: false
      macAddressesStr:
        type: lines
        label: MAC Addresses
        api_only: true
        api_backendtype: method
        grid_display: false
      numCPU:
        type: int
        label: CPU Count
        short_label: CPUs
        label_width: 30
        order: 1.4
      guestDevices:
        type: entity
        label: Guest Device
        api_only: true
        api_backendtype: method
        order: 1.5
      memory:
        type: int
        label: Memory
        renderer: Zenoss.render.bytesString
        order: 1.6
      osType:
        type: string
        default: ''
        label: Operating System Type
        grid_display: false
      powerState:
        type: string
        default: ''
        label: Power State
        short_label: Power
        renderer: Zenoss.render.vsphere_PowerState
        label_width: 40
        order: 1.7
      toolsVersion:
        type: int
        default: 0
        grid_display: false
        details_display: false
      toolsVersionStr:
        type: string
        api_only: true
        api_backendtype: method
        label: VMWare Tools Version
        grid_display: false
      toolsStatus:
        type: string
        default: ''
        label: VMware Tools Status
        grid_display: false
      hardwareVersion:
        type: string
        default: ''
        label: Hardware Version
        grid_display: false
      storageCommitted:
        type: int
        label: Committed Storage
        renderer: Zenoss.render.bytesString
        grid_display: false
      storageUncommitted:
        type: int
        label: Uncommitted Storage
        renderer: Zenoss.render.bytesString
        grid_display: false
      nsx_edge:
        type: entity
        api_only: true
        api_backendtype: method
        label: NSX Edge
        grid_display: false
      nsx_controller:
        type: entity
        api_only: true
        api_backendtype: method
        label: NSX Controller
        grid_display: false
    relationships:
      datacenter:
        order: 1.1
        label_width: 140
      resourcePool:
        order: 1.2
      host:
        order: 1.3
      datastores:
        grid_display: false
      rdms:
        grid_display: false
      vnics:
        grid_display: false
      networks:
        grid_display: false
"""

expected_rp = "Zenoss.nav.appendTo('Component', [{\n    id: 'component_vsphereresourcepool_child_resource_pools',\n    text: _t('Child Resource Pools'),\n    xtype: 'vSphereResourcePoolPanel',\n    subComponentGridPanel: true,\n    filterNav: function(navpanel) {\n        switch (navpanel.refOwner.componentType) {\n            case 'vSphereResourcePool': return true;\n            default: return false;\n        }\n    },\n    setContext: function(uid) {\n        ZC.vSphereResourcePoolPanel.superclass.setContext.apply(this, [uid]);\n    }\n}]);\nZenoss.nav.appendTo('Component', [{\n    id: 'component_vsphereresourcepool_resource_pools',\n    text: _t('Resource Pools'),\n    xtype: 'vSphereResourcePoolPanel',\n    subComponentGridPanel: true,\n    filterNav: function(navpanel) {\n        switch (navpanel.refOwner.componentType) {\n            case 'vSphereVMFolder': return true;\n            case 'vSphereNetworkFolder': return true;\n            case 'vSphereCluster': return true;\n            case 'vSphereRootFolder': return true;\n            case 'vSphereHostFolder': return true;\n            case 'vSphereStandalone': return true;\n            case 'vSphereComputeResource': return true;\n            case 'vSphereFolder': return true;\n            case 'vSphereDatastoreFolder': return true;\n            case 'vSphereDatacenter': return true;\n            default: return false;\n        }\n    },\n    setContext: function(uid) {\n        ZC.vSphereResourcePoolPanel.superclass.setContext.apply(this, [uid]);\n    }\n}]);\n"
expected_va = "Zenoss.nav.appendTo('Component', [{\n    id: 'component_vspherevirtualapp_child_vapps',\n    text: _t('Child vApps'),\n    xtype: 'vSphereVirtualAppPanel',\n    subComponentGridPanel: true,\n    filterNav: function(navpanel) {\n        switch (navpanel.refOwner.componentType) {\n            case 'vSphereVirtualApp': return true;\n            default: return false;\n        }\n    },\n    setContext: function(uid) {\n        ZC.vSphereVirtualAppPanel.superclass.setContext.apply(this, [uid]);\n    }\n}]);\nZenoss.nav.appendTo('Component', [{\n    id: 'component_vspherevirtualapp_vapps',\n    text: _t('vApps'),\n    xtype: 'vSphereVirtualAppPanel',\n    subComponentGridPanel: true,\n    filterNav: function(navpanel) {\n        switch (navpanel.refOwner.componentType) {\n            case 'vSphereVMFolder': return true;\n            case 'vSphereNetworkFolder': return true;\n            case 'vSphereCluster': return true;\n            case 'vSphereRootFolder': return true;\n            case 'vSphereHostFolder': return true;\n            case 'vSphereStandalone': return true;\n            case 'vSphereComputeResource': return true;\n            case 'vSphereFolder': return true;\n            case 'vSphereDatastoreFolder': return true;\n            case 'vSphereDatacenter': return true;\n            default: return false;\n        }\n    },\n    setContext: function(uid) {\n        ZC.vSphereVirtualAppPanel.superclass.setContext.apply(this, [uid]);\n    }\n}]);\n"

class TestSubComponentNavJS(BaseTestCase):
    """Test catalog creation for specs"""

    def test_nav_js(self):
        ''''''
        z = ZPLTestHarness(YAML_DOC)
        if z.zenpack_installed():
            cls = z.cfg.classes.get('ResourcePool')
            self.assertEquals(cls.subcomponent_nav_js_snippet,
                              expected_rp,
                              'Unexpected subcomponent_nav_js_snippet for ResourcePool')

            cls = z.cfg.classes.get('VirtualApp')
            self.assertEquals(cls.subcomponent_nav_js_snippet,
                              expected_va,
                              'Unexpected subcomponent_nav_js_snippet for ResourcePool')
        else:
            print "\nSkipping TestSubComponentNavJS since ZenPacks.zenoss.vSphere not installed"

def test_suite():
    """Return test suite for this module."""
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestSubComponentNavJS))
    return suite

if __name__ == "__main__":
    from zope.testrunner.runner import Runner
    runner = Runner(found_suites=[test_suite()])
    runner.run()
