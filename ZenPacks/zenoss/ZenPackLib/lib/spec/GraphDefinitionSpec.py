##############################################################################
#
# Copyright (C) Zenoss, Inc. 2016, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################
from Products.ZenModel.CommentGraphPoint import CommentGraphPoint
from .Spec import Spec
from .GraphPointSpec import GraphPointSpec


class GraphDefinitionSpec(Spec):
    """GraphDefinitionSpec"""

    def __init__(
            self,
            template_spec,
            name,
            height=None,
            width=None,
            units=None,
            log=None,
            base=None,
            miny=None,
            maxy=None,
            custom=None,
            hasSummary=None,
            graphpoints=None,
            comments=None,
            _source_location=None,
            zplog=None,
            ):
        """
        Create a GraphDefinition Specification

        :param height TODO
        :type height: int
        :param width TODO
        :type width: int
        :param units TODO
        :type units: str
        :param log TODO
        :type log: bool
        :param base TODO
        :type base: bool
        :param miny TODO
        :type miny: int
        :param maxy TODO
        :type maxy: int
        :param custom: TODO
        :type custom: str
        :param hasSummary: TODO
        :type hasSummary: bool
        :param graphpoints: TODO
        :type graphpoints: SpecsParameter(GraphPointSpec)
        :param comments: TODO
        :type comments: list(str)
        """
        super(GraphDefinitionSpec, self).__init__(_source_location=_source_location)
        if zplog:
            self.LOG = zplog
        self.template_spec = template_spec
        self.name = name

        self.height = height
        self.width = width
        self.units = units
        self.log = log
        self.base = base
        self.miny = miny
        self.maxy = maxy
        self.custom = custom
        self.hasSummary = hasSummary
        self.graphpoints = self.specs_from_param(
            GraphPointSpec, 'graphpoints', graphpoints, zplog=self.LOG)
        self.comments = comments

        # TODO fix comments parsing - must always be a list.

    def create(self, templatespec, template, sequence=None):
        graph = template.manage_addGraphDefinition(self.name)
        self.speclog.debug("adding graph")

        if sequence:
            graph.sequence = sequence
        if self.height is not None:
            graph.height = self.height
        if self.width is not None:
            graph.width = self.width
        if self.units is not None:
            graph.units = self.units
        if self.log is not None:
            graph.log = self.log
        if self.base is not None:
            graph.base = self.base
        if self.miny is not None:
            graph.miny = self.miny
        if self.maxy is not None:
            graph.maxy = self.maxy
        if self.custom is not None:
            graph.custom = self.custom
        if self.hasSummary is not None:
            graph.hasSummary = self.hasSummary

        graphpoint_sequence = 0
#         if self.comments:
#             self.speclog.debug("adding {} comments".format(len(self.comments)))
#             for comment_text in self.comments:
#                 graphpoint_sequence += 1
#                 comment = graph.createGraphPoint(
#                     CommentGraphPoint,
#                     'comment-{}'.format(graphpoint_sequence))
#
#                 comment.text = comment_text

        self.speclog.debug("adding {} graphpoints".format(len(self.graphpoints)))
        for graphpoint_id, graphpoint_spec in self.graphpoints.items():
            graphpoint_sequence += 1
            graphpoint_spec.create(self, graph, sequence=graphpoint_sequence)
