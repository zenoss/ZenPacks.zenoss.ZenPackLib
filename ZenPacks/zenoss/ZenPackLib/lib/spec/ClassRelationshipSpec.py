##############################################################################
#
# Copyright (C) Zenoss, Inc. 2016, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################
from Products.Zuul.form import schema
from Products.Zuul.utils import ZuulMessageFactory as _t
from Products.ZenRelations.RelSchema import ToManyCont, ToOne

from .Spec import Spec, RelationshipInfoProperty, RelationshipLengthProperty
from ..helpers.OrderAndValue import OrderAndValue


class ClassRelationshipSpec(Spec):
    """ClassRelationshipSpec"""

    def __init__(
            self,
            class_,
            name,
            schema=None,
            label=None,
            short_label=None,
            label_width=None,
            content_width=None,
            display=True,
            details_display=True,
            grid_display=True,
            renderer=None,
            render_with_type=False,
            order=None,
            _source_location=None,
            zplog=None
            ):
        """
        Create a Class Relationship Specification

            :param label: Label to use when describing this relationship in the
                   UI.  If not specified, the default is to use the name of the
                   relationship's target class.
            :type label: str
            :param short_label: If specified, this is a shorter version of the
                   label, used, for example, in grid table headings.
            :type short_label: str
            :param label_width: Optionally overrides ZPL's label width
                   calculation with a higher value.
            :type label_width: int
            :param content_width:  Optionally overrides ZPL's content width
                   calculation with a higher value.
            :type content_width: int
            :param display: If this is set to False, this relationship will be
                   hidden from the UI completely.
            :type display: bool
            :param details_display: If this is set to False, this relationship
                   will be hidden from the "details" portion of the UI.
            :type details_display: bool
            :param grid_display:  If this is set to False, this relationship
                   will be hidden from the "grid" portion of the UI.
            :type grid_display: bool
            :param renderer: The default javascript renderer for a relationship
                   provides a link with the title of the target object,
                   optionally with the object's type (if render_with_type is
                   set).  If something more specific is required, a javascript
                   renderer function name may be provided.
            :type renderer: str
            :param render_with_type: Indicates that when an object is linked to,
                   it should be shown along with its type.  This is particularly
                   useful when the relationship's target is a base class that
                   may have several subclasses, such that the base class +
                   target object is not sufficiently descriptive on its own.
            :type render_with_type: bool
            :param order: TODO
            :type order: float

        """
        super(ClassRelationshipSpec, self).__init__(_source_location=_source_location)
        if zplog:
            self.LOG = zplog
        self.class_ = class_
        self.name = name
        self.schema = schema
        self.label = label
        self.short_label = short_label
        self.label_width = label_width
        self.content_width = content_width
        self.display = display
        self.details_display = details_display
        self.grid_display = grid_display
        self.renderer = renderer
        self.render_with_type = render_with_type
        self.order = order

        if not self.display:
            self.details_display = False
            self.grid_display = False

        if self.renderer is None:
            self.renderer = 'Zenoss.render.zenpacklib_{zenpack_id_prefix}_entityTypeLinkFromGrid' \
                if self.render_with_type else 'Zenoss.render.zenpacklib_{zenpack_id_prefix}_entityLinkFromGrid'

            self.renderer = self.renderer.format(zenpack_id_prefix=self.class_.zenpack.id_prefix)

    @property
    def zenrelations_tuple(self):
        return (self.name, self.schema)

    @property
    def remote_classname(self):
        return self.schema.remoteClass.split('.')[-1]

    @property
    def iinfo_schemas(self):
        """Return IInfo attribute schema dict."""
        remote_spec = self.class_.zenpack.classes.get(self.remote_classname)
        imported_class = self.class_.zenpack.imported_classes.get(self.schema.remoteClass)
        if not (remote_spec or imported_class):
            return {}

        schemas = {}

        if not self.details_display:
            return {}

        if imported_class:
            remote_spec = imported_class
            remote_spec.label = remote_spec.meta_type

        if isinstance(self.schema, (ToOne)):
            schemas[self.name] = schema.Entity(
                title=_t(self.label or remote_spec.label),
                group="Relationships",
                order=self.order or 3.0)
        else:
            relname_count = '{}_count'.format(self.name)
            schemas[relname_count] = schema.Int(
                title=_t(u'Number of {}'.format(self.label or remote_spec.plural_label)),
                group="Relationships",
                order=self.order or 6.0)

        return schemas

    @property
    def info_properties(self):
        """Return Info properties dict."""
        properties = {}

        if isinstance(self.schema, (ToOne)):
            properties[self.name] = RelationshipInfoProperty(self.name)
        else:
            relname_count = '{}_count'.format(self.name)
            properties[relname_count] = RelationshipLengthProperty(self.name)

        return properties

    @property
    def js_fields(self):
        """Return list of JavaScript fields."""
        remote_spec = self.class_.zenpack.classes.get(self.remote_classname)

        # do not show if grid turned off
        if self.grid_display is False:
            return []

        # No reason to show a column for the device since we're already
        # looking at the device.
        if not remote_spec or remote_spec.is_device:
            return []

        # Don't include containing relationships. They're handled by
        # the class.
        if issubclass(self.schema.remoteType, ToManyCont):
            return []

        if isinstance(self.schema, ToOne):
            fieldname = self.name
        else:
            fieldname = '{}_count'.format(self.name)

        return ["{{name: '{}'}}".format(fieldname)]

    @property
    def js_columns_width(self):
        """Return integer pixel width of JavaScript columns."""
        if not self.grid_display:
            return 0

        remote_spec = self.class_.zenpack.classes.get(self.remote_classname)

        # No reason to show a column for the device since we're already
        # looking at the device.
        if not remote_spec or remote_spec.is_device:
            return 0

        if isinstance(self.schema, ToOne):
            return max(
                (self.content_width or remote_spec.content_width) + 14,
                (self.label_width or remote_spec.label_width) + 20)
        else:
            return (self.label_width or remote_spec.plural_label_width) + 20

    @property
    def js_columns(self):
        """Return list of JavaScript columns."""
        if not self.grid_display:
            return []

        remote_spec = self.class_.zenpack.classes.get(self.remote_classname)

        # No reason to show a column for the device since we're already
        # looking at the device.
        if not remote_spec or remote_spec.is_device:
            return []

        # Don't include containing relationships. They're handled by
        # the class.
        if issubclass(self.schema.remoteType, ToManyCont):
            return []

        if isinstance(self.schema, ToOne):
            fieldname = self.name
            header = self.short_label or self.label or remote_spec.short_label
            renderer = self.renderer
        else:
            fieldname = '{}_count'.format(self.name)
            header = self.short_label or self.label or remote_spec.plural_short_label
            renderer = None

        column_fields = [
            "id: '{}'".format(fieldname),
            "dataIndex: '{}'".format(fieldname),
            "header: _t('{}')".format(header),
            "width: {}".format(self.js_columns_width),
            ]

        if renderer:
            column_fields.append("renderer: {}".format(renderer))

        return [
            OrderAndValue(
                order=self.order or remote_spec.order,
                value='{{{}}}'.format(','.join(column_fields))),
            ]

