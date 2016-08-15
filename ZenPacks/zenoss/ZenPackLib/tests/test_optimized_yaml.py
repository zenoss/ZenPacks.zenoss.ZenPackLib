#!/usr/bin/env python

##############################################################################
#
# Copyright (C) Zenoss, Inc. 2016, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

""" Multi-YAML import load

Tests YAML loading from multiple files

"""
# stdlib Imports
import os
import site
import tempfile
import traceback
from Products.ZenTestCase.BaseTestCase import BaseTestCase

# zenpacklib Imports
from ZenPacks.zenoss.ZenPackLib import zenpacklib
import yaml
from ZenPacks.zenoss.ZenPackLib.lib.helpers.Dumper import Dumper
from ZenPacks.zenoss.ZenPackLib.lib.helpers.Loader import Loader
from ZenPacks.zenoss.ZenPackLib.lib.helpers.utils import optimize_yaml, compare_zenpackspecs


# Zenoss Imports
import Globals  # noqa
from Products.ZenUtils.Utils import unused
unused(Globals)


YAML_WHOLE = """
name: ZenPacks.zenoss.Microsoft.Windows
zProperties:
  DEFAULTS:
    category: Windows
  zWinRMUser:
    default: ''
  zWinRMPassword:
    type: password
    default: ''
  zWinRMUser:
    default: ''
  zWinRMServerName:
    default: ''
  zWinRMPort:
    default: '5985'
  zDBInstances:
    type: instancecredentials
    default: '[{"instance": "MSSQLSERVER", "user": "", "passwd": ""}]'
    category: 'Misc'
  zWinKDC:
    default: ''
  zWinKeyTabFilePath:
    default: ''
  zWinScheme:
    default: 'http'
  zWinPerfmonInterval:
    default: 300
  zWinTrustedRealm:
    default: ''
  zWinTrustedKDC:
    default: ''


class_relationships:
  - ZenPacks.zenoss.Microsoft.Windows.OperatingSystem.OperatingSystem(winrmservices) 1:MC (os)WinService
  - ZenPacks.zenoss.Microsoft.Windows.OperatingSystem.OperatingSystem(winrmiis) 1:MC (os)WinIIS
  - ZenPacks.zenoss.Microsoft.Windows.OperatingSystem.OperatingSystem(winsqlinstances) 1:MC (os)WinSQLInstance
  - ZenPacks.zenoss.Microsoft.Windows.OperatingSystem.OperatingSystem(clusterservices) 1:MC (os)ClusterService
  - ZenPacks.zenoss.Microsoft.Windows.OperatingSystem.OperatingSystem(clusternetworks) 1:MC (os)ClusterNetwork
  - ZenPacks.zenoss.Microsoft.Windows.OperatingSystem.OperatingSystem(clusternodes) 1:MC (os)ClusterNode
  - ClusterService(clusterresources) 1:MC (clusterservice)ClusterResource
  - ClusterNode(clusterdisks) 1:MC (clusternode)ClusterDisk
  - ClusterNode(clusterinterfaces) 1:MC (clusternode)ClusterInterface
  - WinSQLInstance(backups) 1:MC (winsqlinstance)WinSQLBackup
  - WinSQLInstance(databases) 1:MC (winsqlinstance)WinSQLDatabase
  - WinSQLInstance(jobs) 1:MC (winsqlinstance)WinSQLJob
  - TeamInterface(teaminterfaces) 1:M (teaminterface)Interface


classes:
  DEFAULTS:
    base: [BaseComponent]

  BaseDevice:
    base: [zenpacklib.Device]
  
  BaseComponent:
    base: [zenpacklib.Component, Products.ZenModel.OSComponent.OSComponent]

  ClusterObject:
    base: [BaseComponent]
    properties:
      DEFAULTS:
        grid_display: false
        default: None
      getState:
        label: State
        api_only: true
        api_backendtype: method
        grid_display: true
        order: 7
      domain:
        label: Domain
        default: ''

  ClusterNodeObject:
    base: [ClusterObject]
    properties:
      DEFAULTS:
        grid_display: false
        default: None
      ownernode:
        label: Owner Node
      get_host_device:
        label: Cluster Node
        grid_display: true
        api_only: true
        api_backendtype: method
        type: entity
        order: 1

  Device:
    base: [BaseDevice]
    label: Device
    properties:
      clusterdevices:
        label: Cluster Devices
        default: ''
      sqlhostname:
        label: SQL Host Name
        default: None
      msexchangeversion:
        label: MS Exchange Version
        default: None
      ip_and_hostname:
        default: None
      domain_controller:
        label: MS Exchange Version
        type: boolean
        default: false
    impacts:
      - all_filesystems
      - all_processes
      - all_ipservices
      - all_cpus
      - all_interfaces
      - all_clusterservices
      - all_clusternodes
      - all_clusternetworks
      - all_winservices
      - all_hyperv
      - all_winsqlinstances
      - all_winrmiis
    impacted_by: []
    dynamicview_views: [service_view]
    dynamicview_relations:
      impacts:
        - all_filesystems
        - all_processes
        - all_ipservices
        - all_cpus
        - all_interfaces
        - all_clusterservices
        - all_clusternodes
        - all_clusternetworks
        - all_winservices
        - all_hyperv
        - all_winsqlinstances
        - all_winrmiis
      impacted_by: []

  ClusterDevice:
    base: [Device]
    properties:
      clusterhostdevices:
        label: Cluster Host Devices
        default: ''
      GUID:
        label: GUID
        default: None
      creatingdc:
        label: Creating DC
        default: None
    impacts:
      - all_filesystems
      - all_processes
      - all_ipservices
      - all_cpus
      - all_interfaces
      - all_clusterservices
      - all_clusternodes
      - all_clusternetworks
      - all_winservices
      - all_hyperv
      - all_winsqlinstances
      - all_winrmiis
    impacted_by: [all_clusterhosts]
    dynamicview_views: [service_view]
    dynamicview_relations:
      impacts:
        - all_filesystems
        - all_processes
        - all_ipservices
        - all_cpus
        - all_interfaces
        - all_clusterservices
        - all_clusternodes
        - all_clusternetworks
        - all_winservices
        - all_hyperv
        - all_winsqlinstances
        - all_winrmiis
      impacted_by: [all_clusterhosts]

  ClusterResource:
    label: Cluster Resource
    base: [ClusterNodeObject]
    order: 5
    properties:
      DEFAULTS:
        grid_display: false
        default: None
      description:
        label: Description
      ownergroup:
        label: Owner Group
        type: boolean
        default: False
    monitoring_templates: [ClusterResource]
    impacts: []
    impacted_by: [device, clusterservice]
    dynamicview_views: [service_view]
    dynamicview_relations:
      impacts: []
      impacted_by: [clusterservice]

  ClusterService:
    label: Cluster Service
    base: [ClusterNodeObject]
    order: 6
    properties:
      DEFAULTS:
        grid_display: false
        default: None
      description:
        label: Description
      coregroup:
        label: Core Group
        type: boolean
        default: False
      priority:
        label: Priority
        type: int
        default: 0
    monitoring_templates: [ClusterService]
    impacts: [clusterresources]
    impacted_by: [device]
    dynamicview_views: [service_view]
    dynamicview_relations:
      impacts: [clusterresources]
      impacted_by: [device]
    relationships:
      DEFAULTS:
        grid_display: false
        details_display: false
      os: {}

  ClusterNode:
    label: Cluster Node
    base: [ClusterNodeObject]
    order: 1
    properties:
      DEFAULTS:
        grid_display: false
        default: None
      assignedvote:
        label: Assigned Vote
        grid_display: true
        order: 2
      currentvote:
        label: Current Vote
        grid_display: true
        order: 3
    monitoring_templates: [ClusterNode]
    impacts: []
    impacted_by: [clusterdisks, clusterinterfaces]
    dynamicview_views: [service_view]
    dynamicview_relations:
      impacts: []
      impacted_by: [clusterdisks, clusterinterfaces]
    relationships:
      DEFAULTS:
        grid_display: false
        details_display: false
      os: {}

  ClusterDisk:
    label: Cluster Disk
    base: [ClusterNodeObject]
    order: 2
    properties:
      DEFAULTS:
        grid_display: false
        default: None
      volumepath:
        label: Volume Path
      disknumber:
        label: Disk Number
      partitionnumber:
        label: Partition Number
      size:
        label: Size
        grid_display: true
        order: 5
      freespace:
        label: Free Space
        grid_display: true
        order: 6
      assignedto:
        label: Assigned To
        grid_display: true
        order: 2
    monitoring_templates: [ClusterDisk]
    impacts: [clusternode]
    impacted_by: []
    dynamicview_views: [service_view]
    dynamicview_relations:
      impacts: [clusternode]
      impacted_by: []

  ClusterNetwork:
    label: Cluster Network
    base: [ClusterObject]
    order: 4
    properties:
      DEFAULTS:
        grid_display: false
        default: None
      description:
        label: Description
        grid_display: true
        order: 3
      role:
        label: Cluster Use
        type: boolean
        default: False
        grid_display: true
        order: 2
    monitoring_templates: [ClusterNetwork]
    impacts: []
    impacted_by: [device]
    dynamicview_views: [service_view]
    dynamicview_relations:
      impacts: []
      impacted_by: [device]
    relationships:
      DEFAULTS:
        grid_display: false
        details_display: false
      os: {}

  ClusterInterface:
    label: Cluster Interface
    base: [ClusterObject]
    order: 3
    properties:
      DEFAULTS:
        grid_display: false
        default: None
      node:
        label: Node
      get_network:
        label: Network
        grid_display: true
        api_only: true
        api_backendtype: method
        type: entity
        order: 2
      network:
        label: Network
      ipaddresses:
        label: IP Addresses
        grid_display: true
        order: 3
      adapter:
        label: Adapter
    monitoring_templates: [ClusterInterface]
    impacts: [clusternode]
    impacted_by: []
    dynamicview_views: [service_view]
    dynamicview_relations:
      impacts: [clusternode]
      impacted_by: []

  CPU:
    label: Processor
    base: [zenpacklib.Component, Products.ZenModel.CPU.CPU]
    properties:
      DEFAULTS:
        grid_display: false
        default: 0
        type: int
      description:
        label: Description
        type: string
        default: None
      cores:
        label: Cores
      cores:
        label: Cores
      threads:
        label: Threads
      cacheSpeedL2:
        label: L2 Cache Speed
      cacheSpeedL3:
        label: L3 Cache Speed
      cacheSizeL3:
        label: L3 Cache Size
        grid_display: true
    monitoring_templates: [CPU]
    impacts: []
    impacted_by: [device]
    dynamicview_views: [service_view]
    dynamicview_relations:
      impacts: []
      impacted_by: [device]

  FileSystem:
    label: File System
    base: [BaseComponent, Products.ZenModel.FileSystem.FileSystem]
    properties:
      DEFAULTS:
        details_display: false
        grid_display: false
      mediatype:
        label: Media Type
        default: None
      drivetype:
        label: Drive Type
        default: None
      total_bytes:
        type: long
        label: Total Bytes
        default: 0
    monitoring_templates: [FileSystem]
    impacts: []
    impacted_by: [device]
    dynamicview_views: [service_view]
    dynamicview_relations:
      impacts: []
      impacted_by: [device]

  Interface:
    label: Interface
    base: [BaseComponent, Products.ZenModel.IpInterface.IpInterface]
    monitoring_templates: [ethernetCsmacd]
    impacts: []
    impacted_by: [device]
    dynamicview_views: [service_view]
    dynamicview_relations:
      impacts: []
      impacted_by: [device]
    relationships:
      DEFAULTS:
        grid_display: true
        details_display: false
      teaminterface: {}

  OSProcess:
    label: Process
    base: [BaseComponent, Products.ZenModel.OSProcess.OSProcess]
    monitoring_templates: [OSProcess]
    properties:
      supports_WorkingSetPrivate:
        label: Supports Private Working Set
        type: boolean
        default: False
    impacts: []
    impacted_by: [device]
    dynamicview_views: [service_view]
    dynamicview_relations:
      impacts: []
      impacted_by: [device]

  TeamInterface:
    label: Team Interface
    base: [BaseComponent, Products.ZenModel.IpInterface.IpInterface]
    monitoring_templates: [TeamInterface]
    properties:
      DEFAULTS:
        grid_display: false
        default: None
      description:
        label: Description
      get_niccount:
        type: int
        label: NIC Count
        default: 0
        api_only: true
        api_backendtype: method
    impacts: []
    impacted_by: [device]
    dynamicview_views: [service_view]
    dynamicview_relations:
      impacts: []
      impacted_by: [device]

  WinIIS:
    label: IIS Site
    plural_label: IIS Sites
    properties:
      DEFAULTS:
        grid_display: false
        default: None
      sitename:
        label: Site Name
      apppool:
        label: Application Pool
        grid_display: true
        order: 2
      caption:
        label: Caption
      status:
        label: Status
        grid_display: true
        order: 3
      statusname:
        label: Status Name
      iis_version:
        label: Version
        type: int
    monitoring_templates: [IISSites]
    impacts: []
    impacted_by: [device]
    dynamicview_views: [service_view]
    dynamicview_relations:
      impacts: []
      impacted_by: [device]
    relationships:
      DEFAULTS:
        grid_display: false
        details_display: false
      os: {}

  WinSQLBackup:
    label: SQL Backup
    order: 13
    properties:
      DEFAULTS:
        grid_display: false
        default: None
      instancename:
        label: Instance Name
      devicetype:
        label: Device Type
        grid_display: true
        order: 1
      physicallocation:
        label: Physical Location
      status:
        label: Status
    monitoring_templates: [WinBackupDevice]
    impacts: []
    impacted_by:  [winsqlinstance]
    dynamicview_views: [service_view]
    dynamicview_relations:
      impacts: []
      impacted_by:  [winsqlinstance]

  WinSQLDatabase:
    label: SQL Database
    order: 11
    properties:
      DEFAULTS:
        grid_display: false
        default: None
      instancename:
        label: Instance Name
      version:
        label: Version
      owner:
        label: Owner
        grid_display: true
        order: 1
      lastbackupdate:
        label: Last Backup
      lastlogbackupdate:
        label: Last Log Backup
      isaccessible:
        label: Accessible
      collation:
        label: Collation
      createdate:
        label: Created On
      defaultfilegroup:
        label: File Group
      primaryfilepath:
        label: File Path
      systemobject:
        label: System Object
      recoverymodel:
        label: Recovery Model
      status:
        label: Status
        grid_display: true
        order: 3
      cluster_node_server:
        label: Cluster Node Server
    monitoring_templates: [WinDatabase]
    impacts: []
    impacted_by: [winsqlinstance]
    dynamicview_views: [service_view]
    dynamicview_relations:
      impacts: []
      impacted_by: [winsqlinstance]

  WinSQLInstance:
    label: SQL Instance
    order: 10
    properties:
      DEFAULTS:
        grid_display: false
        default: None
      instancename:
        label: Instance Name
        grid_display: true
      backupdevices:
        label: Backup Devices
      roles:
        label: Roles
      cluster_node_server:
        label: Cluster Node Server
    monitoring_templates: [WinDBInstance]
    impacts: [backups, databases, jobs]
    impacted_by: [device]
    dynamicview_views: [service_view]
    dynamicview_relations:
      impacts: [backups, databases, jobs]
      impacted_by: [device]
    relationships:
      DEFAULTS:
        grid_display: false
        details_display: false
      os: {}

  WinSQLJob:
    label: SQL Job
    order: 12
    properties:
      DEFAULTS:
        grid_display: false
        #default: None
      instancename:
        label: Instance Name
      jobid:
        label: Job ID
      enabled:
        label: Enabled
        grid_display: true
        order: 1
      description:
        label: Description
      username:
        label: User
        #default: None
      datecreated:
        label: Date Created
      cluster_node_server:
        label: Cluster Node Server
    monitoring_templates: [WinSQLJob]
    impacts: []
    impacted_by: [winsqlinstance]
    dynamicview_views: [service_view]
    dynamicview_relations:
      impacts: []
      impacted_by: [winsqlinstance]
"""



class TestOptimizedYAML(BaseTestCase):
    """Test optimized YAML"""

    def test_optimized_yaml(self):
        ''''''
        # reference yaml (all in one

        cfg = zenpacklib.load_yaml(YAML_WHOLE)
        orig_yaml = yaml.dump(cfg.specparams, Dumper=Dumper)
        new_yaml = optimize_yaml(YAML_WHOLE)

        compare_equals = compare_zenpackspecs(orig_yaml, new_yaml)

        self.assertTrue(compare_equals, 
                        'YAML Optimization test failed')


def test_suite():
    """Return test suite for this module."""
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestOptimizedYAML))
    return suite

if __name__ == "__main__":
    from zope.testrunner.runner import Runner
    runner = Runner(found_suites=[test_suite()])
    runner.run()
