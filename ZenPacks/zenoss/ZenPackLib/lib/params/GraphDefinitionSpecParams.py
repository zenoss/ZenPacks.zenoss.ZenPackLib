##############################################################################
#
# Copyright (C) Zenoss, Inc. 2016, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################
from collections import OrderedDict
from operator import attrgetter
from Acquisition import aq_base
from Products.ZenModel.DataPointGraphPoint import DataPointGraphPoint
from Products.ZenModel.CommentGraphPoint import CommentGraphPoint

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

        for propname in ('description', 'height', 'width', 'units', 'log',
                         'base', 'miny', 'maxy', 'custom', 'hasSummary',
                         'comments'):
            if hasattr(sample_gd, propname):
                setattr(self, '_%s_defaultvalue' % propname, getattr(sample_gd, propname))
            if getattr(graphdefinition, propname, None) != getattr(sample_gd, propname, None):
                setattr(self, propname, getattr(graphdefinition, propname, None))

        graphpoints = sorted(graphdefinition.graphPoints(), key=attrgetter('sequence'))

        self.graphpoints = OrderedDict([(x.id, GraphPointSpecParams.fromObject(x, graphdefinition)) for x in graphpoints])

        return self

