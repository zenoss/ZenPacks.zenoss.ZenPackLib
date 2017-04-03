##############################################################################
#
# Copyright (C) Zenoss, Inc. 2016, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################
from zope.component import adapts
from zope.interface import implements
from Products.Zuul.catalog.interfaces import IPathReporter
from Products.Zuul.catalog.paths import (
     DefaultPathReporter,
     DevicePathReporter,
     ServicePathReporter as ServicePathReporterBase,
     InterfacePathReporter as InterfacePathReporterBase,
     ProcessPathReporter as ProcessPathReporterBase,
     ProductPathReporter as ProductPathReporterBase,
     relPath
     )

from ..base.ComponentBase import ComponentBase
from ..base.Component import (
     HWComponent,
     IpInterface,
     OSProcess,
     Service,
)


class ComponentPathMixIn(DefaultPathReporter):
    """Global catalog path reporter override"""
    implements(IPathReporter)

    def getPaths(self):
        paths = super(ComponentPathMixIn, self).getPaths()

        for facet in self.context.get_facets():
            rp = relPath(facet, facet.containing_relname)
            paths.extend(rp)

        return paths


class ComponentPathReporter(ComponentPathMixIn):
    """Global catalog path reporter adapter factory for basic components."""
    adapts(ComponentBase)


class ProductPathReporter(ComponentPathMixIn, ProductPathReporterBase):
    """"""
    adapts(HWComponent)


class InterfacePathReporter(ComponentPathMixIn, InterfacePathReporterBase):
    """"""
    adapts(IpInterface)


class ProcessPathReporter(ComponentPathMixIn, ProcessPathReporterBase):
    """"""
    adapts(OSProcess)

class ServicePathReporter(ComponentPathMixIn, ServicePathReporterBase):
    """"""
    adapts(Service)

