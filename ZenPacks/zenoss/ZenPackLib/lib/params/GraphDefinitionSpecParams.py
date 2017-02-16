##############################################################################
#
# Copyright (C) Zenoss, Inc. 2016, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################
from Acquisition import aq_base
from Products.ZenModel.DataPointGraphPoint import DataPointGraphPoint
from Products.ZenModel.CommentGraphPoint import CommentGraphPoint
from Products.ZenModel.ThresholdGraphPoint import ThresholdGraphPoint

from ..spec.GraphDefinitionSpec import GraphDefinitionSpec
from .SpecParams import SpecParams
from .GraphPointSpecParams import GraphPointSpecParams


class GraphDefinitionSpecParams(SpecParams, GraphDefinitionSpec):
    def __init__(self, template_spec, name, graphpoints=None, **kwargs):
        SpecParams.__init__(self, **kwargs)
        self.name = name
        self.graphpoints = self.specs_from_param(
            GraphPointSpecParams, 'graphpoints', graphpoints, zplog=self.LOG)

    @classmethod
    def fromObject(cls, graphdefinition):
        self = object.__new__(cls)
        SpecParams.__init__(self)
        graphdefinition = aq_base(graphdefinition)
        sample_gd = graphdefinition.__class__(graphdefinition.id)

        for propname in ('height', 'width', 'units', 'log', 'base', 'miny',
                         'maxy', 'custom', 'hasSummary', 'comments'):
            if hasattr(sample_gd, propname):
                setattr(self, '_%s_defaultvalue' % propname, getattr(sample_gd, propname))
            if getattr(graphdefinition, propname, None) != getattr(sample_gd, propname, None):
                setattr(self, propname, getattr(graphdefinition, propname, None))

        datapoint_graphpoints = [x for x in graphdefinition.graphPoints() if isinstance(x, DataPointGraphPoint) or isinstance(x, ThresholdGraphPoint)]
        self.graphpoints = {x.id: GraphPointSpecParams.fromObject(x, graphdefinition) for x in datapoint_graphpoints}

        comment_graphpoints = [x for x in graphdefinition.graphPoints() if isinstance(x, CommentGraphPoint)]
        if comment_graphpoints:
            self.comments = [y.text for y in sorted(comment_graphpoints, key=lambda x: x.id)]

        return self

