##############################################################################
#
# Copyright (C) Zenoss, Inc. 2016, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################
from .Spec import Spec

'''
Example

link_providers:
    Cluster Node:
        global_search: False
        link_class: ZenPacks.zenoss.Microsoft.Windows.Device.Device
        catalog: device
        queries:
            - id:clusterhostdevices
    Cluster:
        link_class: ZenPacks.zenoss.Microsoft.Windows.Device.Device
        queries:
            - id:clusterdevices
        device_class: /Server/Microsoft/Cluster
'''


class LinkProviderSpec(Spec):
    """Initialize a LinkProviderClass via Python at install time."""

    def __init__(
            self,
            class_spec,
            link_title,
            global_search=False,
            link_class='ZenPacks.zenoss.ZenPackLib.lib.base.Device.Device',
            device_class=None,
            catalog='device',
            queries=None,
            _source_location=None,
            zplog=None):
        """
            Create a Device Link Provider Specification

            :param global_search: Search global catalog?
            :type global_search: bool
            :param link_class: Class for which this is a provider
            :type link_class: str
            :param device_class: Device class which contains the search catalog
            :type device_class: str
            :param catalog: name of catalog to search.  device, component, etc.
            :type catalog: str
            :param queries: Queries to match on search results in remote:local format.
                    e.g. id:manageIp denotes a match on the remote id with the device's manageIp
            :type queries: list(str)
        """
        super(LinkProviderSpec, self).__init__(_source_location=_source_location)
        if zplog:
            self.LOG = zplog
        self.link_title = link_title
        self.global_search = global_search
        self.link_class = link_class
        self.catalog = catalog
        self.queries = queries
        self.device_class = device_class

    @property
    def queries(self):
        return self._queries

    @queries.setter
    def queries(self, value):
        self._queries = {}
        if not value:
            self.LOG.error('Link provider queries for {} cannot be empty.'.format(self.link_title))
        if not isinstance(value, list):
            self.LOG.warn('Link provider queries must be a list of strings: {}'.format(value))
            return
        for query in value:
            try:
                left, right = query.split(':', 1)
                self._queries[left] = right
            except ValueError:
                self.LOG.warn('Link provider query must be matched pairs.  Discarding "{}"'.format(query))
