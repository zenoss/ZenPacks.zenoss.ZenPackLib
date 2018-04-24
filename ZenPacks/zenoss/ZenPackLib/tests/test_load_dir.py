#!/usr/bin/env python

##############################################################################
#
# Copyright (C) Zenoss, Inc. 2018, all rights reserved.
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

# zenpacklib Imports
from ZenPacks.zenoss.ZenPackLib import zenpacklib
import yaml
from ZenPacks.zenoss.ZenPackLib.lib.base.ZenPack import ZenPack
from ZenPacks.zenoss.ZenPackLib.lib.helpers.Dumper import Dumper
from ZenPacks.zenoss.ZenPackLib.lib.helpers.utils import compare_zenpackspecs

# Zenoss Imports
import Globals  # noqa
from Products.ZenUtils.Utils import unused
unused(Globals)
from Products.ZenTestCase.BaseTestCase import BaseTestCase


YAML_WHOLE = """
name: ZenPacks.zenoss.Microsoft.Azure
zProperties:
  DEFAULTS:
    category: Microsoft Azure
  zAzureEAAccessKey:
    default: ''
  zAzureEAEnrollmentNumber:
    default: ''
  zAzureEABillingCostThreshold:
    type: multilinethreshold
    default: '{}'
  zAzureMonitoringIgnore:
    default: ''


class_relationships:
- AzureSubscription(affinity_groups) 1:MC (subscription)AzureAffinityGroup
- AzureSubscription(hosted_services) 1:MC (subscription)AzureHostedService
- AzureHostedService(instances) 1:MC (hosted_service)AzureInstance
- AzureInstance(disks) 1:MC (instance)AzureDisk
- AzureSubscription(storage_services) 1:MC (subscription)AzureStorageService
- AzureStorageService(queues) 1:MC (storage_service)AzureQueue
- AzureStorageService(tables) 1:MC (storage_service)AzureTable
- AzureStorageService(containers) 1:MC (storage_service)AzureContainer
- AzureContainer(blobs) 1:MC (container)AzureBlob
- AzureSubscription(web_spaces) 1:MC (subscription)AzureWebSpace
- AzureWebSpace(sites) 1:MC (web_space)AzureSite
- AzureSubscription(virtual_network_sites) 1:MC (subscription)AzureVirtualNetworkSite
- AzureVirtualNetworkSite(subnets) 1:MC (virtual_network_site)AzureSubnet
- AzureSubscription(locations) 1:MC (subscription)AzureLocation


classes:
  DEFAULTS:
    base: [AzureComponent]

  AzureComponent:
    base: [zenpacklib.Component]

  SubscriptionObject:
    base: [AzureComponent]
    properties:
      getSubscription:
        label: Subscription
        grid_display: true
        api_only: true
        api_backendtype: method
        type: entity
        order: 1
        content_width: 90

  AzureServiceObject:
    base: [AzureComponent]
    properties:
      service_status:
        label: Service Status
        grid_display: true
        content_width: 90
        order: 2

  AzureStatusObject:
    base: [AzureComponent]
    properties:
      status:
        label: Status
        api_only: true
        api_backendtype: method
        grid_display: true
        renderer: Zenoss.render.azure_pingStatus
        content_width: 60
        order: 10

  AzureSubscription:
    base: [zenpacklib.Device]
    label: Subscription
    properties:
      DEFAULTS:
        grid_display: false
      subscription_id:
        label: Subscription ID
      cert_file:
        label: Cert File
      service_status:
        label: Service Status
      max_core_count:
        label: Max Core Count
      max_storage_accounts:
        label: Max Storage Accounts
      max_hosted_services:
        label: Max Hosted Services
      max_virtual_network_sites:
        label: Max Virtual Network Sites
      max_local_network_sites:
        label: Max Local Network Sites
      max_dns_servers:
        label: Max DNS Servers
      current_core_count:
        label: Current Core Count
      current_hosted_services:
        label: Current Hosted Services
      current_storage_accounts:
        label: Current Storage Accounts
      model_time:
        label: Model Time
      first_seen:
        label: First Seen
        api_only: true
        api_backendtype: method
      last_change:
        label: Last Change
        api_only: true
        api_backendtype: method
    dynamicview_group: Subscription
    dynamicview_relations:
      impacts: [hosted_services, storage_services, web_spaces, virtual_network_sites, locations, affinity_groups]

  AzureAffinityGroup:
    base: [SubscriptionObject, AzureStatusObject]
    label: Affinity Group
    properties:
      DEFAULTS:
        grid_display: false
      label:
        label: Label
      description:
        label: Description
        grid_display: true
        order: 2
      location:
        label: Location
        grid_display: true
        order: 3
      capabilities:
        label: Capabilities
        grid_display: true
        order: 4
      # prob should replace these 2 with relations
      hosted_services:
        label: Hosted Services
      storage_services:
        label: Storage Services
    dynamicview_relations:
      impacted_by: [subscription]
    monitoring_templates: [AzureAffinityGroup]

  AzureHostedService:
    base: [SubscriptionObject,AzureServiceObject]
    label: Hosted Service
    properties:
      DEFAULTS:
        grid_display: false
      url:
        label: URL
      production_status:
        label: Production Status
        grid_display: true
        renderer: Zenoss.render.azure_pingStatus
        order: 7
        content_width: 90
      staging_status:
        label: Staging Status
        grid_display: true
        renderer: Zenoss.render.azure_pingStatus
        order: 8
        content_width: 80
      location:
        label: Location
        grid_display: true
        renderer: Zenoss.render.azure_entityLinkFromGrid
        order: 4
      affinity_group:
        label: Affinity Group
        grid_display: true
        renderer: Zenoss.render.azure_entityLinkFromGrid
        order: 3
      date_created:
        label: Created
        #grid_display: true
        order: 5
        content_width: 80
      date_last_modified:
        label: Last Modified
        #grid_display: true
        order: 6
        content_width: 90
    dynamicview_relations:
      impacts: [instances]
      impacted_by: [subscription]
    monitoring_templates: [AzureHostedService]

  AzureStorageService:
    base: [SubscriptionObject, AzureStatusObject, AzureServiceObject]
    label: Storage Service
    properties:
      DEFAULTS:
        grid_display: false
      url:
        label: URL
      location:
        label: Location
        grid_display: true
        order: 4
        renderer: Zenoss.render.azure_entityLinkFromGrid
        content_width: 100
      affinity_group:
        label: Affinity Group
        grid_display: true
        order: 3
        renderer: Zenoss.render.azure_entityLinkFromGrid
        content_width: 100
    relationships:
      DEFAULTS:
        grid_display: false
      tables: {
      }
      queues: {
      }
      containers: {
      }
    dynamicview_relations:
      impacts: [containers, tables, queues]
      impacted_by: [subscription]
    monitoring_templates: [AzureStorageService]

  AzureWebSpace:
    base: [SubscriptionObject, AzureStatusObject, AzureServiceObject]
    label: Web Space
    properties:
      DEFAULTS:
        grid_display: false
      plan:
        label: Plan
      geo_location:
        label: Geo Location
      number_of_workers:
        label: Workers
      availability_state:
        label: Availability State
        order: 3
        grid_display: true
      compute_mode:
        label: Compute Mode
    relationships:
      DEFAULTS:
        grid_display: false
      sites: {
      }
    dynamicview_relations:
      impacts: [sites]
      impacted_by: [subscription]
    monitoring_templates: [AzureWebSpace]

  AzureVirtualNetworkSite:
    base: [SubscriptionObject, AzureStatusObject]
    label: Virtual Network Site
    properties:
      DEFAULTS:
        grid_display: false
      label:
        label: Label
        grid_display: true
      vn_id:
        label: VN ID
        grid_display: true
        order: 2
      affinity_group:
        label: Affinity Group
        grid_display: true
        renderer: Zenoss.render.azure_entityLinkFromGrid
        order: 3
      state:
        label: State
        grid_display: true
        order: 4
    dynamicview_relations:
      impacts: [subnets]
      impacted_by: [subscription]
    monitoring_templates: [AzureVirtualNetworkSite]

  AzureLocation:
    base: [SubscriptionObject, AzureStatusObject]
    label: Location
    dynamicview_relations:
      impacted_by: [subscription]
    monitoring_templates: [AzureLocation]

  AzureInstance:
    base: [SubscriptionObject, AzureStatusObject]
    label: Instance
    properties:
      DEFAULTS:
        grid_display: false
      instance_status:
        label: Instance Status
        grid_display: true
        order: 2
      instance_size:
        label: Instance Size
      ip_address:
        label: IP Address
        grid_display: true
        order: 3
      power_state:
        label: Power State
        grid_display: true
        order: 4
      instance_error_code:
        label: Instance Error Code
      fqdn:
        label: FQDN
    dynamicview_relations:
      impacted_by: [disks, hosted_service]
    monitoring_templates: [AzureInstance]

  AzureBlob:
    label: Blob
    base: [AzureStatusObject]
    properties:
      DEFAULTS:
        grid_display: false
      snapshot:
        label: Snapshot
      url:
        label: URL
      snapshot:
        label: Snapshot
      content_length:
        label: Content Length
        grid_display: true
        order: 2
      content_type:
        label: Content Type
        grid_display: true
        order: 3
      blob_type:
        label: Blob Type
        grid_display: true
        order: 4
      lease_status:
        label: Lease Status
        grid_display: true
        order: 5
      attached:
        label: Attached Status
        grid_display: false
    dynamicview_relations:
      impacted_by: [container]
    monitoring_templates: [AzureBlob]

  AzureContainer:
    base: [SubscriptionObject, AzureStatusObject]
    label: Container
    properties:
      DEFAULTS:
        grid_display: true
      url:
        label: URL
        order: 3
      last_modified:
        label: Last Modified
        order: 2
    dynamicview_relations:
      impacts: [blobs]
      impacted_by: [storage_service]
    monitoring_templates: [AzureContainer]

  AzureDisk:
    base: [SubscriptionObject, AzureStatusObject]
    label: Disk
    properties:
      DEFAULTS:
        grid_display: false
      affinity_group:
        label: Affinity Group
      has_operating_system:
        label: Has Operating System
      is_corrupted:
        label: Is Corrupted
      location:
        label: Location
        grid_display: true
        order: 2
      logical_disk_size_in_gb:
        label: Logical Disk Size In GB
        short_label: Size
        grid_display: true
        order: 4
      label:
        label: Label
      media_link:
        label: Media Link
      os:
        label: OS
        grid_display: true
        order: 3
      source_image_name:
        label: Source Image Name
    dynamicview_relations:
      impacts: [instance]
    monitoring_templates: [AzureDisk]

  AzureQueue:
    base: [SubscriptionObject, AzureStatusObject]
    label: Queue
    properties:
      DEFAULTS:
        grid_display: false
      url:
        label: URL
    dynamicview_relations:
      impacted_by: [subscription, storage_service]
    monitoring_templates: [AzureQueue]

  AzureSite:
    base: [SubscriptionObject, AzureStatusObject]
    label: Site
    properties:
      DEFAULTS:
        grid_display: false
      state:
        label: State
      server_farm:
        label: Server Farm
      owner:
        label: Owner
      availability_state:
        label: Availability State
        grid_display: true
        order: 2
      runtime_availability_state:
        label: Runtime Availability
        #grid_display: true
        #order: 3
      admin_enabled:
        label: Admin Enabled
        grid_display: true
        order: 5
      compute_mode:
        label: Compute Mode
      enabled:
        label: Enabled
      host_names:
        label: Host Names
        #grid_display: true
        #order: 6
        renderer: Zenoss.render.azure_URL
      enabled_host_names:
        label: Enabled Host Names
      self_link:
        label: Self Link
      usage_state:
        label: Usage State
        grid_display: true
        order: 4
    dynamicview_relations:
      impacted_by: [web_space]
    monitoring_templates: [AzureSite]

  AzureSubnet:
    base: [SubscriptionObject, AzureStatusObject]
    label: Subnet
    properties:
      DEFAULTS:
        grid_display: true
      address_prefix:
        label: Address Prefix
        order: 2
    dynamicview_relations:
      impacted_by: [virtual_network_site]
    monitoring_templates: [AzureSubnet]

  AzureTable:
    base: [SubscriptionObject, AzureStatusObject]
    label: Table
    properties:
      DEFAULTS:
        grid_display: false    
    dynamicview_relations:
      impacted_by: [subscription, storage_service]
    monitoring_templates: [AzureTable]


device_classes:
  /Azure:
    remove: true
    zProperties:
      zPythonClass: ZenPacks.zenoss.Microsoft.Azure.AzureSubscription
      zCollectorPlugins:
        - AzureCollector
      zDeviceTemplates:
        - AzureSubscription
    templates:
      AzureAffinityGroup:
        datasources:
          AzureDataSource:
            type: AzureDataSource
            component: ${here/id}
            cycletime: 300
      AzureBlob:
        datasources:
          AzureDataSource:
            type: AzureDataSource
            component: ${here/id}
            cycletime: 1800
      AzureContainer:
        datasources:
          AzureDataSource:
            type: AzureDataSource
            component: ${here/id}
            cycletime: 300
      AzureDisk:
        datasources:
          AzureDataSource:
            type: AzureDataSource
            component: ${here/id}
            cycletime: 300
      AzureHostedService:
        datasources:
          AzureDataSource:
            type: AzureDataSource
            component: ${here/id}
            cycletime: 300
      AzureInstance:
        datasources:
          AzureDataSource:
            type: AzureDataSource
            component: ${here/id}
            cycletime: 300
      AzureSite:
        targetPythonClass: ZenPacks.zenoss.Microsoft.Azure.AzureSite
        datasources:
          AzureDataSource:
            type: AzureDataSource
            component: ${here/id}
            cycletime: 300
            datapoints:
              bytes_received:
                aliases: {bytes_received: null}
              bytes_sent:
                aliases: {bytes_sent: null}
              cpu_time:
                aliases: {cpu_time: null}
              filesystem_storage:
                aliases: {filesystem_storage: null}
              local_bytes_read:
                aliases: {local_bytes_read: null}
              local_bytes_written:
                aliases: {local_bytes_written: null}
              memory_usage:
                aliases: {memory_usage: null}
        graphs:
          Bytes:
            units: Bytes
            graphpoints:
              bytes_received:
                dpName: AzureDataSource_bytes_received
                legend: Received
              bytes_sent:
                dpName: AzureDataSource_bytes_sent
                legend: Sent
              local_bytes_read:
                dpName: AzureDataSource_local_bytes_read
                legend: Local bytes read
              local_bytes_written:
                dpName: AzureDataSource_local_bytes_written
                legend: Local bytes written
          CPU time:
            units: Miliseconds
            graphpoints:
              cpu_time:
                dpName: AzureDataSource_cpu_time
                legend: CPU time
          Filesystem:
            units: Bytes
            graphpoints:
              filesystem_storage:
                dpName: AzureDataSource_filesystem_storage
                legend: Storage
          Memory:
            units: Bytes
            graphpoints:
              memory_usage:
                dpName: AzureDataSource_memory_usage
                legend: Usage
      AzureStorageService:
        datasources:
          AzureDataSource:
            type: AzureDataSource
            component: ${here/id}
            cycletime: 300
            datapoints:
              blobs_capacity:
                aliases: {blobs_capacity: null}
              blobs_container_count:
                aliases: {blobs_container_count: null}
              blobs_object_count:
                aliases: {blobs_object_count: null}
        graphs:
          Blobs:
            units: Count
            miny: 0
            maxy: 0
            graphpoints:
              blobs_container_count:
                dpName: AzureDataSource_blobs_container_count
                legend: Container count
              blobs_object_count:
                dpName: AzureDataSource_blobs_object_count
                legend: Object count
          Blobs capacity:
            units: Bytes
            graphpoints:
              blobs_capacity:
                dpName: AzureDataSource_blobs_capacity
                legend: Capacity
      AzureSubnet:
        datasources:
          AzureDataSource:
            type: AzureDataSource
            component: ${here/id}
            cycletime: 300
      AzureSubscription:
        datasources:
          AzureDataSource:
            type: AzureDataSource
            cycletime: 300
            datapoints:
              current_core_count: {}
              current_hosted_services: {}
              current_storage_accounts: {}
              max_core_count: {}
              max_hosted_services: {}
              max_storage_accounts: {}
        graphs:
          Cores:
            units: Cores
            miny: 0
            graphpoints:
              current_core_count:
                dpName: AzureDataSource_current_core_count
                legend: Current core count
              max_core_count:
                dpName: AzureDataSource_max_core_count
                legend: Max core count
          Hosted services:
            units: Hosted services
            miny: 0
            graphpoints:
              current_hosted_services:
                dpName: AzureDataSource_current_hosted_services
                legend: Current hosted services
              max_hosted_services:
                dpName: AzureDataSource_max_hosted_services
                legend: Max hosted services
          Storage accounts:
            units: storage accounts
            miny: 0
            graphpoints:
              current_storage_accounts:
                dpName: AzureDataSource_current_storage_accounts
                legend: Current storage accounts
              max_storage_accounts:
                dpName: AzureDataSource_max_storage_accounts
                legend: Max storage accounts
      AzureVirtualNetworkSite:
        datasources:
          AzureDataSource:
            type: AzureDataSource
            component: ${here/id}
            cycletime: 300
      AzureWebSpace:
        datasources:
          AzureDataSource:
            type: AzureDataSource
            component: ${here/id}
            cycletime: 300

"""



class TestDirectoryLoad(BaseTestCase):
    """Test loading from directory"""


    def test_dir_load(self):
        ''''''
        # reference yaml (all in one
        cfg_whole = zenpacklib.load_yaml(YAML_WHOLE)

        # reference yaml split across multiple files
        fdir = '{}/data/yaml/test_dir_load'.format(os.path.abspath(os.path.dirname(__file__)))
        cfg_dir = zenpacklib.load_yaml(fdir)

        # dump both back to YAML
        whole_yaml = yaml.dump(cfg_whole.specparams, Dumper=Dumper)
        dir_yaml = yaml.dump(cfg_dir.specparams, Dumper=Dumper)

        compare_equals = compare_zenpackspecs(whole_yaml, dir_yaml)

        diff = ZenPack.get_yaml_diff(whole_yaml, dir_yaml)
        self.assertTrue(compare_equals,
                        'YAML Multiple file test failed:\n{}'.format(diff))



def test_suite():
    """Return test suite for this module."""
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestDirectoryLoad))
    return suite

if __name__ == "__main__":
    from zope.testrunner.runner import Runner
    runner = Runner(found_suites=[test_suite()])
    runner.run()