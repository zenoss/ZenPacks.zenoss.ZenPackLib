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
from Products.Zuul.infos import ProxyProperty
from ..helpers.OrderAndValue import OrderAndValue
from .Spec import Spec, MethodInfoProperty, EnumInfoProperty


class ClassPropertySpec(Spec):
    """ClassPropertySpec"""

    def __init__(
            self,
            class_spec,
            name,
            type_='string',
            label=None,
            short_label=None,
            index_type=None,
            label_width=80,
            default=None,
            content_width=None,
            display=True,
            details_display=True,
            grid_display=True,
            renderer=None,
            order=100,
            editable=False,
            api_only=False,
            api_backendtype='property',
            enum=None,
            datapoint=None,
            datapoint_default=None,
            datapoint_cached=True,
            index_scope='device',
            _source_location=None,
            zplog=None,
            ):
        """
        Create a Class Property Specification

            :param type_: Property Data Type (TODO (enum))
            :yaml_param type_: type
            :type type_: str
            :param label: Label to use when describing this property in the
                   UI.  If not specified, the default is to use the name of the
                   property.
            :type label: str
            :param short_label: If specified, this is a shorter version of the
                   label, used, for example, in grid table headings.
            :type short_label: str
            :param index_type: TODO (enum)
            :type index_type: str
            :param label_width: Optionally overrides ZPL's label width
                   calculation with a higher value.
            :type label_width: int
            :param default: Default Value
            :type default: ZPropertyDefaultValue
            :param content_width: Optionally overrides ZPL's content width
                   calculation with a higher value.
            :type content_width: int
            :param display: If this is set to False, this property will be
                   hidden from the UI completely.
            :type display: bool
            :param details_display: If this is set to False, this property
                   will be hidden from the "details" portion of the UI.
            :type details_display: bool
            :param grid_display: If this is set to False, this property
                   will be hidden from the "grid" portion of the UI.
            :type grid_display: bool
            :param renderer: Optional name of a javascript renderer to apply
                   to this property, rather than passing the text through
                   unformatted.
            :type renderer: str
            :param order: Rank for sorting this property among other properties
            :type order: int
            :param editable: TODO
            :type editable: bool
            :param api_only: TODO
            :type api_only: bool
            :param api_backendtype: TODO (enum)
            :type api_backendtype: str
            :param enum: TODO
            :type enum: dict
            :param datapoint: TODO (validate datapoint name)
            :type datapoint: str
            :param datapoint_default: TODO  - DEPRECATE (use default instead)
            :type datapoint_default: str
            :param datapoint_cached: TODO
            :type datapoint_cached: bool
            :param index_scope: TODO (enum)
            :type index_scope: str

        """
        super(ClassPropertySpec, self).__init__(_source_location=_source_location)
        if zplog:
            self.LOG = zplog
        self.class_spec = class_spec
        self.name = name
        # self.default = default
        self.type_ = type_
        self.label = label or self.name
        self.short_label = short_label or self.label
        self.index_type = index_type
        self.index_scope = index_scope
        self.label_width = label_width
        self.content_width = content_width or label_width
        self.display = display
        self.details_display = details_display
        self.grid_display = grid_display
        self.renderer = renderer

        if not self.display:
            self.details_display = False
            self.grid_display = False

        # pick an appropriate default renderer for this property.
        if type_ == 'entity' and not self.renderer:
            self.renderer = 'Zenoss.render.zenpacklib_{zenpack_id_prefix}_entityLinkFromGrid'.format(
                zenpack_id_prefix=self.class_spec.zenpack.id_prefix)

        self.editable = bool(editable)
        self.api_only = bool(api_only)
        self.api_backendtype = api_backendtype
        if isinstance(enum, (set, list, tuple)):
            enum = dict(enumerate(enum))
        self.enum = enum
        self.datapoint = datapoint
        self.datapoint_default = datapoint_default
        self.datapoint_cached = bool(datapoint_cached)
        # Force api mode when a datapoint is supplied
        if self.datapoint:
            self.api_only = True
            self.api_backendtype = 'method'

        if self.api_backendtype not in ('property', 'method'):
            raise TypeError(
                "Property '%s': api_backendtype must be 'property' or 'method', not '%s'"
                % (name, self.api_backendtype))

        if self.index_scope not in ('device', 'global', 'both'):
            raise TypeError(
                "Property '%s': index_scope must be 'device', 'global', or 'both', not '%s'"
                % (name, self.index_scope))

        self.order = order

        if default is None:
            self.default = self.get_default()
        else:
            self.default = default
        # print 'HA', self.name, self.type_, self.category, self.default

    def get_default(self):
        return {'string': '',
                'password': '',
                'lines': [],
                'boolean': False,
            }.get(self.type_, None)

    @property
    def scaled_order(self):
        return self.scale_order(scale=1, offset=4)

    def update_inherited_params(self):
        """Copy any inherited parameters if they are not default or already specified here"""
        custom = self.get_custom_params()
        prop_spec = self.class_spec.find_property_in_base_specs(self.name)
        if not prop_spec:
            return
        for k, v in prop_spec.get_custom_params().items():
            if k not in custom:
                setattr(self, k, v)

    @property
    def ofs_dict(self):
        """Return OFS _properties dictionary."""
        if self.api_only:
            return None

        return {
            'id': self.name,
            'label': self.label,
            'type': self.type_,
            }

    @property
    def catalog_indexes(self):
        """Return catalog indexes dictionary."""
        if not self.index_type:
            return {}

        return {
            self.name: {'type': self.index_type,
                        'scope': self.index_scope},
            }

    @property
    def iinfo_schemas(self):
        """Return IInfo attribute schema dict.

        Return None if type has no known schema.

        """
        schema_map = {
            'boolean': schema.Bool,
            'int': schema.Int,
            'float': schema.Float,
            'lines': schema.Text,
            'string': schema.TextLine,
            'password': schema.Password,
            'entity': schema.Entity
            }

        if self.type_ not in schema_map:
            return {}

        if self.details_display is False:
            return {}

        return {
            self.name: schema_map[self.type_](
                title=_t(self.label),
                alwaysEditable=self.editable,
                order=self.scaled_order)
            }

    @property
    def info_properties(self):
        """Return Info properties dict."""
        if self.api_backendtype == 'method':
            isEntity = self.type_ == 'entity'
            return {
                self.name: MethodInfoProperty(self.name, entity=isEntity, enum=self.enum),
                }
        else:
            if not self.enum:
                return {self.name: ProxyProperty(self.name), }
            else:
                return {self.name: EnumInfoProperty(self.name, self.enum), }

    @property
    def js_fields(self):
        """Return list of JavaScript fields."""
        if self.grid_display is False:
            return []
        else:
            return ["{{name: '{}'}}".format(self.name)]

    @property
    def js_columns_width(self):
        """Return integer pixel width of JavaScript columns."""
        if self.grid_display:
            return max(self.content_width + 14, self.label_width + 20)
        else:
            return 0

    @property
    def js_columns(self):
        """Return list of JavaScript columns."""

        if self.grid_display is False:
            return []

        column_fields = [
            "id: '{}'".format(self.name),
            "dataIndex: '{}'".format(self.name),
            "header: _t('{}')".format(self.short_label),
            "width: {}".format(self.js_columns_width),
            ]

        if self.renderer:
            column_fields.append("renderer: {}".format(self.renderer))
        else:
            if self.type_ == 'boolean':
                column_fields.append("renderer: Zenoss.render.checkbox")

        return [
            OrderAndValue(
                order=self.scaled_order,
                value='{{{}}}'.format(',\n                       '.join(column_fields))),
            ]

