##############################################################################
#
# Copyright (C) Zenoss, Inc. 2016, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################
from Acquisition import aq_base
from Products.ZenRelations.zPropertyCategory import getzPropertyCategory
from .SpecParams import SpecParams
from ..spec.ZPropertySpec import ZPropertySpec

class ZPropertySpecParams(SpecParams, ZPropertySpec):
    def __init__(self, zenpack_spec, name, **kwargs):
        SpecParams.__init__(self, **kwargs)
        self.name = name

    @classmethod
    def fromObject(cls, id, deviceclass):
        """Generate SpecParams from example object and list of properties"""
        self = object.__new__(cls)
        SpecParams.__init__(self)

        deviceclass = aq_base(deviceclass)

        self.name = id
#         entry = next((p.get('type', 'string') for p in deviceclass._properties if p['id'] == id), 'string')
#
#         self.type_ = entry
#
#         self.default = getattr(deviceclass, id)
#
#         self.category = getzPropertyCategory(id)

        return self

    @classmethod
    def fromTuple(cls, tuple):
        """Generate SpecParams from tuple entry in ZenPack. packZProperties"""
        self = object.__new__(cls)
        SpecParams.__init__(self)

        name, default, type = tuple
        self.name = name
        self.type_ = type
        self.default = default

        self.category = getzPropertyCategory(self.name)

        return self
