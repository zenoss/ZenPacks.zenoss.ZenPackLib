##############################################################################
#
# Copyright (C) Zenoss, Inc. 2016, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################
from Products.ZenRelations.zPropertyCategory import setzPropertyCategory
from ..base.types import Property
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

        self._property = Property(name, type_, default)
        self.name = self._property.name
        self.type_ = self._property.type_
        self.default = self._property.default

        self.category = category
        self.label = label or name
        self.description = description

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

