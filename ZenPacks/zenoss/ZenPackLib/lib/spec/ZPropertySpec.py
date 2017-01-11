##############################################################################
#
# Copyright (C) Zenoss, Inc. 2016, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################
from Products.ZenRelations.zPropertyCategory import setzPropertyCategory
from ..base.ClassProperty import ClassProperty
from .Spec import Spec
import inspect
from collections import OrderedDict
import re


class ZPropertySpec(Spec):
    """ZPropertySpec"""
    _default = None

    def __init__(
            self,
            zenpack_spec,
            name,
            type_='string',
            default=None,
            category=None,
            _source_location=None,
            zplog=None
            ):
        """
            Create a ZProperty Specification

            :param type_: ZProperty Type (boolean, int, float, string, password, or lines)
            :yaml_param type_: type
            :type type_: str
            :param default: Default Value
            :type default: ZPropertyDefaultValue
            :param category: ZProperty Category.  This is used for display/sorting purposes.
            :type category: str
        """
        super(ZPropertySpec, self).__init__(_source_location=_source_location)
        if zplog:
            self.LOG = zplog

        self.zenpack_spec = zenpack_spec
        self.name = name
        self.type_ = type_
        self.category = category
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

    def create(self):
        """Implement specification."""
        if self.category:
            setzPropertyCategory(self.name, self.category)

    @property
    def packZProperties(self):
        """Return packZProperties tuple for this zProperty."""
        return (self.name, self.default, self.type_)
#
#     @ClassProperty
#     @classmethod
#     def init_params(cls):
#         # if not cls._init_params:
#             return cls.get_init_params()
#         # return cls._init_params
#
#     # @classmethod
#     # def get_init_params(cls):
#         # params = super(ZPropertySpec, cls).get_init_params()
#
#         # params['type_']['type'] = cls.type_
#         # params['default']['default'] = self.get_default()
#
#         # return params
#
#     @classmethod
#     def get_init_params(cls):
#         """Return a dictionary describing the parameters accepted by __init__"""
#         # import pdb ; pdb.set_trace()
#         argspec = inspect.getargspec(cls.__init__)
#         if argspec.defaults:
#             defaults = dict(zip(argspec.args[-len(argspec.defaults):], argspec.defaults))
#         else:
#             defaults = {}
#
#         params = OrderedDict()
#         for op, param, value in re.findall(
#             "^\s*:(type|param|yaml_param|yaml_block_style)\s+(\S+):\s*(.*)$",
#             cls.__init__.__doc__,
#             flags=re.MULTILINE
#         ):
#             print op, param
#             if param not in params:
#                 params[param] = {'description': None,
#                                  'type': None,
#                                  'yaml_param': param,
#                                  'yaml_block_style': False}
#                 if param in defaults:
#                     params[param]['default'] = defaults[param]
#
#             if op == 'type':
#                 params[param]['type'] = value
#
#                 if 'default' not in params[param] or \
#                    params[param]['default'] is None:
#                     # For certain types, we know that None doesn't really mean
#                     # None.
#                     if params[param]['type'].startswith("dict"):
#                         params[param]['default'] = {}
#                     elif params[param]['type'].startswith("list"):
#                         params[param]['default'] = []
#                     elif params[param]['type'].startswith("SpecsParameter("):
#                         params[param]['default'] = {}
#             elif op == 'yaml_param':
#                 params[param]['yaml_param'] = value
#             elif op == 'yaml_block_style':
#                 params[param]['yaml_block_style'] = bool(value)
#             else:
#                 params[param]['description'] = value
#
#         return params
