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
from collections import OrderedDict

class GraphPointSpecParams(SpecParams, GraphPointSpec):
    def __init__(self, graph_spec, name, **kwargs):
        SpecParams.__init__(self, **kwargs)
        self.name = name

    @classmethod
    def fromObject(cls, graphpoint, graphdefinition):
        self = object.__new__(cls)
        SpecParams.__init__(self)
        graphpoint = aq_base(graphpoint)
        graphdefinition = aq_base(graphdefinition)
        sample_gp = graphpoint.__class__(graphpoint.id)

        for propname in ('sequence', 'isThreshold', 'instruct_type', 'includeThresholds',
                         'thresholdLegends'):
            if hasattr(sample_gp, propname):
                setattr(self, '_%s_defaultvalue' % propname, getattr(sample_gp, propname))
            if getattr(graphpoint, propname, None) != getattr(sample_gp, propname, None):
                setattr(self, propname, getattr(graphpoint, propname, None))

        # any custom object properties not defined in the spec will go in extra_params
        self.extra_params = OrderedDict()
        ob_propnames = [x['id'] for x in graphpoint._properties if x['id'] not in cls.init_params]
        for propname in ob_propnames:
            if getattr(graphpoint, propname, None) != getattr(sample_gp, propname, None):
                self.extra_params[propname] = getattr(graphpoint, propname, None)

        threshold_graphpoints = [x for x in graphdefinition.graphPoints() if isinstance(x, ThresholdGraphPoint)]

        self.includeThresholds = False
        if threshold_graphpoints:
            thresholds = {x.id: x for x in graphpoint.graphDef().rrdTemplate().thresholds()}
            for tgp in threshold_graphpoints:
                threshold = thresholds.get(tgp.threshId, None)
                if threshold:
                    if graphpoint.dpName in threshold.dsnames:
                        self.includeThresholds = True

        return self
