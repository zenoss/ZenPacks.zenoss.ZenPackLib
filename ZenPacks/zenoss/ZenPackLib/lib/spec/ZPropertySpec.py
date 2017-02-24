##############################################################################
#
# Copyright (C) Zenoss, Inc. 2016, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################
from Products.ZenRelations.zPropertyCategory import setzPropertyCategory
from .Spec import Spec


class ZPropertySpec(Spec):
    """ZPropertySpec"""

    def __init__(
            self,
            zenpack_spec,
            name,
            type_='string',
            default=None,
            category=None,
            label=None,
            description='',
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
            :param label: ZProperty Label.  This is used for display/sorting purposes.
            :type label: str
            :param description: ZProperty Label.  This is used for display/sorting purposes.
            :type description: str
        """
        super(ZPropertySpec, self).__init__(_source_location=_source_location)
        if zplog:
            self.LOG = zplog

        self.zenpack_spec = zenpack_spec
        self.name = name
        self.type_ = type_
        self.category = category
        self.label = label or name
        self.description = description

        if default is None:
            self.default = self.get_default()
        else:
            self.default = default

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

    @property
    def packZProperties_data(self):
        """Return packZProperties_data dict for this zProperty."""
        return {self.name: {'label': self.label, 'description': self.description, 'type': self.type_}}

