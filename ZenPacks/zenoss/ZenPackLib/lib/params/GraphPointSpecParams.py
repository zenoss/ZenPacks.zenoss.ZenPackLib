##############################################################################
#
# Copyright (C) Zenoss, Inc. 2016, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################
from collections import OrderedDict
from Acquisition import aq_base
from Products.ZenModel.ThresholdGraphPoint import ThresholdGraphPoint
from ..spec.GraphPointSpec import GraphPointSpec
from .SpecParams import SpecParams


class GraphPointSpecParams(SpecParams, GraphPointSpec):

    def __init__(self, template_spec, name, **kwargs):
        SpecParams.__init__(self, **kwargs)
        GraphPointSpec.__init__(self, template_spec, name, **kwargs)

    @classmethod
    def fromObject(cls, graphpoint, graphdefinition):
        self = object.__new__(cls)
        SpecParams.__init__(self)
        graphpoint = aq_base(graphpoint)
        graphdefinition = aq_base(graphdefinition)
        sample_gp = graphpoint.__class__(graphpoint.id)

        self.type_ = graphpoint.__class__.__name__

        self.extra_params = OrderedDict()

        ordered = ('lineType', 'lineWidth', 'stacked', 'format',
            'legend', 'limit', 'rpn', 'cFunc', 'color', 'dpName')

        for propname in ordered:
            default_value = getattr(sample_gp, propname, None)
            ob_value = getattr(graphpoint, propname, None)
            if propname in self.init_params:
                # set the default value for this spec attribute
                if hasattr(sample_gp, propname):
                    setattr(self, '_%s_defaultvalue' % propname, default_value)
                # set the value locally if different from class default
                if ob_value != default_value:
                    setattr(self, propname, ob_value)
            # property must belong in extra_params
            else:
                # set the value locally if different from class default
                if ob_value != default_value:
                    self.extra_params[propname] = ob_value

        # now get other extra_params
        for propname in [x['id'] for x in graphpoint._properties if x['id'] not in ordered]:
            if propname in self.init_params:
                continue
            default_value = getattr(sample_gp, propname, None)
            ob_value = getattr(graphpoint, propname, None)
            if ob_value != default_value:
                self.extra_params[propname] = ob_value

        return self
