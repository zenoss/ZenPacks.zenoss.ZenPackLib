#!/usr/bin/env python

##############################################################################
#
# Copyright (C) Zenoss, Inc. 2016, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

"""extra_paths unit tests

This module tests zenpacklib 'extra_paths' and path reporters.

"""

# stdlib Imports
import os
import site
import tempfile

# Zenoss Imports
import Globals  # noqa
from Products.ZenRelations.RelationshipBase import RelationshipBase
from Products.ZenRelations.ToManyContRelationship import ToManyContRelationship
from Products.ZenTestCase.BaseTestCase import BaseTestCase


# zenpacklib Imports
site.addsitedir(os.path.join(os.path.dirname(__file__), '..'))
import zenpacklib

YAML = """
name: ZenPacks.zenoss.SimplevSphere

class_relationships:
  - Endpoint 1:MC Datacenter
  - Endpoint 1:MC Folder
  - Endpoint(vms) 1:MC VirtualMachine
  - ComputeResource(resourcePools) 1:M (owner)ResourcePool
  - Datacenter 1:MC ComputeResource
  - Datacenter 1:MC ResourcePool
  - Datacenter(vms) 1:M VirtualMachine
  - Folder(childEntities) 1:M (containingFolder)VMwareComponent
  - Folder(childFolders) 1:M (parentFolder)Folder
  - ResourcePool(childResourcePools) 1:M (parentResourcePool)ResourcePool
  - ResourcePool(vms) 1:M VirtualMachine

classes:
  Endpoint:
    base: [zenpacklib.Device]

  VMwareComponent:
    base: [zenpacklib.Component]

  Datacenter:
    base: [VMwareComponent]

  ComputeResource:
    base: [VMwareComponent]

  Cluster:
    base: [ComputeResource]

  Folder:
    base: [VMwareComponent]

  ResourcePool:
    base: [VMwareComponent]
    extra_paths:
      # pools are reachable from all of their parents
      - ['(parentResourcePool)+']

  VirtualMachine:
    base: [VMwareComponent]
    extra_paths:
      - ['resourcePool', 'owner']  # from cluster or standalone
      - ['resourcePool', '(parentResourcePool)+']   # from all parent resource pools, recursively.

"""


def spec_from_string(s):
    with tempfile.NamedTemporaryFile() as f:
        f.write(s.strip())
        f.flush()
        return zenpacklib.load_yaml(f.name)


# When a manually-created python object is first added to its container, we
# need to reload it, as its in-memory representation is changed.
def addContained(object, relname, target):
    rel = getattr(object, relname)

    # contained via a relationship
    if isinstance(rel, ToManyContRelationship):
        rel._setObject(target.id, target)
        return rel._getOb(target.id)

    elif isinstance(rel, RelationshipBase):
        rel.addRelation(target)
        return rel._getOb(target.id)

    # contained via a property
    else:
        # note: in this scenario, you must have the target object's ID the same
        #       as the relationship from the parent object.

        assert(relname == target.id)
        object._setObject(target.id, target)
        return getattr(object, relname)


def addNonContained(object, relname, target):
    rel = getattr(object, relname)
    rel.addRelation(target)
    return target


class TestExtraPaths(BaseTestCase):

    """Specs test suite."""

    def afterSetUp(self):
        super(TestExtraPaths, self).afterSetUp()

        self.dmd.REQUEST = None

        # Create standard objects the ZenPack relies on.
        self.dmd.Devices.createOrganizer('/SimplevSphere')
        self.dmd.Devices.SimplevSphere._setProperty('zPythonClass', 'ZenPacks.zenoss.SimplevSphere.Endpoint')

        # Load the YAML
        self.CFG = spec_from_string(YAML)

        # And create the model.
        self._create_device()

    def _create_device(self):
        # endpoint (device)
        ep = self.dmd.Devices.SimplevSphere.createInstance('testdevice')

        # Datacenter
        from ZenPacks.zenoss.SimplevSphere.Datacenter import Datacenter
        datacenter = Datacenter("Datacenter")
        datacenter = addContained(ep, "datacenters", datacenter)  # link into endpoin

        # Create a couple of nested folders
        from ZenPacks.zenoss.SimplevSphere.Folder import Folder
        folder_top = Folder("Folder-Top")
        folder_top = addContained(ep, "folders", folder_top)

        folder_child = Folder("Folder-Child")
        folder_child = addContained(ep, "folders", folder_child)
        folder_child = addNonContained(folder_top, "childFolders", folder_child)

        # A cluster
        from ZenPacks.zenoss.SimplevSphere.Cluster import Cluster
        cluster = Cluster("Cluster")
        cluster = addContained(datacenter, "computeResources", cluster)  # link into DC
        cluster = addNonContained(folder_top, "childEntities", cluster)  # link into folder

        # And a couple of nested resource pools
        from ZenPacks.zenoss.SimplevSphere.ResourcePool import ResourcePool
        cluster_rp = ResourcePool("ResourcePool-Top")
        cluster_rp = addContained(datacenter, "resourcePools", cluster_rp)
        cluster_rp = addNonContained(cluster, "resourcePools", cluster_rp)
        cluster = addNonContained(cluster_rp, "owner", cluster)

        sub_rp = ResourcePool("ResourcePool-Child")
        sub_rp = addContained(datacenter, "resourcePools", sub_rp)
        sub_rp = addNonContained(cluster_rp, "childResourcePools", sub_rp)
        cluster = addNonContained(sub_rp, "owner", cluster)

        # VMs
        from ZenPacks.zenoss.SimplevSphere.VirtualMachine import VirtualMachine

        # One at the top level
        vm1 = VirtualMachine("VirtualMachine-1")
        vm1 = addContained(ep, "vms", vm1)
        vm1 = addNonContained(datacenter, "vms", vm1)
        vm1 = addNonContained(folder_top, "childEntities", vm1)
        vm1 = addNonContained(cluster_rp, "vms", vm1)

        # One in both a subfolder and a subresource pool
        vm2 = VirtualMachine("VirtualMachine-2")
        vm2 = addContained(ep, "vms", vm2)
        vm2 = addNonContained(datacenter, "vms", vm2)
        vm2 = addNonContained(folder_child, "childEntities", vm2)
        vm2 = addNonContained(sub_rp, "vms", vm2)

        # Make available to tests
        self.endpoint = ep
        self.vm1 = vm1
        self.vm2 = vm2

    def testVirtualMachinePathsTopLevelDirect(self):
        vm1_facet_ids = sorted([x.id for x in self.vm1.get_facets()])
        for id_ in ['Datacenter', 'Folder-Top', 'ResourcePool-Top']:
            self.assertIn(id_, vm1_facet_ids)

    def testVirtualMachinePathsTopLevelExtra(self):
        vm1_facet_ids = sorted([x.id for x in self.vm1.get_facets()])
        for id_ in ['Cluster']:
            self.assertIn(id_, vm1_facet_ids)

    def testVirtualMachinePathsChildLevelDirect(self):
        vm2_facet_ids = sorted([x.id for x in self.vm2.get_facets()])
        for id_ in ['Datacenter', 'Folder-Child', 'ResourcePool-Child']:
            self.assertIn(id_, vm2_facet_ids)

    def testVirtualMachinePathsChildLevelExtra(self):
        # thanks to extra_paths, VMs are now reachable from the cluster.
        vm2_facet_ids = sorted([x.id for x in self.vm2.get_facets()])
        for id_ in ['Cluster']:
            self.assertIn(id_, vm2_facet_ids)

    def testResourcePoolPathsTopLevelDirect(self):
        cluster_rp = self.vm1.resourcePool()
        rp_facet_ids = sorted([x.id for x in cluster_rp.get_facets()])
        for id_ in ['Cluster']:
            self.assertIn(id_, rp_facet_ids)

    def testResourcePoolPathsTopLevelExtra(self):
        # No change, on a top-level resource pool.
        pass

    def testResourcePoolPathsChildLevelDirect(self):
        child_rp = self.vm2.resourcePool()
        rp_facet_ids = sorted([x.id for x in child_rp.get_facets()])
        for id_ in ['Cluster']:
            self.assertIn(id_, rp_facet_ids)

    def testResourcePoolPathsChildLevelExtra(self):
        # But for sub-resource pools. they are now also reachable from any
        # of their parents.
        child_rp = self.vm2.resourcePool()
        rp_facet_ids = sorted([x.id for x in child_rp.get_facets()])
        for id_ in ['ResourcePool-Top']:
            self.assertIn(id_, rp_facet_ids)


def test_suite():
    """Return test suite for this module."""
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestExtraPaths))
    return suite


if __name__ == "__main__":
    from zope.testrunner.runner import Runner
    runner = Runner(found_suites=[test_suite()])
    runner.run()
