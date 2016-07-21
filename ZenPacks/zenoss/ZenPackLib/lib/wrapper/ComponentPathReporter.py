from zope.component import adapts
from zope.interface import implements
from Products.Zuul.catalog.interfaces import IPathReporter
from Products.Zuul.catalog.paths import DefaultPathReporter, relPath
from ..base.ComponentBase import ComponentBase


class ComponentPathReporter(DefaultPathReporter):

    """Global catalog path reporter adapter factory for components."""

    implements(IPathReporter)
    adapts(ComponentBase)

    def getPaths(self):
        paths = super(ComponentPathReporter, self).getPaths()

        for facet in self.context.get_facets():
            rp = relPath(facet, facet.containing_relname)
            paths.extend(rp)

        return paths

