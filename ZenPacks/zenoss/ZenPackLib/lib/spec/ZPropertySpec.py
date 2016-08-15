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
from ..functions import LOG


class ZPropertySpec(Spec):
    """ZPropertySpec"""

    LOG = LOG

    def __init__(
            self,
            zenpack_spec,
            name,
            type_='string',
            default=None,
            category=None,
            _source_location=None,
            log=LOG
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
        self.LOG=log

        self.zenpack_spec = zenpack_spec
        self.name = name
        self.type_ = type_
        self.category = category

        if default is None:
            self.default = {
                'string': '',
                'password': '',
                'lines': [],
                'boolean': False,
                }.get(self.type_, None)
        else:
            self.default = default

    def create(self):
        """Implement specification."""
        if self.category:
            setzPropertyCategory(self.name, self.category)

    @property
    def packZProperties(self):
        """Return packZProperties tuple for this zProperty."""
        return (self.name, self.default, self.type_)

