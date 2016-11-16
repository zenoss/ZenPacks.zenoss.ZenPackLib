##############################################################################
#
# Copyright (C) Zenoss, Inc. 2016, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################
from .SpecParams import SpecParams
from ..spec.LinkProviderSpec import LinkProviderSpec


class LinkProviderSpecParams(SpecParams, LinkProviderSpec):
    def __init__(self,
                 zenpack_spec,
                 link_title,
                 global_search=False,
                 link_class='Products.ZenModel.Device.Device',
                 device_class=None,
                 catalog='device',
                 queries=None,
                 **kwargs):
        SpecParams.__init__(self, **kwargs)
        self.link_title = link_title
        self.global_search = global_search
        self.link_class = link_class
        self.device_class = device_class
        self.catalog = catalog
        self.queries = queries
