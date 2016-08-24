##############################################################################
#
# Copyright (C) Zenoss, Inc. 2016, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################
from zope.interface import implements
from zope.component import adapts
from Products.ZenUtils.guid.interfaces import IGlobalIdentifier
from .helpers.ZenPackLibLog import DEFAULTLOG
from .base.ComponentBase import ComponentBase
from .base.DeviceBase import DeviceBase
from ZenPacks.zenoss.Impact.impactd.relations import ImpactEdge
from ZenPacks.zenoss.Impact.impactd.interfaces import IRelationshipDataProvider


class ImpactRelationshipDataProvider(object):

    """Generic Impact RelationshipDataProvider adapter factory.

    Implements IRelationshipDataProvider.

    Creates impact relationships by introspecting the adapted object's
    impacted_by and impacts properties.

    """

    implements(IRelationshipDataProvider)
    adapts(DeviceBase, ComponentBase)

    def __init__(self, adapted):
        self.adapted = adapted

    @property
    def relationship_provider(self):
        """Return string indicating from where generated edges came.

        Required by IRelationshipDataProvider.

        """
        return getattr(self.adapted, 'zenpack_name', 'ZenPack')

    def belongsInImpactGraph(self):
        """Return True so generated edges will show in impact graph.

        Required by IRelationshipDataProvider.

        """
        return True

    def getEdges(self):
        """Generate ImpactEdge instances for adapted object.

        Required by IRelationshipDataProvider.

        """
        provider = self.relationship_provider
        myguid = IGlobalIdentifier(self.adapted).getGUID()
        impacted_by = getattr(self.adapted, 'impacted_by', [])
        if impacted_by:
            for methodname in impacted_by:
                for impactor_guid in self.get_remote_guids(methodname):
                    yield ImpactEdge(impactor_guid, myguid, provider)

        impacts = getattr(self.adapted, 'impacts', [])
        if impacts:
            for methodname in impacts:
                for impactee_guid in self.get_remote_guids(methodname):
                    yield ImpactEdge(myguid, impactee_guid, provider)

    def get_remote_guids(self, methodname):
        """Generate object GUIDs returned by adapted.methodname()."""
        method = getattr(self.adapted, methodname, None)
        if not method or not callable(method):
            DEFAULTLOG.warning(
                "no %r relationship or method for %r",
                methodname,
                self.adapted.meta_type)

            return

        r = method()
        if not r:
            return

        try:
            for obj in r:
                yield IGlobalIdentifier(obj).getGUID()

        except TypeError:
            yield IGlobalIdentifier(r).getGUID()
