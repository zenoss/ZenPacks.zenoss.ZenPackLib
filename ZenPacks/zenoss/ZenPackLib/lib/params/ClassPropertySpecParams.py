##############################################################################
#
# Copyright (C) Zenoss, Inc. 2016, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################
from Acquisition import aq_base
from .SpecParams import SpecParams
from ..spec.ClassPropertySpec import ClassPropertySpec


class ClassPropertySpecParams(SpecParams, ClassPropertySpec):
    """ClassPropertySpecParams"""

    def __init__(self, class_spec, name, **kwargs):
        SpecParams.__init__(self, **kwargs)
        self.name = name

    @classmethod
    def get_prop_default(self, type_):
        return {'string': '',
                'password': '',
                'lines': [],
                'boolean': False,
            }.get(type_, None)

    @classmethod
    def fromObject(cls, ob, id):
        """Generate SpecParams from example object and list of properties"""
        self = object.__new__(cls)
        SpecParams.__init__(self)

        ob = aq_base(ob)
        proto = self.get_prototype(ob)

        self.name = id

        entry = next((p for p in proto._properties if p['id'] == id), {})
        if entry:
            self.type_ = entry.get('type', 'string')
            self.label = entry.get('label')
            if self.label == self.name:
                self.label = None
            if entry.get('mode', '') == 'w':
                self.editable = True

            value = getattr(ob, id, None)
            default = cls.get_prop_default(self.type_)
            self.default = value
            if value == default:
                self.default = None
            else:
                self.default = value
            if proto.__class__.__name__ == 'BasicComponent':
                print "{}: {} ({}), {} ({})".format(id, value, type(value), default, type(default))

        return self
