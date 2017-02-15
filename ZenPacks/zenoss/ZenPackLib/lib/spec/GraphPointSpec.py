##############################################################################
#
# Copyright (C) Zenoss, Inc. 2016, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################
from Products.ZenModel.GraphPoint import GraphPoint
from Products.ZenModel.DataPointGraphPoint import DataPointGraphPoint
from Products.ZenModel.ComplexGraphPoint import ComplexGraphPoint
from Products.ZenModel.ThresholdGraphPoint import ThresholdGraphPoint
from ..base.types import Color
from .Spec import Spec


class GraphPointSpec(Spec):
    """TODO."""

    def __init__(
            self,
            template_spec,
            name=None,
            dpName=None,
            lineType=None,
            lineWidth=None,
            stacked=None,
            format=None,
            legend=None,
            limit=None,
            rpn=None,
            cFunc=None,
            colorindex=None,
            color=None,
            includeThresholds=False,
            thresholdLegends=None,
            _source_location=None,
            zplog=None
            ):
        """
        Create a GraphPoint Specification

            :param dpName: TODO
            :type dpName: str
            :param lineType: TODO
            :type lineType: str
            :param lineWidth: TODO
            :type lineWidth: int
            :param stacked: TODO
            :type stacked: bool
            :param format: TODO
            :type format: str
            :param legend: TODO
            :type legend: str
            :param limit: TODO
            :type limit: int
            :param rpn: TODO
            :type rpn: str
            :param cFunc: TODO
            :type cFunc: str
            :param color: TODO
            :type color: str
            :param colorindex: TODO
            :type colorindex: int
            :param includeThresholds: TODO
            :type includeThresholds: bool
            :param thresholdLegends: map of {thresh_id: {legend: TEXT, color: HEXSTR, threshId: TEXT}
            :type thresholdLegends: dict(str)
        """
        super(GraphPointSpec, self).__init__(_source_location=_source_location)
        if zplog:
            self.LOG = zplog

        self.template_spec = template_spec
        self.name = name

        self.lineType = lineType
        self.lineWidth = lineWidth
        self.stacked = stacked
        self.format = format
        self.legend = legend
        self.limit = limit
        self.rpn = rpn
        self.cFunc = cFunc
        self.color = color
        if color:
            Color.LOG = self.LOG
            self.color = Color(color)
        self.includeThresholds = includeThresholds
        self.thresholdLegends = thresholdLegends

        # Shorthand for datapoints that have the same name as their datasource.
        if '_' not in dpName:
            self.dpName = '{0}_{0}'.format(dpName)
        else:
            self.dpName = dpName

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

        # Validate lineType.
        if lineType:
            valid_linetypes = [x[1] for x in ComplexGraphPoint.lineTypeOptions]

            if lineType.upper() in valid_linetypes:
                self.lineType = lineType.upper()
            else:
                raise ValueError("'%s' is not a valid graphpoint lineType. Valid lineTypes: %s" % (
                                 lineType, ', '.join(valid_linetypes)))

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
                data = {'legend': None, 'color': None, 'threshId': None}
            self._thresholdLegends[id]['legend'] = data.get('legend')
            self._thresholdLegends[id]['color'] = data.get('color')
            self._thresholdLegends[id]['threshId'] = data.get('threshId', id)

    def get_threshold_ids(self):
        """find thresholds related to this datapoint"""
        return [t.name for t in self.template_spec.template_spec.thresholds.values() if self.dpName in t.dsnames]

    def create(self, graph_spec, graph, sequence=None):
        graphpoint = graph.createGraphPoint(DataPointGraphPoint, self.name)
        self.speclog.debug("adding graphpoint")

        graphpoint.dpName = self.dpName

        if sequence:
            graphpoint.sequence = sequence
        if self.lineType is not None:
            graphpoint.lineType = self.lineType
        if self.lineWidth is not None:
            graphpoint.lineWidth = self.lineWidth
        if self.stacked is not None:
            graphpoint.stacked = self.stacked
        if self.format is not None:
            graphpoint.format = self.format
        if self.legend is not None:
            graphpoint.legend = self.legend
        if self.limit is not None:
            graphpoint.limit = self.limit
        if self.rpn is not None:
            graphpoint.rpn = self.rpn
        if self.cFunc is not None:
            graphpoint.cFunc = self.cFunc
        if self.color is not None:
            graphpoint.color = str(self.color)

        # build threshold graph points
        if self.includeThresholds:
            thresh_ids = self.get_threshold_ids()
            # if not specified, then create them generically
            if not self.thresholdLegends:
                thresh_gps = graph.addThresholdsForDataPoint(thresh_ids)
            # otherwise proceed and use specified legends
            else:
                for id, data in self.thresholdLegends.items():
                    if id in thresh_ids or data.get('threshId') in thresh_ids:
                        thresh_gp = graph.createGraphPoint(ThresholdGraphPoint, id)
                        thresh_gp.threshId = data.get('threshId') or id
                        legend = data.get('legend')
                        color = data.get('color')
                        if legend:
                            thresh_gp.legend = legend
                        if color:
                            thresh_gp.color = str(color)
