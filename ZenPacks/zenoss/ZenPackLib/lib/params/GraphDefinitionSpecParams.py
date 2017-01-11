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
    def fromObject(cls, ob):
        self = super(GraphDefinitionSpecParams, cls).fromObject(ob)

        ob = aq_base(ob)

        datapoint_graphpoints = [x for x in ob.graphPoints() if isinstance(x, DataPointGraphPoint)]
        self.graphpoints = {x.id: GraphPointSpecParams.fromObject(x, ob) for x in datapoint_graphpoints}

        comment_graphpoints = [x for x in ob.graphPoints() if isinstance(x, CommentGraphPoint)]
        if comment_graphpoints:
            self.comments = [y.text for y in sorted(comment_graphpoints, key=lambda x: x.id)]

        return self
