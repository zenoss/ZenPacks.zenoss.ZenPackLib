##############################################################################
#
# Copyright (C) Zenoss, Inc. 2016, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################
from Products.ZenModel.DeviceComponent import DeviceComponent
from Products.ZenModel.ManagedEntity import ManagedEntity
from ..factory.ComponentTypeFactory import ComponentTypeFactory


Component = ComponentTypeFactory('Component', (DeviceComponent, ManagedEntity))
