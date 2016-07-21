import collections
from Acquisition import aq_base
from .SpecParams import SpecParams
from ..spec.RRDThresholdSpec import RRDThresholdSpec


class RRDThresholdSpecParams(SpecParams, RRDThresholdSpec):
    def __init__(self, template_spec, name, foo=None, **kwargs):
        SpecParams.__init__(self, **kwargs)
        self.name = name

    @classmethod
    def fromObject(cls, threshold):
        self = object.__new__(cls)
        SpecParams.__init__(self)
        threshold = aq_base(threshold)
        sample_th = threshold.__class__(threshold.id)

        for propname in ('dsnames', 'eventClass', 'severity', 'type_'):
            if hasattr(sample_th, propname):
                setattr(self, '_%s_defaultvalue' % propname, getattr(sample_th, propname))
            if getattr(threshold, propname, None) != getattr(sample_th, propname, None):
                setattr(self, propname, getattr(threshold, propname, None))

        self.extra_params = collections.OrderedDict()
        for propname in [x['id'] for x in threshold._properties]:
            if propname not in self.init_params():
                if getattr(threshold, propname, None) != getattr(sample_th, propname, None):
                    self.extra_params[propname] = getattr(threshold, propname, None)

        return self

