##############################################################################
#
# Copyright (C) Zenoss, Inc. 2016, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################
import os
import math
import re
import time
import copy
from zope.interface import classImplements
from Products.Zuul.decorators import memoize
from Products.Zuul.utils import ZuulMessageFactory as _t
from Products.ZenRelations.RelSchema import ToMany, ToManyCont
from Products.Zuul.form import schema
from Products.Zuul.form.interfaces import IFormBuilder
from Products.Zuul.infos import InfoBase, ProxyProperty
from Products.Zuul.interfaces import IInfo
from Products.Zuul.catalog.interfaces import IPathReporter

from ..wrapper.ComponentFormBuilder import ComponentFormBuilder
from ..wrapper.ComponentPathReporter import ComponentPathReporter
from ..utils import impact_installed, dynamicview_installed, has_metricfacade, FACET_BLACKLIST

from ..gsm import get_gsm
from ..functions import pluralize, get_symbol_name, relname_from_classname, \
    get_zenpack_path, ordered_values

from ..base.Component import Component, HWComponent, Service
from ..base.Device import Device
from ..zuul import schema_map

from .Spec import Spec, DeviceInfoStatusProperty, \
    RelationshipInfoProperty, RelationshipGetter, RelationshipSetter
from .ClassPropertySpec import ClassPropertySpec
from .ClassRelationshipSpec import ClassRelationshipSpec
from .ImpactTriggerSpec import ImpactTriggerSpec

DYNAMICVIEW_INSTALLED = dynamicview_installed()
if DYNAMICVIEW_INSTALLED:
    from ZenPacks.zenoss.DynamicView.interfaces import IRelatable, IRelationsProvider
    from ZenPacks.zenoss.DynamicView.interfaces import IGroupMappingProvider
    from ..dynamicview import DynamicViewRelatable, DynamicViewRelationsProvider, DynamicViewGroupMappingProvider

IMPACT_INSTALLED = impact_installed()
if IMPACT_INSTALLED:
    from ZenPacks.zenoss.Impact.impactd.interfaces import IRelationshipDataProvider, INodeTriggers
    from ..impact import ImpactRelationshipDataProvider
    from ..base.BaseTriggers import BaseTriggers

HAS_METRICFACADE = has_metricfacade()

GSM = get_gsm()


class ClassSpec(Spec):
    """ClassSpec.

    'impacts' and 'impacted_by' will cause impact adapters to be registered, so the
    relationship is shown in impact, but not in dynamicview. If you would like to
    use dynamicview, you should change:

        'MyComponent': {
            'impacted_by': ['someRelationship']
            'impacts': ['someThingElse']
        }

    To:

        'MyComponent': {
            'dynamicview_views': ['service_view'],
            'dynamicview_relations': {
                'impacted_by': ['someRelationship']
                'impacts': ['someThingElse']
            }
        }

    This will cause your impact relationship to show in both dynamicview and impact.

    There is one important exception though.  Until ZEN-14579 is fixed, if your
    relationship/method returns an object that is not itself part of service_view,
    the dynamicview -> impact export will not include that object.

    To fix this, you must use impacts/impact_by for such relationships:

        'MyComponent': {
            'dynamicview_views': ['service_view'],
            'dynamicview_relations': {
                'impacted_by': ['someRelationship']
                'impacts': ['someThingElse']
            }
            impacted_by': ['someRelationToANonServiceViewThing']
        }

    If you need the object to appear in both DV and impact, include it in both lists.  If
    it would already be exported to impact, because it is in service_view, only use
    dynamicview_relations -> impacts/impacted_by, to avoid slowing down performance due
    to double adapters doing the same thing.
    """

    _model_schema_class = None
    _model_class = None
    _iinfo_schema_class = None
    _iinfo_class = None
    _info_schema_class = None
    _info_class = None
    _formbuilder_class = None
    _icon_url = None
    _datapoints_to_fetch = None
    _plumbed = False
    _property_defaults = {}

    def __init__(
            self,
            zenpack,
            name,
            base=Component,
            meta_type=None,
            label=None,
            plural_label=None,
            short_label=None,
            plural_short_label=None,
            auto_expand_column='name',
            initial_sort_column='name',
            label_width=80,
            plural_label_width=None,
            content_width=None,
            icon=None,
            order=100,
            properties=None,
            relationships=None,
            impact_triggers=None,
            impacts=None,
            impacted_by=None,
            monitoring_templates=None,
            filter_display=True,
            filter_hide_from=None,
            dynamicview_views=None,
            dynamicview_group=None,
            dynamicview_weight=None,
            dynamicview_relations=None,
            extra_paths=None,
            _source_location=None,
            zplog=None
            ):
        """
            Create a Class Specification

            :param base: Base Class (defaults to Component)
            :type base: list(class)
            :param meta_type: meta_type (defaults to class name)
            :type meta_type: str
            :param label: Label to use when describing this class in the
                   UI.  If not specified, the default is to use the class name.
            :type label: str
            :param plural_label: Plural form of the label (default is to use the
                  "pluralize" function on the label)
            :type plural_label: str
            :param short_label: If specified, this is a shorter version of the
                   label.
            :type short_label: str
            :param plural_short_label:  If specified, this is a shorter version
                   of the short_label.
            :type plural_short_label: str
            :param auto_expand_column: The name of the column to expand to fill
                   available space in the grid display.  Defaults to the first
                   column ('name').
            :type auto_expand_column: str
            :param initial_sort_column: The name of the column on which to initially sort.
                    Defaults to the first column ('name').
            :type initial_sort_column: str
            :param label_width: Optionally overrides ZPL's label width
                   calculation with a higher value.
            :type label_width: int
            :param plural_label_width: Optionally overrides ZPL's label width
                   calculation with a higher value.
            :type plural_label_width: int
            :param content_width: Optionally overrides ZPL's content width
                   calculation with a higher value.
            :type content_width: int
            :param icon: Filename (of a file within the zenpack's 'resources/icon'
                   directory).  Default is the {class name}.png
            :type icon: str
            :param order: Rank for sorting this class among other classes
            :type order: int
            :param properties: TODO
            :type properties: SpecsParameter(ClassPropertySpec)
            :param relationships: TODO
            :type relationships: SpecsParameter(ClassRelationshipSpec)
            :param impact_triggers: Impact Trigger
            :type impact_triggers: SpecsParameter(ImpactTriggerSpec)
            :param impacts: TODO
            :type impacts: list(str)
            :param impacted_by: TODO
            :type impacted_by: list(str)
            :param monitoring_templates: TODO
            :type monitoring_templates: list(str)
            :param filter_display: Should this class show in any other filter dropdowns?
            :type filter_display: bool
            :param filter_hide_from: Classes for which this class should not show in the filter dropdown.
            :type filter_hide_from: list(class)
            :param dynamicview_views: TODO
            :type dynamicview_views: list(str)
            :param dynamicview_group: TODO
            :type dynamicview_group: str
            :param dynamicview_weight: TODO
            :type dynamicview_weight: float
            :param dynamicview_relations: TODO
            :type dynamicview_relations: dict
            :param extra_paths: TODO
            :type extra_paths: list(ExtraPath)

        """
        super(ClassSpec, self).__init__(_source_location=_source_location)
        if zplog:
            self.LOG = zplog
        self.zenpack = zenpack
        self.name = name
        self.symbol_name = get_symbol_name(self.zenpack.name, self.name)

        # Verify that bases is a tuple of base types.
        if isinstance(base, (tuple, list, set)):
            bases = tuple(base)
        else:
            bases = (base,)

        self.bases = bases
        self.base = self.bases

        self.meta_type = meta_type or self.name
        self.label = label or self.meta_type
        self.plural_label = plural_label or pluralize(self.label)

        if short_label:
            self.short_label = short_label
            self.plural_short_label = plural_short_label or pluralize(self.short_label)
        else:
            self.short_label = self.label
            self.plural_short_label = plural_short_label or self.plural_label

        self.auto_expand_column = auto_expand_column
        self.initial_sort_column = initial_sort_column

        self.label_width = int(label_width)
        self.plural_label_width = plural_label_width or self.label_width + 7
        self.content_width = content_width or label_width

        self.icon = icon

        self.order = order

        # save property defaults so they can be reapplied later
        if properties:
            self._property_defaults = properties.get('DEFAULTS', {})

        # Properties.
        self.properties = self.specs_from_param(
            ClassPropertySpec, 'properties', properties, zplog=self.LOG)

        self.normalize_child_order(self.properties.values())

        # Relationships
        # If these exist, they will refer to relationship display properties, but won't have a schema
        # defined (yet).  The schema is added later
        self.relationships = self.specs_from_param(
            ClassRelationshipSpec, 'relationships', relationships, zplog=self.LOG)

        self.normalize_child_order(self.relationships.values())

        # Impact.
        self.impacts = impacts
        self.impacted_by = impacted_by

        # Properties.
        self.impact_triggers = self.specs_from_param(
            ImpactTriggerSpec, 'impact_triggers', impact_triggers, zplog=self.LOG)

        # Monitoring Templates.
        if monitoring_templates is None:
            self.monitoring_templates = [self.label.replace(' ', '')]
        elif isinstance(monitoring_templates, basestring):
            self.monitoring_templates = [monitoring_templates]
        else:
            self.monitoring_templates = list(monitoring_templates)

        self.filter_display = filter_display
        self.filter_hide_from = filter_hide_from

        # Dynamicview Views and Group
        if dynamicview_views is None:
            self.dynamicview_views = ['service_view']
        elif isinstance(dynamicview_views, basestring):
            self.dynamicview_views = [dynamicview_views]
        else:
            self.dynamicview_views = list(dynamicview_views)

        if dynamicview_group is None:
            self.dynamicview_group = self.plural_short_label
        else:
            self.dynamicview_group = dynamicview_group

        if dynamicview_weight is None:
            self.dynamicview_weight = self.scale_order(scale=1000, offset=1000)
        else:
            self.dynamicview_weight = dynamicview_weight

        # additional relationships to add, beyond IMPACTS and IMPACTED_BY.
        if dynamicview_relations is None:
            self.dynamicview_relations = {}
        else:
            # TAG_NAME: ['relationship', 'or_method']
            self.dynamicview_relations = dict(dynamicview_relations)

        # Paths
        self.path_pattern_streams = []
        if extra_paths is not None:
            self.extra_paths = extra_paths
            for pattern_tuple in extra_paths:
                # Each item in extra_paths is expressed as a tuple of
                # regular expression patterns that are matched
                # in order against the actual relationship path structure
                # as it is traversed and built up get_facets.
                #
                # To facilitate matching, we construct a compiled set of
                # regular expressions that can be matched against the
                # entire path string, from root to leaf.
                #
                # So:
                #
                #   ('orgComponent', '(parentOrg)+')
                # is transformed into a "pattern stream", which is a list
                # of regexps that can be applied incrementally as we traverse
                # the possible paths:
                #   (re.compile(^orgComponent),
                #    re.compile(^orgComponent/(parentOrg)+),
                #    re.compile(^orgComponent/(parentOrg)+/?$')
                #
                # Once traversal embarks upon a stream, these patterns are
                # matched in order as the traversal proceeds, with the
                # first one to fail causing recursion to stop.
                # When the final one is matched, then the objects on that
                # relation are matched.  Note that the final one may
                # match multiple times if recursive relationships are
                # in play.

                pattern_stream = []
                for i, _ in enumerate(pattern_tuple, start=1):
                    pattern = "^" + "/".join(pattern_tuple[0:i])
                    # If we match these patterns, keep going.
                    pattern_stream.append(re.compile(pattern))
                if pattern_stream:
                    # indicate that we've hit the end of the path.
                    pattern_stream.append(re.compile("/?$"))

                self.path_pattern_streams.append(pattern_stream)
        else:
            self.extra_paths = []

    @property
    def scaled_order(self):
        return self.scale_order(scale=1, offset=5)

    def check_ancestor_properties(self, spec_name):
        """Update any inheritable properties from ancestor"""
        base_spec = self.zenpack.classes.get(spec_name)
        for prop_name, prop_spec in base_spec.properties.items():
            # if we don't have it, create our own copy
            if prop_name not in self.properties:
                self.properties[prop_name] = copy.copy(prop_spec)
                this_prop_spec = self.properties[prop_name]
                this_prop_spec.class_spec = self

                # override any inherited properties with properties DEFAULTS
                for k, v in self._property_defaults.items():
                    # avoid unwanted keys like _source_location
                    if k not in this_prop_spec.init_params.keys():
                        continue
                    setattr(this_prop_spec, k, v)

    def update_inherited_property_parameters(self):
        """ Update properties and property parameters from ancestors """
        # Retrieve missing properties from bases
        for base_name in self.get_base_specs():
            self.check_ancestor_properties(base_name)

        # For existing, update any inheritable property parameters
        for prop_spec in self.properties.values():
            prop_spec.update_inherited_params()

    def plumb_class_relations(self):
        """
            Plumb class relations and update
            remote class _v_local_relations/_relations
            as well as updating NEW_RELATIONS and NEW_COMPONENT_TYPES
        """
        if not self._plumbed:
            for relname, relationship in self.relationships.iteritems():
                # if no schema was ever allocated, remove this relationship from the class
                # this happens if the ClassSpec sets display properties for a nonexistent relation
                if not relationship.schema:
                    self.LOG.error("Removing invalid display config for relationship {} from  {}.{}".format(
                        relname, self.zenpack.name, self.name))
                    self.relationships.pop(relname)
                    continue
                relationship.plumb()
            self._plumbed = True

    def update_inherited_relation_parameters(self):
        """inherit parent relationship properties if not overridden locally"""
        for rel_spec in self.relationships.values():
            rel_spec.update_inherited_params()

    def update_child_relations(self, relname):
        """ Update relationships with any that
            should be inherited from base classes
        """
        # process descendants first
        for d in self.get_descendant_specs():
            self.zenpack.classes.get(d).update_child_relations(relname)

        # find this relation
        found_rel = self.find_relation_in_base_specs(relname)
        if found_rel:
            # add if it's not already here
            if relname not in self.relationships:
                self.relationships[relname] = found_rel
            else:
                # otherwise ensure it has a schema
                if not self.relationships[relname].schema:
                    self.relationships[relname].schema = found_rel.schema

    def find_property_in_base_specs(self, propname):
        '''return nearest inherited ClassPropertySpec'''
        base_specs = self.get_base_specs()
        for base in base_specs:
            base_cls = self.zenpack.classes.get(base)
            if propname in base_cls.properties:
                return base_cls.properties.get(propname)
        return None

    def find_relation_in_base_specs(self, relname):
        '''return nearest inherited RelationshipSpec'''
        base_specs = self.get_base_specs()
        for base in base_specs:
            base_cls = self.zenpack.classes.get(base)
            if relname in base_cls.relationships:
                return base_cls.relationships.get(relname)
        return None

    def get_base_specs(self, bases=None):
        '''Return ClassSpec bases in order of nearest proximity'''
        if not bases:
            bases = []
        for base in self.bases:
            base_cls = self.zenpack.classes.get(base)
            if not base_cls:
                continue
            if base not in bases:
                bases.append(base)
            bases = base_cls.get_base_specs(bases)
        return bases

    def get_descendant_specs(self):
        """Return ClassSpec descendants of this class"""
        descendents = []
        for cls in self.zenpack.classes.values():
            if self.name in cls.bases:
                descendents.append(cls.name)
        return descendents

    @property
    @memoize
    def resolved_bases(self):
        """Return tuple of base classes.

        This is different than ClassSpec.bases in that all elements of
        the tuple will be type instances. ClassSpec.bases may contain
        string representations of types.
        """
        resolved_bases = []
        for base in self.bases:
            if isinstance(base, type):
                resolved_bases.append(base)
            elif base not in self.zenpack.classes:
                raise ValueError("Unrecognized base class name '%s'" % base)
            else:
                base_spec = self.zenpack.classes[base]
                resolved_bases.append(base_spec.model_class)

        return tuple(resolved_bases)

    def base_class_specs(self, recursive=False):
        """Return tuple of base ClassSpecs.

        Iterates over ClassSpec.bases (possibly recursively) and returns
        instances of the ClassSpec objects for them.
        """
        base_specs = []
        for base in self.bases:
            if isinstance(base, type):
                # bases will contain classes rather than class names when referring
                # to a class outside of this zenpack specification.  Ignore
                # these.
                continue

            class_spec = self.zenpack.classes[base]
            base_specs.append(class_spec)

            if recursive:
                base_specs.extend(class_spec.base_class_specs())

        return tuple(base_specs)

    def subclass_specs(self):
        subclass_specs = []
        for class_spec in self.zenpack.classes.values():
            if self in class_spec.base_class_specs(recursive=True):
                subclass_specs.append(class_spec)

        return subclass_specs

    @property
    def filter_hide_from_class_specs(self):
        specs = []
        if self.filter_hide_from is None:
            return specs

        for classname in self.filter_hide_from:
            if classname not in self.zenpack.classes:
                raise ValueError("Unrecognized filter_hide_from class name '%s'" % classname)
            class_spec = self.zenpack.classes[classname]
            specs.append(class_spec)

        return specs

    def inherited_properties(self):
        properties = {}
        for base in self.bases:
            if not isinstance(base, type):
                class_spec = self.zenpack.classes[base]
                properties.update(class_spec.inherited_properties())

        properties.update(self.properties)

        return properties

    def inherited_relationships(self):
        relationships = {}
        for base in self.bases:
            if not isinstance(base, type):
                class_spec = self.zenpack.classes[base]
                relationships.update(class_spec.inherited_relationships())

        relationships.update(self.relationships)

        return relationships

    def is_a(self, type_):
        """Return True if this class is a subclass of type_."""
        return issubclass(self.model_schema_class, type_)

    def get_info_base(self):
        """Return appropriate info class"""
        for cls, map in schema_map.items():
            if self.is_a(cls):
                return map.get('info', InfoBase)
        return InfoBase

    def get_interfaces_base(self):
        """Return appropriate interfaces class"""
        for cls, map in schema_map.items():
            if self.is_a(cls):
                return map.get('interface', IInfo)
        return IInfo

    def get_facade_base(self):
        """Return appropriate interfaces class"""
        for cls, map in schema_map.items():
            if self.is_a(cls):
                return map.get('facade', None)
        return None

    def get_path_reporter(self):
        """Return appropriate path reporter class"""
        for cls, map in schema_map.items():
            if self.is_a(cls):
                return map.get('reporter', None)
        return None

    @property
    def is_device(self):
        """Return True if this class is a Device."""
        return self.is_a(Device)

    @property
    def is_component(self):
        """
            **Deprecated
            Return True if this class is a Component.
        """

        return self.is_a(Component)

    @property
    def is_hardware_component(self):
        """
            **Deprecated
            Return True if this class is a HWComponent.
        """
        return self.is_a(HWComponent)

    @property
    def is_a_component(self):
        """Return True if this class is a component class."""
        for cls in schema_map.keys():
            if cls == Device or cls == Service:
                continue
            if self.is_a(cls):
                return True
        return False

    @property
    def icon_url(self):
        """Return relative URL to icon."""
        if not self._icon_url:
            self._icon_url = self.get_icon_url()
        return self._icon_url

    def get_icon_url(self):
        """Set icon_url"""
        # if it's already given with the path
        if self.icon and self.icon.startswith('/'):
            return self.icon
        else:
            # otherwise check if it exists whether or not it's given
            icon_filename = self.icon or '{}.png'.format(self.name)
            zenpack_path = get_zenpack_path(self.zenpack.name)
            if zenpack_path:
                icon_path = os.path.join(
                    zenpack_path,
                    'resources',
                    'icon',
                    icon_filename)
                if os.path.isfile(icon_path):
                    return '/++resource++{zenpack_name}/icon/{filename}'.format(
                        zenpack_name=self.zenpack.name,
                        filename=icon_filename)
        # fall back to default
        return '/zport/dmd/img/icons/noicon.png'

    @property
    def model_schema_class(self):
        """Return model schema class."""
        if not self._model_schema_class:
            self._model_schema_class = self.create_model_schema_class()
        return self._model_schema_class

    def create_model_schema_class(self):
        """Create and return model schema class."""
        attributes = {
            'zenpack_name': self.zenpack.name,
            'meta_type': self.meta_type,
            'portal_type': self.meta_type,
            'icon_url': self.icon_url,
            'class_label': self.label,
            'class_plural_label': self.plural_label,
            'class_short_label': self.short_label,
            'class_plural_short_label': self.plural_short_label,
            'dynamicview_views': self.dynamicview_views,
            'dynamicview_group': {
                'name': self.dynamicview_group,
                'weight': self.dynamicview_weight,
                'type': self.zenpack.name,
                'icon': self.icon_url,
            },
        }

        properties = []
        relations = []
        templates = []
        device_catalogs = {}
        global_catalogs = {}

        # First inherit from bases.
        for base in self.resolved_bases:
            if hasattr(base, '_properties'):
                properties.extend(base._properties)
            if hasattr(base, '_templates'):
                templates.extend(base._templates)
            if hasattr(base, '_device_catalogs'):
                device_catalogs.update(base._device_catalogs)
            if hasattr(base, '_global_catalogs'):
                global_catalogs.update(base._global_catalogs)

        # Add local properties and catalog indexes.
        for name, spec in self.properties.iteritems():
            if spec.api_backendtype == 'property':
                # for normal properties (not methods or datapoints, apply default value)
                attributes[name] = spec.default  # defaults to None

            elif spec.datapoint:
                # Provide a method to look up the datapoint and get the value from rrd
                def datapoint_method(self, default=spec.datapoint_default, cached=spec.datapoint_cached, datapoint=spec.datapoint):
                    if cached:
                        r = self.cacheRRDValue(datapoint, default=default)
                    else:
                        if HAS_METRICFACADE:
                            r = self.getFetchedDataPoint(datapoint)
                        else:
                            r = self.getRRDValue(datapoint, start=time.time() - 1800)

                    if r is not None:
                        if not math.isnan(float(r)):
                            return r
                    return default

                attributes[name] = datapoint_method

            else:
                # api backendtype is 'method', and it is assumed that this
                # pre-existing method is being inherited from a parent class
                # or will be provided by the developer.  In any case, we want
                # to omit it from the generated schema class, so that we don't
                # shadow an existing method with a property with a default
                # value of 'None.'
                pass

            if spec.ofs_dict:
                properties.append(spec.ofs_dict)

            # Add class and instance catalogs.
            for index_name, index_spec in spec.catalog_indexes.iteritems():
                index_scope = index_spec.get('scope', 'device')
                index_type = index_spec.get('type', 'field')

                if index_scope in ('both', 'device'):
                    if self.name in device_catalogs:
                        device_catalogs[self.name][index_name] = index_type
                    else:
                        device_catalogs[self.name] = {index_name: index_type}

                if index_scope in ('both', 'global'):
                    if self.name in global_catalogs:
                        global_catalogs[self.name][index_name] = index_type
                    else:
                        global_catalogs[self.name] = {index_name: index_type}

        # Add local relations.
        for name, spec in self.relationships.iteritems():
            relations.append(spec.zenrelations_tuple)

            # Add getter and setter to allow modeling. Only for local
            # relationships because base classes will provide methods
            # for their relationships.
            attributes['get_{}'.format(name)] = RelationshipGetter(name)
            attributes['set_{}'.format(name)] = RelationshipSetter(name)

        # Add local templates.
        templates.extend(self.monitoring_templates)

        attributes['_properties'] = tuple(properties)
        attributes['_v_local_relations'] = tuple(relations)
        attributes['_templates'] = tuple(templates)
        attributes['_device_catalogs'] = device_catalogs
        attributes['_global_catalogs'] = global_catalogs

        # Add Impact stuff.
        attributes['impacts'] = self.impacts
        attributes['impacted_by'] = self.impacted_by
        attributes['impact_triggers'] = [t.get_trigger() for t in self.impact_triggers.values()]

        attributes['dynamicview_relations'] = self.dynamicview_relations

        # Add link provider
        attributes['link_providers'] = self.zenpack.link_providers

        # And facet patterns.
        if self.path_pattern_streams:
            attributes['_v_path_pattern_streams'] = self.path_pattern_streams

        attributes['LOG'] = self.LOG
        return self.create_schema_class(
            get_symbol_name(self.zenpack.name, 'schema'),
            self.name,
            self.resolved_bases,
            attributes)


    @property
    def model_class(self):
        """Return model class."""
        if not self._model_class:
            self._model_class = self.create_model_class()
        return self._model_class

    def create_model_class(self):
        """Create and return model class."""
        return self.create_stub_class(
            get_symbol_name(self.zenpack.name, self.name),
            self.model_schema_class,
            self.name)

    @property
    def iinfo_schema_class(self):
        """Return I<name>Info schema class."""
        if not self._iinfo_schema_class:
            self._iinfo_schema_class = self.create_iinfo_schema_class()
        return self._iinfo_schema_class

    def create_iinfo_schema_class(self):
        """Create and return I<name>Info schema class."""
        bases = []
        for base_classname in self.zenpack.classes[self.name].bases:
            if base_classname in self.zenpack.classes:
                bases.append(self.zenpack.classes[base_classname].iinfo_class)

        if not bases:
            bases = [self.get_interfaces_base()]

        attributes = {}

        for spec in self.inherited_properties().itervalues():
            attributes.update(spec.iinfo_schemas)

        for i, specs in enumerate(self.containing_spec_relations):
            spec, relspec = specs
            relname = self.get_relname(spec, relspec)
            if relspec and not relspec.details_display:
                continue

            attributes[relname] = schema.Entity(
                title=_t(spec.label),
                group="Overview",
                order=3 + i / 100.0)

        for spec in self.inherited_relationships().itervalues():
            attributes.update(spec.iinfo_schemas)

        return self.create_schema_class(
            get_symbol_name(self.zenpack.name, 'schema'),
            'I{}Info'.format(self.name),
            tuple(bases),
            attributes)

    @property
    def iinfo_class(self):
        """Return I<name>Info class."""
        if not self._iinfo_class:
            self._iinfo_class = self.create_iinfo_class()
        return self._iinfo_class

    def create_iinfo_class(self):
        """Create and return I<Info>Info class."""
        return self.create_stub_class(
            get_symbol_name(self.zenpack.name, self.name),
            self.iinfo_schema_class,
            'I{}Info'.format(self.name))

    @property
    def info_schema_class(self):
        """Return <name>Info schema class."""
        if not self._info_schema_class:
            self._info_schema_class = self.create_info_schema_class()
        return self._info_schema_class

    def create_info_schema_class(self):
        """Create and return <name>Info schema class."""
        bases = []
        for base_classname in self.zenpack.classes[self.name].bases:
            if base_classname in self.zenpack.classes:
                bases.append(self.zenpack.classes[base_classname].info_class)

        attributes = {}

        if not bases:
            bases = [self.get_info_base()]
            if self.is_device:
                # Override how status is determined for devices.
                attributes["status"] = DeviceInfoStatusProperty()

        attributes.update({
            'class_label': ProxyProperty('class_label'),
            'class_plural_label': ProxyProperty('class_plural_label'),
            'class_short_label': ProxyProperty('class_short_label'),
            'class_plural_short_label': ProxyProperty('class_plural_short_label')
        })

        for spec, relspec in self.containing_spec_relations:
            if relspec:
                attributes.update(relspec.info_properties)
            else:
                attr = relname_from_classname(spec.name)
                attributes[attr] = RelationshipInfoProperty(attr)

        for spec in self.inherited_properties().itervalues():
            attributes.update(spec.info_properties)

        for spec in self.inherited_relationships().itervalues():
            attributes.update(spec.info_properties)

        attributes['dataPointsToFetch'] = self.datapoints_to_fetch

        return self.create_schema_class(
            get_symbol_name(self.zenpack.name, 'schema'),
            '{}Info'.format(self.name),
            tuple(bases),
            attributes)

    @property
    def info_class(self):
        """Return Info subclass."""
        if not self._info_class:
            self._info_class = self.create_info_class()
        return self._info_class

    def create_info_class(self):
        """Create and return Info subclass."""
        info_class = self.create_stub_class(
            get_symbol_name(self.zenpack.name, self.name),
            self.info_schema_class,
            '{}Info'.format(self.name))
        classImplements(info_class, self.iinfo_class)
        return info_class

    @property
    def formbuilder_class(self):
        """Return FormBuilder subclass."""
        if not self._formbuilder_class:
            self._formbuilder_class = self.create_formbuilder_class()
        return self._formbuilder_class

    def create_formbuilder_class(self):
        """Create and return FormBuilder subclass.

        Includes rendering hints for ComponentFormBuilder.

        """
        bases = (ComponentFormBuilder,)
        attributes = {}
        renderer = {}

        # Find renderers for our properties:
        for propname, spec in self.properties.iteritems():
            renderer[propname] = spec.renderer

        # Find renderers for inherited properties
        for class_spec in self.base_class_specs(recursive=True):
            for propname, spec in class_spec.properties.iteritems():
                renderer[propname] = spec.renderer

        attributes['renderer'] = renderer
        attributes['zenpack_id_prefix'] = self.zenpack.id_prefix

        formbuilder = self.create_class(
            get_symbol_name(self.zenpack.name, self.name),
            get_symbol_name(self.zenpack.name, 'schema'),
            '{}FormBuilder'.format(self.name),
            tuple(bases),
            attributes)

        classImplements(formbuilder, IFormBuilder)

        return formbuilder

    def create_registered(self):
        GSM.registerAdapter(self.info_class, (self.model_class,), self.iinfo_class)
        if self.is_a_component:
            GSM.registerAdapter(self.formbuilder_class, (self.info_class,), IFormBuilder)
        self.register_facade_types()
        self.register_path_adapters()
        self.register_dynamicview_adapters()
        self.register_impact_adapters()

    def register_dynamicview_adapters(self):
        if not DYNAMICVIEW_INSTALLED:
            return

        if not self.dynamicview_views:
            return

        GSM.registerAdapter(
            DynamicViewRelatable,
            (self.model_class,),
            IRelatable)

        GSM.registerSubscriptionAdapter(
            DynamicViewRelationsProvider,
            required=(self.model_class,),
            provided=IRelationsProvider)

        GSM.registerSubscriptionAdapter(
            DynamicViewGroupMappingProvider,
            required=(DynamicViewRelatable,),
            provided=IGroupMappingProvider)

    def register_impact_adapters(self):
        """Register Impact adapters."""

        if not IMPACT_INSTALLED:
            return

        if self.impacts or self.impacted_by:
            GSM.registerSubscriptionAdapter(
                ImpactRelationshipDataProvider,
                required=(self.model_class,),
                provided=IRelationshipDataProvider)

        if self.impact_triggers:
            GSM.registerSubscriptionAdapter(
                BaseTriggers,
                required=(self.model_class,),
                provided=INodeTriggers)

    def register_facade_types(self):
        """Ensure this class gets listed in GUI elements using the _instanceClass property"""
        f_cls = self.get_facade_base()
        if f_cls:
            cls_name = '{}.{}'.format(self.symbol_name, self.name)
            if hasattr(f_cls, '_types'):
                f_cls._types = tuple(set(list(f_cls._types) + [cls_name]))
            else:
                self.LOG.error("Could not register {} in {}".format(cls_name, f_cls.__name__))

    def register_path_adapters(self):
        """Register additional path adapters if needed"""
        mixin = self.get_path_reporter()
        if mixin and not self.is_device:
            reporter = type('{}PathReporter'.format(self.name), (ComponentPathReporter, mixin,), {})
            GSM.registerAdapter(reporter, (self.model_class,), IPathReporter)

    @property
    def containing_components(self):
        return self.containing_component_specs()

    @property
    def containing_spec_relations(self):
        return self.containing_component_specs(include_relations=True)

    def containing_component_specs(self, include_relations=False):
        """Return iterable of containing component ClassSpec instances.
        and optionally their matching ClassRelationshipSpec instances
        Instances will be sorted shallow to deep.
        """
        containing_specs = []

        for relname, relspec in self.relationships.items():
            if not relspec.schema:
                self.LOG.warn('{} relation {} has no schema'.format(self.name, relspec.name))
                continue

            if not issubclass(relspec.schema.remoteType, ToManyCont):
                continue

            remote_spec = relspec.remote_class_spec
            if not remote_spec or remote_spec.is_device:
                continue
            if remote_spec == self:
                continue

            containing_specs.extend(remote_spec.containing_component_specs(include_relations))

            if include_relations:
                containing_specs.append((remote_spec, relspec))
            else:
                containing_specs.append(remote_spec)

        return containing_specs

    @property
    def faceting_components(self):
        return self.faceting_component_specs()

    @property
    def faceting_spec_relations(self):
        return self.faceting_component_specs(include_relations=True)

    def faceting_component_specs(self, include_relations=False):
        """Return iterable of faceting component ClassSpec and optionally RelationshipSpec instances."""
        faceting_specs = []
        for relname, relspec in self.relationships.items():
            # probably not relevant now
            if relname in FACET_BLACKLIST:
                continue
            # this shouldn't be possible
            if not relspec.schema:
                self.LOG.warn('{} relation {} has no schema'.format(self.name, relspec.name))
                continue
            if not issubclass(relspec.schema.remoteType, ToMany):
                continue
            remote_spec = relspec.remote_class_spec
            remote_relname = relspec.schema.remoteName
            if remote_spec:
                for class_spec in [remote_spec] + remote_spec.subclass_specs():
                    if class_spec and not class_spec.is_device:
                        if include_relations:
                            remote_relspec = class_spec.relationships.get(remote_relname)
                            faceting_specs.append((class_spec, remote_relspec))
                        else:
                            faceting_specs.append(class_spec)

        return faceting_specs

    @property
    def filterable_by(self):
        """Return meta_types by which this class can be filtered."""
        if not self.filter_display:
            return []

        containing = {x.meta_type for x in self.containing_components}
        faceting = {x.meta_type for x in self.faceting_components}
        hidden = {x.meta_type for x in self.filter_hide_from_class_specs}

        return list(containing | faceting - hidden)

    @property
    def datapoints_to_fetch(self):
        if not self._datapoints_to_fetch:
            self._datapoints_to_fetch = self.get_datapoints_to_fetch()
        return self._datapoints_to_fetch

    def get_datapoints_to_fetch(self):
        """return list of datapoint names for templates associated with this class"""
        return [spec.datapoint for spec in self.properties.values() if spec.datapoint and spec.grid_display]

    @property
    def containing_js_fields(self):
        """Return list of JavaScript fields for containing components."""
        fields = []

        if self.is_device:
            return fields

        filtered_relationships = {}
        for r in self.relationships.values():
            if r.grid_display is False:
                filtered_relationships[r.remote_classname] = r

        for spec, relspec in self.containing_spec_relations:
            if spec.name in filtered_relationships:
                continue
            fields.append(
                "{{name: '{}'}}"
                .format(self.get_relname(spec, relspec)))

        return fields

    @property
    def containing_js_columns(self):
        """Return list of JavaScript columns for containing components."""
        columns = []

        if self.is_device:
            return columns

        filtered_relationships = {}
        for r in self.relationships.values():
            if r.grid_display is False:
                filtered_relationships[r.remote_classname] = r

        for spec, relspec in self.containing_spec_relations:
            if spec.name in filtered_relationships:
                continue

            header = spec.short_label
            if relspec:
                header = relspec.short_label or spec.short_label

            width = max(spec.content_width + 14, spec.label_width + 20)
            renderer = 'Zenoss.render.zenpacklib_{zenpack_id_prefix}_entityLinkFromGrid'.format(
                zenpack_id_prefix=self.zenpack.id_prefix)

            column_fields = [
                "id: '{}'".format(spec.name),
                "dataIndex: '{}'".format(self.get_relname(spec, relspec)),
                "header: _t('{}')".format(header),
                "width: {}".format(width),
                "renderer: {}".format(renderer),
                "sortable: true"
            ]

            columns.append('{{{}}}'.format(',\n                       '.join(column_fields)))

        return columns

    @property
    def global_js_snippet(self):
        """Return global JavaScript snippet."""
        return (
            "ZC.registerName("
            "'{meta_type}', _t('{label}'), _t('{plural_label}')"
            ");\n"
            .format(
                meta_type=self.meta_type,
                label=self.label,
                plural_label=self.plural_label))

    @property
    def component_grid_panel_js_snippet(self):
        """Return ComponentGridPanel JavaScript snippet."""
        if self.is_device:
            return ''

        default_fields = [
            "{{name: '{}'}}".format(x) for x in (
                'uid', 'name', 'meta_type', 'class_label', 'status', 'severity',
                'usesMonitorAttribute', 'monitored', 'locking',
                )]

        default_left_columns = [(
            "{"
            "id: 'severity',\n"
            "                       dataIndex: 'severity',\n"
            "                       header: _t('Events'),\n"
            "                       renderer: Zenoss.render.severity,\n"
            "                       width: 50"
            "}"
        ), (
            "{"
            "id: 'name',\n"
            "                       dataIndex: 'name',\n"
            "                       header: _t('Name'),\n"
            "                       renderer: Zenoss.render.zenpacklib_" + self.zenpack.id_prefix + "_entityLinkFromGrid"
            "}"
        )]

        default_right_columns = [(
            "{"
            "id: 'monitored',\n"
            "                       dataIndex: 'monitored',\n"
            "                       header: _t('Monitored'),\n"
            "                       renderer: Zenoss.render.checkbox,\n"
            "                       width: 70"
            "}"
        ), (
            "{"
            "id: 'locking',\n"
            "                       dataIndex: 'locking',\n"
            "                       header: _t('Locking'),\n"
            "                       renderer: Zenoss.render.locking_icons,\n"
            "                       width: 65"
            "}"
        )]

        fields = []
        ordered_columns = []

        # Keep track of pixel width of custom fields. Exceeding a
        # certain width causes horizontal scrolling of the component
        # grid panel.
        width = 0

        for spec in self.inherited_properties().itervalues():
            fields.extend(spec.js_fields)
            ordered_columns.extend(spec.js_columns)
            width += spec.js_columns_width

        for spec in self.inherited_relationships().itervalues():
            fields.extend(spec.js_fields)
            ordered_columns.extend(spec.js_columns)
            width += spec.js_columns_width

        if width > 750:
            self.LOG.warning(
                "{}: {} custom columns exceed 750 pixels ({})".format(
                self.zenpack.name, self.name, width))

        return (
            "ZC.{meta_type}Panel = Ext.extend(ZC.ZPL_{zenpack_id_prefix}_ComponentGridPanel, {{"
            "    constructor: function(config) {{\n"
            "        config = Ext.applyIf(config||{{}}, {{\n"
            "            componentType: '{meta_type}',\n"
            "            autoExpandColumn: '{auto_expand_column}',\n"
            "            sortInfo: {{field: '{initial_sort_column}', direction: 'ASC'}},\n"
            "            fields: [{fields}],\n"
            "            columns: [{columns}]\n"
            "        }});\n"
            "        ZC.{meta_type}Panel.superclass.constructor.call(this, config);\n"
            "    }}\n"
            "}});\n"
            "\n"
            "Ext.reg('{meta_type}Panel', ZC.{meta_type}Panel);\n"
            .format(
                meta_type=self.meta_type,
                zenpack_id_prefix=self.zenpack.id_prefix,
                auto_expand_column=self.auto_expand_column,
                initial_sort_column=self.initial_sort_column,
                fields=',\n                     '.join(
                    default_fields +
                    self.containing_js_fields +
                    fields),
                columns=',\n                      '.join(
                    default_left_columns +
                    self.containing_js_columns +
                    ordered_values(ordered_columns) +
                    default_right_columns)))

    @property
    def subcomponent_nav_js_snippet(self):
        """Return subcomponent navigation JavaScript snippet."""

        def get_js_snippet(id, label, classes):
            """return basic JS nav snippet"""
            cases = []
            for c in classes:
                cases.append("case '{}': return true;".format(c))
            if not cases:
                return ''
            return (
                "Zenoss.nav.appendTo('Component', [{{\n"
                "    id: 'component_{id}',\n"
                "    text: _t('{label}'),\n"
                "    xtype: '{meta_type}Panel',\n"
                "    subComponentGridPanel: true,\n"
                "    filterNav: function(navpanel) {{\n"
                "        switch (navpanel.refOwner.componentType) {{\n"
                "            {cases}\n"
                "            default: return false;\n"
                "        }}\n"
                "    }},\n"
                "    setContext: function(uid) {{\n"
                "        ZC.{meta_type}Panel.superclass.setContext.apply(this, [uid]);\n"
                "    }}\n"
                "}}]);\n"
                .format(meta_type=self.meta_type, id=id, label=label, cases='\n            '.join(cases)))

        # list of containing and faceted class, relationship specs
        specs_rels = list(set(self.containing_spec_relations) | set(self.faceting_spec_relations))
        # dictionary with meta_type keys
        specs_rels_dict = dict([(r[0].meta_type, r) for r in specs_rels])
        # filtered class and relationship specs
        filtered = list(specs_rels_dict.get(f) for f in self.filterable_by)

        # decide what labels to use for each relation
        sections = {}
        for spec, relation in filtered:
            # skip if spec is a descendant to prevent duplicate entries from its bases
            if spec.name in self.get_descendant_specs():
                continue
            # default if no label specified
            label = self.plural_short_label
            # override with relation label
            if relation and relation.label:
                label = relation.label
            # new snippet if relation labeled
            if label not in sections:
                sections[label] = []
            # metatypes to which this label will apply
            if spec.meta_type not in sections[label]:
                sections[label].append(spec.meta_type)

        snippets = []
        for label, metatypes in sections.items():
            id = '{}_{}'.format(self.meta_type.lower(), '_'.join(label.lower().split(' ')))
            snippets.append(get_js_snippet(id, label, metatypes))

        return ''.join(snippets)

    @property
    def device_js_snippet(self):
        """Return device JavaScript snippet."""
        return ''.join((
            self.component_grid_panel_js_snippet,
            self.subcomponent_nav_js_snippet,
            ))

    def get_relname(self, spec, relspec):
        if relspec:
            return relspec.name
        else:
            return relname_from_classname(spec.name)

    def test_setup(self):
        """Execute from a test suite's afterSetUp method.

        Our test layer appears to wipe out adapter registrations. We
        call this again after the layer has been setup so that
        programatically-registered adapters are in place for testing.

        """
        self.create_registered()
        self.register_dynamicview_adapters()
        self.register_impact_adapters()

