##############################################################################
#
# Copyright (C) Zenoss, Inc. 2016, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################
from .ModelTypeFactory import ModelTypeFactory
from ..base.DeviceBase import DeviceBase


def DeviceTypeFactory(name, bases):
    """Return a "ZenPackified" device class given bases tuple."""
    all_bases = (DeviceBase,) + bases

    device_type = ModelTypeFactory(name, all_bases)

    def index_object(self, idxs=None, noips=False):
        for base in all_bases:
            if hasattr(base, 'index_object'):
                try:
                    base.index_object(self, idxs=idxs, noips=noips)
                except TypeError:
                    base.index_object(self)

    device_type.index_object = index_object

    return device_type
