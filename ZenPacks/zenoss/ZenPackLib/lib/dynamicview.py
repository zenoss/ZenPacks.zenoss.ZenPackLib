import collections
from zope.interface import implements
from zope.component import adapts
from .utils import LOG


from ZenPacks.zenoss.DynamicView import BaseRelation, BaseGroup
from ZenPacks.zenoss.DynamicView import TAG_ALL
from ZenPacks.zenoss.DynamicView.interfaces import IRelatable, IRelationsProvider
from ZenPacks.zenoss.DynamicView.interfaces import IGroupMappingProvider
from ZenPacks.zenoss.DynamicView.model.adapters import BaseRelatable
from ZenPacks.zenoss.DynamicView.model.adapters import BaseRelationsProvider

class DynamicViewRelatable(BaseRelatable):
    """Generic DynamicView Relatable adapter (IRelatable)

    Places object into a group based upon the class name.
    """

    implements(IRelatable)

    @property
    def id(self):
        return self._adapted.getPrimaryId()

    @property
    def name(self):
        return self._adapted.titleOrId()

    @property
    def tags(self):
        return set([self._adapted.meta_type])

    @property
    def group(self):
        data = self._adapted.getDynamicViewGroup()
        if data:
            return data.get('name', 'Unknown')

    @property
    def group_data(self):
        return self._adapted.getDynamicViewGroup()

class DynamicViewGroupMappingProvider(object):
    """Generic DynamicView IGroupMappingProvider adapter.

    All group information is gathered from the adapted model object.

    """

    implements(IGroupMappingProvider)
    adapts(DynamicViewRelatable)

    def __init__(self, adapted):
        self._adapted = adapted

    def getGroup(self, viewName):
        group = self._adapted
        entity = group._adapted

        if viewName not in entity.dynamicview_views:
            return

        data = self._adapted.group_data
        if data:
            return BaseGroup(
                name=data.get('name', 'Unknown'),
                weight=data.get('weight', 999),
                type=data.get('type', 'Unknown'),
                icon=data.get('icon', '/zport/dmd/img/icons/noicon.png'))

class DynamicViewRelationsProvider(BaseRelationsProvider):
    """Generic DynamicView RelationsProvider subscription adapter (IRelationsProvider)

    Creates impact relationships by introspecting the adapted object's
    impacted_by and impacts properties.

    Note that these impact relationships will also be exposed through to
    impact, so it is not necessary to activate both
    ImpactRelationshipDataProvider and DynamicViewRelatable /
    DynamicViewRelationsProvider for a given model class.
    """
    implements(IRelationsProvider)

    def relations(self, type=TAG_ALL):
        target = IRelatable(self._adapted)
        relations = getattr(self._adapted, 'dynamicview_relations', {})

        # Group methods by type to allow easy tagging of multiple types
        # per yielded relation. This allows supporting the special TAG_ALL
        # type without duplicating work or relations.
        types_by_methodname = collections.defaultdict(set)
        if type == TAG_ALL:
            for ltype, lmethodnames in relations.items():
                for lmethodname in lmethodnames:
                    types_by_methodname[lmethodname].add(ltype)
        else:
            for lmethodname in relations.get(type, []):
                types_by_methodname[lmethodname].add(type)

        for methodname, type_set in types_by_methodname.items():
            for remote in self.get_remote_relatables(methodname):
                yield BaseRelation(target, remote, list(type_set))

    def get_remote_relatables(self, methodname):
        """Generate object relatables returned by adapted.methodname()."""
        method = getattr(self._adapted, methodname, None)
        if not method or not callable(method):
            LOG.warning(
                "no %r relationship or method for %r",
                methodname,
                self._adapted.meta_type)

            return

        r = method()
        if not r:
            return

        try:
            for obj in r:
                yield IRelatable(obj)

        except TypeError:
            yield IRelatable(r)

