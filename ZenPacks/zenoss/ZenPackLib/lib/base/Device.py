##############################################################################
#
# Copyright (C) Zenoss, Inc. 2016, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################
from Products.ZenModel.Device import Device
from ..factory.DeviceTypeFactory import DeviceTypeFactory


Device = DeviceTypeFactory('Device', (Device,))
