##############################################################################
#
# Copyright (C) Zenoss, Inc. 2016, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

import logging
from .functions import catalog_search

log = logging.getLogger('zen.ZenPackLib')


class DeviceLinkProvider(object):
    """
    Provides links
    """
    queries = ''

    def __init__(self, device):
        self.device = device

    def getExpandedLinks(self):
        links = []
        # Find types that match and return them
        try:
            link_providers = self.device.link_providers
        except Exception:
            log.warn('No link providers defined for device {} in {}'.format(self.device.id,
                                                                            self.device.zenpack_name))
            return links

        for lp_key, link_provider in link_providers.iteritems():
            class_name = '.'.join([self.device.zPythonClass, self.device.__class__.__name__])
            queries = {}
            for key, value in link_provider.queries.iteritems():
                try:
                    # look for attribute of device
                    queries[key] = getattr(self.device, value)
                except AttributeError:
                    # could be a specific value, such as a meta_type
                    queries[key] = value

            # make sure we're looking at the right class and there is at least one query
            if link_provider.link_class == class_name and queries:
                # get the scope, either local to device, global, or local to device class
                if link_provider.global_search:
                    scope = self.device.getDmdRoot('Devices')
                else:
                    try:
                        scope = self.device.getDmdRoot('Devices').getOrganizer(link_provider.device_class)
                    except (KeyError, TypeError, AttributeError):
                        scope = self.device.device()

                # use named catalog
                results = catalog_search(scope, link_provider.catalog, **queries)

                for brain in results:
                    obj = brain.getObject()
                    links.append(
                        '{}: <a href="{}">{}</a>'.format(
                            link_provider.link_title,
                            obj.getPrimaryUrlPath(),
                            obj.titleOrId()
                        )
                    )

        return links
