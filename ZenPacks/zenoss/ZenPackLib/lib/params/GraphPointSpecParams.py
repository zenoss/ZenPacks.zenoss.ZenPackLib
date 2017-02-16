##############################################################################
#
# Copyright (C) Zenoss, Inc. 2016, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################
from Acquisition import aq_base
from Products.ZenModel.ThresholdGraphPoint import ThresholdGraphPoint
from ..spec.GraphPointSpec import GraphPointSpec
from .SpecParams import SpecParams


class GraphPointSpecParams(SpecParams, GraphPointSpec):
    def __init__(self, template_spec, name, **kwargs):
        SpecParams.__init__(self, **kwargs)
        self.name = name

    @classmethod
    def fromObject(cls, graphpoint, graphdefinition):
        self = object.__new__(cls)
        SpecParams.__init__(self)
        graphpoint = aq_base(graphpoint)
        graphdefinition = aq_base(graphdefinition)
        sample_gp = graphpoint.__class__(graphpoint.id)

        for propname in ('lineType', 'lineWidth', 'stacked', 'format',
                         'legend', 'limit', 'rpn', 'cFunc', 'color', 'dpName', 'threshId'):
            if hasattr(sample_gp, propname):
                setattr(self, '_%s_defaultvalue' % propname, getattr(sample_gp, propname))
            if getattr(graphpoint, propname, None) != getattr(sample_gp, propname, None):
                setattr(self, propname, getattr(graphpoint, propname, None))

        return self
