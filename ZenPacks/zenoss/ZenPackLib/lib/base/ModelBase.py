##############################################################################
#
# Copyright (C) Zenoss, Inc. 2016, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################
from .CatalogBase import CatalogBase


class ModelBase(CatalogBase):
    """Base class for ZenPack model classes."""
    
    def getIconPath(self):
        """Return relative URL path for class' icon."""
        return getattr(self, 'icon_url', '/zport/dmd/img/icons/noicon.png')

    def getDynamicViewGroup(self):
        return getattr(self, 'dynamicview_group', None)
