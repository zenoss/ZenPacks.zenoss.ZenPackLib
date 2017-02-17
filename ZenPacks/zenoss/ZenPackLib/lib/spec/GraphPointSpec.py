##############################################################################
#
# Copyright (C) Zenoss, Inc. 2016, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################
from Products.ZenModel.GraphDefinition import GraphDefinition
from Products.ZenModel.GraphPoint import GraphPoint
from Products.ZenModel.DataPointGraphPoint import DataPointGraphPoint
from Products.ZenModel.ComplexGraphPoint import ComplexGraphPoint
from Products.ZenModel.ThresholdGraphPoint import ThresholdGraphPoint
from Products.ZenModel.DefGraphPoint import DefGraphPoint
from Products.ZenModel.VdefGraphPoint import VdefGraphPoint
from Products.ZenModel.CdefGraphPoint import CdefGraphPoint
from Products.ZenModel.PrintGraphPoint import PrintGraphPoint
from Products.ZenModel.GprintGraphPoint import GprintGraphPoint
from Products.ZenModel.CommentGraphPoint import CommentGraphPoint
from Products.ZenModel.VruleGraphPoint import VruleGraphPoint
from Products.ZenModel.HruleGraphPoint import HruleGraphPoint
from Products.ZenModel.LineGraphPoint import LineGraphPoint
from Products.ZenModel.AreaGraphPoint import AreaGraphPoint
from Products.ZenModel.TickGraphPoint import TickGraphPoint
from Products.ZenModel.ShiftGraphPoint import ShiftGraphPoint
from ..base.types import Color
from .Spec import Spec
from collections import OrderedDict

class GraphPointSpec(Spec):
    """TODO."""

    def __init__(
            self,
            graph_spec,
            name,
            sequence=None,
            isThreshold=False,
            instruct_type=None,
            includeThresholds=False,
            thresholdLegends=None,
            extra_params={},
            _source_location=None,
            zplog=None
            ):
        """
        Create a GraphPoint Specification
            :param sequence: Order that this point is rendered
            :type sequence: int
            :param isThreshold: Whether or not this is a threshold
            :type isThreshold: bool
            :param instruct_type: Instruction for custom graph point type
            :type instruct_type: str
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

        # basic GraphPoint params
        self.graph_spec = graph_spec
        self.name = name
        self.sequence = sequence
        self.isThreshold = isThreshold
        self.instruct_type = instruct_type
        self.extra_params = extra_params

        # Whether to include related thresholds in the graph
        self.includeThresholds = includeThresholds
        # dictionary of threshold legend attributes
        self.thresholdLegends = thresholdLegends


    # this probably should be moved to Spec.py and used throughout
    @property
    def extra_params(self):
        """"""
        return self._extra_params

    @extra_params.setter
    def extra_params(self, value):
        self._extra_params = OrderedDict()
        if value is None:
            value = {}
        for k, v in value.items():
            setattr(self, k, v)
            # set the extra param to the cleaned value
            self._extra_params[k] = getattr(self, k)

    @property
    def lineType(self):
        return self._lineType

    @lineType.setter
    def lineType(self, value):
        value = value.upper()
        valid_linetypes = [x[1] for x in DataPointGraphPoint.lineTypeOptions]
        if value not in valid_linetypes:
            raise ValueError("'{}' is not a valid graphpoint lineType. Valid lineTypes: {}".format(
                                 value, ', '.join(valid_linetypes)))
        self._lineType = value

    @property
    def colorindex(self):
        """
        Allow color to be specified by color_index instead of directly. This is
        useful when you want to keep the normal progression of colors, but need
        to add some DONTDRAW graphpoints for calculations.
        """
        return self._colorindex

    @colorindex.setter
    def colorindex(self, value):
        if not isinstance(value, int):
            raise ValueError("graphpoint colorindex must be numeric. (got {})".format(value))
        self._colorindex = value
        indexed = value % len(GraphPoint.colors)
        self.color = GraphPoint.colors[indexed].lstrip('#')

    @property
    def color(self):
        return self._color

    @color.setter
    def color(self, value):
        if value:
            Color.LOG = self.LOG
        self._color = Color(value)

    @property
    def dpName(self):
        return self._dpName

    @dpName.setter
    def dpName(self, value):
        if value and len(value.split('_')) == 1:
            self._dpName = '{0}_{0}'.format(value)
        else:
            self._dpName = value

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

    @property
    def instruct_type(self):
        return self._instruct_type

    @instruct_type.setter
    def instruct_type(self, value):
        self._instruct_type = value
        if value:
            instruct_types = self.get_instruct_types()
            if value not in instruct_types:
                raise ValueError("{} is an invalid instruction type. Valid types: {}".format(
                             value, ', '.join(instruct_types.keys())))

    def get_instruct_types(self):
        """return dictionary of instructions and related classes"""
        ob = GraphDefinition('tmp')
        return dict([(x[1], eval(x[0])) for x in ob.getGraphPointOptions()])

    def get_point_type(self):
        """return appropriate graphpoint subclass"""
        # if types not provided, assume it's the default or a threshold
        if not self.instruct_type:
            if not self.isThreshold:
                return DataPointGraphPoint
            else:
                return ThresholdGraphPoint
        else:
            graphpoint_types = self.get_instruct_types()
            return graphpoint_types.get(self.instruct_type, DataPointGraphPoint)

    # probably should be moved to Spec
    def update_instance_attributes(self, ob):
        """
            Set extra_params attributes on created objects, 
            preferring any property setter method override versions
        """
        for k, v in self.extra_params.items():
            setattr(ob, k, getattr(self, k, v))

    def create(self, graph_spec, graph, sequence=None):
        type_ = self.get_point_type()
        if not type_:
            raise ValueError("{} - {} cannot be created. Valid types: {}" % (
                        graph_spec.name, self.name, ', '.join(self.get_instruct_types().keys())))

        graphpoint = graph.createGraphPoint(type_, self.name)

        self.update_instance_attributes(graphpoint)

        # threshold sequence is set to -1 by default
        if not self.isThreshold:
            if sequence or self.sequence:
                graphpoint.sequence = self.sequence or sequence 

        if self.includeThresholds:
            thresh_gps = graph.addThresholdsForDataPoint(self.dpName)
            for thresh_gp in thresh_gps:
                entry = self.thresholdLegends.get(thresh_gp.id)
                if not entry:
                    continue
                legend = entry.get('legend')
                color = entry.get('color')
                if legend:
                    thresh_gp.legend = legend
                if color:
                    thresh_gp.color = str(color)
