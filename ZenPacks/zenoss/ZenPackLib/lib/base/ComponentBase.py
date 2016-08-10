import os
import json
from Products.AdvancedQuery import Eq, Or
from Products.Zuul.decorators import memoize
from Products.Zuul.catalog.events import IndexingEvent
from zope.event import notify
from Products.ZenModel.Device import Device
from Products.ZenModel.DeviceComponent import DeviceComponent
from Products.ZenModel.ZenossSecurity import ZEN_CHANGE_DEVICE
from Products.ZenRelations.RelSchema import ToMany, ToManyCont
from Products.ZenRelations import ToOneRelationship, ToManyContRelationship, ToManyRelationship
from Products.ZenRelations.Exceptions import ZenSchemaError

from .ModelBase import ModelBase
from ..utils import FACET_BLACKLIST
from ..functions import catalog_search


class ComponentBase(ModelBase):

    """First superclass for zenpacklib types created by ComponentTypeFactory.

    Contains attributes that should be standard on all ZenPack Component
    types.

    """
    factory_type_information = ({
        'actions': ({
            'id': 'perfConf',
            'name': 'Template',
            'action': 'objTemplates',
            'permissions': (ZEN_CHANGE_DEVICE,),
            },),
        },)

    _catalogs = {
        'ComponentBase': {
            'indexes': {
                'id': {'type': 'field'},
                }
            }
        }

    def device(self):
        """Return device under which this component/device is contained."""
        obj = self

        for i in xrange(200):
            if isinstance(obj, Device):
                return obj

            try:
                obj = obj.getPrimaryParent()
            except AttributeError:
                # While it is generally not normal to have devicecomponents
                # that are not part of a device, it CAN occur in certain
                # non-error situations, such as when it is in the process of
                # being deleted.  In that case, the DeviceComponentProtobuf
                # (Products.ZenMessaging.queuemessaging.adapters) implementation
                # expects device() to return None, not to throw an exception.
                return None

    def getStatus(self, statClass='/Status'):
        """Return the status number for this component.

        Overridden to default statClass to /Status instead of
        /Status/<self.meta_type>. Current practices do not include using
        a separate event class for each component meta_type. The event
        class plus component field already convey this level of
        information.

        """
        return DeviceComponent.getStatus(self, statClass=statClass)

    def getIdForRelationship(self, relationship):
        """Return id in ToOne relationship or None."""
        obj = relationship()
        if obj:
            return obj.id

    def setIdForRelationship(self, relationship, id_):
        """Update ToOne relationship given relationship and id."""
        old_obj = relationship()

        # Return with no action if the relationship is already correct.
        if (old_obj and old_obj.id == id_) or (not old_obj and not id_):
            return

        # Remove current object from relationship.
        if old_obj:
            relationship.removeRelation()

            # Index old object. It might have a custom path reporter.
            notify(IndexingEvent(old_obj.primaryAq(), 'path', False))

        # If there is no new ID to add, we're done.
        if id_ is None:
            return

        # Find and add new object to relationship.
        for result in catalog_search(self.device(), 'ComponentBase', id=id_):
            try:
                new_obj = result.getObject()
            except Exception as e:
                self.LOG.error("Trying to add relation to non-existent object {}".format(e))
            else:
                relationship.addRelation(new_obj)

            # Index remote object. It might have a custom path reporter.
            notify(IndexingEvent(new_obj.primaryAq(), 'path', False))

            # For componentSearch. Would be nice if we could target
            # idxs=['getAllPaths'], but there's a chance that it won't exist
            # yet.
            new_obj.index_object()
            return

        self.LOG.error("setIdForRelationship ({}): No target found matching id={}".format(relationship, id_))

    def getIdsInRelationship(self, relationship):
        """Return a list of object ids in relationship.

        relationship must be of type ToManyContRelationship or
        ToManyRelationship. Raises ValueError for any other type.

        """
        if isinstance(relationship, ToManyContRelationship):
            return relationship.objectIds()
        elif isinstance(relationship, ToManyRelationship):
            return [x.id for x in relationship.objectValuesGen()]

        try:
            type_name = type(relationship.aq_self).__name__
        except AttributeError:
            type_name = type(relationship).__name__

        raise ValueError(
            "invalid type '%s' for getIdsInRelationship()" % type_name)

    def setIdsInRelationship(self, relationship, ids):
        """Update ToMany relationship given relationship and ids."""
        new_ids = set(ids)
        current_ids = set(o.id for o in relationship.objectValuesGen())
        changed_ids = new_ids.symmetric_difference(current_ids)

        query = Or(*[Eq('id', x) for x in changed_ids])

        obj_map = {}
        for result in catalog_search(self.device(), 'ComponentBase', query):
            try:
                component = result.getObject()
            except Exception as e:
                self.LOG.error("Trying to access non-existent object {}".format(e))
            else:
                obj_map[result.id] = component

        for id_ in new_ids.symmetric_difference(current_ids):
            obj = obj_map.get(id_)
            if not obj:
                self.LOG.error(
                    "setIdsInRelationship ({}): No targets found matching "
                    "id={}".format(relationship, id_))

                continue

            if id_ in new_ids:
                self.LOG.debug("Adding {} to {}".format(obj, relationship))
                relationship.addRelation(obj)

                # Index remote object. It might have a custom path reporter.
                notify(IndexingEvent(obj, 'path', False))
            else:
                self.LOG.debug("Removing {} from {}".format(obj, relationship))
                relationship.removeRelation(obj)

                # If the object was not deleted altogether..
                if not isinstance(relationship, ToManyContRelationship):
                    # Index remote object. It might have a custom path reporter.
                    notify(IndexingEvent(obj, 'path', False))

            # For componentSearch. Would be nice if we could target
            # idxs=['getAllPaths'], but there's a chance that it won't exist
            # yet.
            obj.index_object()

    @property
    def containing_relname(self):
        """Return name of containing relationship."""
        return self.get_containing_relname()

    @memoize
    def get_containing_relname(self):
        """Return name of containing relationship."""
        for relname, relschema in self._relations:
            if issubclass(relschema.remoteType, ToManyCont):
                return relname
        raise ZenSchemaError("%s (%s) has no containing relationship" % (self.__class__.__name__, self))

    @property
    def faceting_relnames(self):
        """Return non-containing relationship names for faceting."""
        return self.get_faceting_relnames()

    @memoize
    def get_faceting_relnames(self):
        """Return non-containing relationship names for faceting."""
        faceting_relnames = []

        for relname, relschema in self._relations:
            if relname in FACET_BLACKLIST:
                continue

            if issubclass(relschema.remoteType, ToMany):
                faceting_relnames.append(relname)

        return faceting_relnames

    def get_facets(self, root=None, streams=None, seen=None, depth=0, path=None, recurse_all=False):
        """Generate non-containing related objects for faceting."""

        if recurse_all:
            # recurse_all is only used for list_paths to show all possible paths
            # from this object to any other object, so in the interest of time
            # and keeping noise to a minimum, don't bother traversing deeper
            # than 15 levels.
            if depth > 15:
                return
        else:
            # in non-recurse_all mode, deep traverals only occur when an
            # extra_paths expression directs it to keep going down a specific
            # path.  It is assumed that this will generally be of limited depth
            # anyway, but just in case, put an absolute limit on it, of the
            # maximum depth supported by zenpacklib's device() method.
            if depth > 200:
                return

        if seen is None:
            seen = set()

        if path is None:
            path = []

        if root is None:
            root = self

        if streams is None:
            streams = getattr(self, '_v_path_pattern_streams', [])

        for relname in self.get_faceting_relnames():
            rel = getattr(self, relname, None)
            if not rel or not callable(rel):
                continue

            relobjs = rel()
            if not relobjs:
                continue

            if isinstance(rel, ToOneRelationship):
                # This is really a single object.
                relobjs = [relobjs]

            relpath = "/".join(path + [relname])

            # Always include directly-related objects.
            for obj in relobjs:
                if (self.id, relname, obj.id) in seen:
                    # avoid a cycle
                    continue

                yield obj
                seen.add((self.id, relname, obj.id))

                # If 'all' mode, just include indirectly-related objects as well, in
                # an unfiltered manner.
                if recurse_all:
                    for facet in obj.get_facets(root=root, seen=seen, path=path, depth=depth+1, recurse_all=True):
                        yield facet

                else:
                    # Otherwise, look at extra_path defined path pattern streams
                    for stream in streams:
                        recurse = any([pattern.match(relpath) for pattern in stream])

                        self.LOG.log(9, "[{}] matching {} against {}: {}".format(root.meta_type, relpath, [x.pattern for x in stream], recurse))
                        if not recurse:
                            continue

                        for facet in obj.get_facets(root=root, seen=seen, streams=[stream], path=path, depth=depth+1):
                            if (self.id, relname, facet.id) in seen:
                                # avoid a cycle
                                continue
                            yield facet
                            seen.add((self.id, relname, facet.id))

    def rrdPath(self):
        """Return filesystem path for RRD files for this component.

        Overrides RRDView to flatten component RRD files into a single
        subdirectory per-component per-device. This allows for the
        possibility of a component changing its contained path within
        the device without losing historical performance data.

        This requires that each component have a unique id within the
        device's namespace.

        """
        original = super(ComponentBase, self).rrdPath()

        try:
            # Zenoss 5 returns a JSONified dict from rrdPath.
            json.loads(original)
        except ValueError:
            # Zenoss 4 and earlier return a string that starts with "Devices/"
            return os.path.join('Devices', self.device().id, self.id)
        else:
            return original

    def getRRDTemplateName(self):
        """Return name of primary template to bind to this component."""
        if self._templates:
            return self._templates[-1]

        return ''

    def getRRDTemplates(self):
        """Return list of templates to bind to this component.

        Enhances RRDView.getRRDTemplates by supporting both acquisition
        and inhertence template binding. Additionally supports user-
        defined *-replacement and *-addition monitoring templates that
        can replace or augment the standard templates respectively.

        """
        templates = []

        for template_name in self._templates:
            replacement = self.getRRDTemplateByName(
                '{}-replacement'.format(template_name))

            if replacement:
                templates.append(replacement)
            else:
                template = self.getRRDTemplateByName(template_name)
                if template:
                    templates.append(template)

            addition = self.getRRDTemplateByName(
                '{}-addition'.format(template_name))

            if addition:
                templates.append(addition)

        return templates
