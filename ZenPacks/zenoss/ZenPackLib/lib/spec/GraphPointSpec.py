##############################################################################
#
# Copyright (C) Zenoss, Inc. 2016, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################
from Products.ZenModel.GraphPoint import GraphPoint
from collections import OrderedDict
from Products.ZenModel.DataPointGraphPoint import DataPointGraphPoint
from Products.ZenModel.ComplexGraphPoint import ComplexGraphPoint
from Products.ZenModel.CommentGraphPoint import CommentGraphPoint
from Products.ZenModel.ThresholdGraphPoint import ThresholdGraphPoint
from ..base.types import Color
from .Spec import Spec

GRAPHPOINT_TYPES = {'DataPointGraphPoint': DataPointGraphPoint,
                    'CommentGraphPoint': CommentGraphPoint,
                    'ThresholdGraphPoint': ThresholdGraphPoint, }


class GraphPointSpec(Spec):
    """GraphPointSpec"""

    def __init__(
            self,
            template_spec,
            name,
            type_='DataPointGraphPoint',
            sequence=0,
            colorindex=None,
            color=None,
            includeThresholds=False,
            thresholdLegends=None,
            extra_params=None,
            _source_location=None,
            zplog=None
            ):
        """
        Create a GraphPoint Specification
        
            :param type_: TODO
            :type type_: str
            :yaml_param type_: type
            :param sequence: Order of graph point in graph
            :type sequence: int
            :param color: TODO    
            :type color: str    
            :param colorindex: TODO    
            :type colorindex: int
            :param includeThresholds: TODO
            :type includeThresholds: bool
            :param thresholdLegends: map of {thresh_id: {legend: TEXT, color: HEXSTR}
            :type thresholdLegends: dict(str)
            :param extra_params: Additional parameters that may be used by subclasses of GraphPoint
            :type extra_params: ExtraParams
        """
        super(GraphPointSpec, self).__init__(_source_location=_source_location)
        if zplog:
            self.LOG = zplog

        self.template_spec = template_spec
        self.name = name

        self.type_ = type_

        self.sequence = sequence

        self.color = color
        if color:
            print "GOT COLOR", self.name, color, Color(color)
            Color.LOG = self.LOG
            self.color = Color(color)

        # Allow color to be specified by color_index instead of directly. This is
        # useful when you want to keep the normal progression of colors, but need
        # to add some DONTDRAW graphpoints for calculations.
        self.colorindex = colorindex
        if colorindex:
            try:
                colorindex = int(colorindex) % len(GraphPoint.colors)
            except (TypeError, ValueError):
                raise ValueError("graphpoint colorindex must be numeric.")

            self.color = GraphPoint.colors[colorindex].lstrip('#')

        self.includeThresholds = includeThresholds
        self.thresholdLegends = thresholdLegends

        if extra_params is None:
            self.extra_params = OrderedDict()
        else:
            self.extra_params = extra_params
            self.validate_extra_params()

    def validate_extra_params(self):
        """Perform input validation for extra paramters"""
        # Shorthand for datapoints that have the same name as their datasource.
        dpName = self.extra_params.get('dpName')
        if dpName is not None and '_' not in dpName:
            self.extra_params['dpName'] = '{0}_{0}'.format(dpName)

        lineType = self.extra_params.get('lineType')
        # Validate lineType.
        if lineType:
            valid_linetypes = [x[1] for x in ComplexGraphPoint.lineTypeOptions]
            if lineType.upper() in valid_linetypes:
                self.extra_params['lineType'] = lineType.upper()
            else:
                raise ValueError("'%s' is not a valid graphpoint lineType. Valid lineTypes: %s" % (
                                 lineType, ', '.join(valid_linetypes)))

        # Consolidation function validation
        cFunc = self.extra_params.get('cFunc')
        if cFunc is not None:
            if cFunc not in ['AVERAGE', 'MIN', 'MAX', 'LAST']:
                self.extra_params['cFunc'] = 'AVERAGE'

    @property
    def thresholdLegends(self):
        return self._thresholdLegends

    @thresholdLegends.setter
    def thresholdLegends(self, value):
        if value is None:
            self._thresholdLegends = {}
        elif isinstance(value, dict):
            self._thresholdLegends = value
        elif isinstance(value, str):
            self.LOG.debug('setting default thresholdLegends for {}'.format(value))
            self._thresholdLegends = {value: None}
        else:
            raise ValueError("thresholdLegends must be specified as a dict or string (got {})".format(value))
        for id, data in self._thresholdLegends.items():
            if not isinstance(data, dict):
                data = {'legend': None, 'color': None}
            self._thresholdLegends[id]['legend'] = data.get('legend')
            self._thresholdLegends[id]['color'] = data.get('color')

    def create(self, graph_spec, graph, sequence=None):

        type_ = GRAPHPOINT_TYPES.get(self.type_)

        graphpoint = graph.createGraphPoint(type_, self.name)
        self.speclog.debug("adding graphpoint")

        seq = self.sequence or sequence
        if seq is not None:
            graphpoint.sequence = seq
        if self.color is not None:
            graphpoint.color = self.color

        if self.extra_params:
            for param, value in self.extra_params.iteritems():
                if param in [x['id'] for x in graphpoint._properties]:
                    setattr(graphpoint, param, value)
                else:
                    raise ValueError("%s is not a valid property for graphoint of type %s" % (param, type_))

        if self.includeThresholds:
            dpName = self.extra_params.get('dpName')
            if dpName:
                thresh_gps = graph.addThresholdsForDataPoint(dpName)
                for thresh_gp in thresh_gps:
                    entry = self.thresholdLegends.get(thresh_gp.id)
                    if not entry:
                        continue
                    legend = entry.get('legend')
                    color = entry.get('color')
                    if legend:
                        thresh_gp.legend = legend
                        thresh_gp.threshId = legend
                    if color:
                        thresh_gp.color = str(color)
