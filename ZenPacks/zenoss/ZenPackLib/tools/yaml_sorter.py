#! /usr/bin/python
##############################################################################
# Copyright (C) Zenoss, Inc. 2017, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
##############################################################################

"""
This tool will re-order the YAML that is created by dump tools to make it more
human readable. It will not reorder any order-critical sections:
(ie. datasources, graphs, graphpoints, thresholds will not be reordered).
Only sections that are explicitly specified are reordered, not sub-sections

This script will :
* Write the entire ZPL yaml structure into a nested Ordered Dict.
    * Looking for sections to reorder, create new reordered copies of the topmost structure
    * All other sections are copied as is in their original order
    * Upon finish, writes out the resulting data
    * Unrap inline-list format to YAML dash-style formatted lists

    NOTE: This has only been tested on YAML with the following structure:
          ('name', 'zProperties', 'device_classes', 'event_classes')
"""

import sys
import yaml
import os
import re
from collections import OrderedDict


class MyDumper(yaml.Dumper):
    def increase_indent(self, flow=False, indentless=False):
        return super(MyDumper, self).increase_indent(flow, False)


def ordered_load(stream, Loader=yaml.Loader, object_pairs_hook=OrderedDict):
    class OrderedLoader(Loader):
        pass

    def construct_mapping(loader, node):
        loader.flatten_mapping(node)
        return object_pairs_hook(loader.construct_pairs(node))
    OrderedLoader.add_constructor(
        yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
        construct_mapping)
    return yaml.load(stream, OrderedLoader)


def ordered_dump(data, stream=None, Dumper=MyDumper, **kwds):
    class OrderedDumper(Dumper):
        pass

    def _dict_representer(dumper, data):
        return dumper.represent_mapping(
            yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
            data.items())
    OrderedDumper.add_representer(OrderedDict, _dict_representer)
    return yaml.dump(data, stream, OrderedDumper, default_flow_style=False, **kwds)


def reorder_ordereddict(od, new_key_order):
    """ This creates a new OrderedDict, it can't replace a pre-existing one"""
    new_od = OrderedDict([(k, None) for k in new_key_order if k in od])
    new_od.update(od)
    return new_od


order = {}
order['top'] = ['name', 'zProperties', 'device_classes', 'event_classes']  # This is not used (yet).
order['device_classes'] = ['remove', 'description', 'protocol', 'zProperties', 'templates']
order['templates'] = ['description', 'targetPythonClass', 'datasources', 'thresholds', 'graphs']
order['datasources'] = ['type', 'oid', 'datapoints']
order['thresholds'] = ['type', 'dsnames', 'minval', 'maxval', 'enabled', 'eventClass', 'eventClassKey', 'severity']
masterkeys = order.keys()


def reorder_recurse(structure):
    """
    This Recursive method  should overcome the limitations of the manual approach below
    by allowing a general ordering dictated by the order[] dict.
    This method is not ready to be used.
    """

    new_structure = OrderedDict()
    # Iterate through the structures, looking for plural items
    for s_key, s_val in structure.items():
        if s_key in masterkeys:
            # Found a s_key to iterate on, now iterate through children
            # First create a substruct to hold reordered data
            new_substructure = OrderedDict()
            sub_structs = structure.get(s_key)
            for sub_key, sub_val in sub_structs.items():
                # Get reordered item and add it to sub_structure
                reordered_item = reorder_ordereddict(sub_val, order[s_key])
                # Last step is to recurse into sub_stucture to re-order any sub-sub-structs
                new_substructure[sub_key] = reorder_recurse(reordered_item)

            # You have to now add the substructure to the new_structure
            new_structure[s_key] = new_substructure
        else:
            # Nothing to reorder, just add it to new_structure.
            new_structure[s_key] = s_val

    return new_structure


def reorder(structure):
    """
    Reorder the YAML as required and return an OrderedDict.
    This manual ordering is limited because it is not easily extensible.
    """

    new_ordered = OrderedDict()
    for topkey, topval in structure.items():

        if topkey == 'device_classes':
            dcs = OrderedDict()
            device_classes = structure.get('device_classes')
            for dc_name, dc in device_classes.items():
                # Create New DeviceClass dict
                reordered_dc = reorder_ordereddict(dc, order['device_classes'])

                _dc = OrderedDict()
                for dc_key, dc_val in reordered_dc.items():
                    if dc_key == "templates":
                        # Create new templates dict
                        _templates = OrderedDict()
                        for t_name, tpl in dc_val.items():
                            template = reorder_ordereddict(tpl, order['templates'])
                            _templates[t_name] = template
                        _dc['templates'] = _templates

                    else:
                        _dc[dc_key] = dc_val

                dcs[dc_name] = _dc
            new_ordered[topkey] = dcs

        else:
            # Nothing to be re-ordered, populate it with default
            dcs = OrderedDict()
            new_ordered[topkey] = topval

    return new_ordered


color_rx = re.compile(
    r'(?P<pre>^\s+color:\s)'
    r'(?P<color>[0-9,a-f]{6})',    # Hexidecimal number
    re.I
)

if __name__ == '__main__':

    if len(sys.argv) < 2:
        scriptname = os.path.split(__file__)[-1]
        print "Usage: ", scriptname, 'filename.yaml'
        sys.exit(1)

    _filename = sys.argv[1]
    with open(_filename, 'r') as content_file:
        data = content_file.read()
    ordered_data = ordered_load(data, yaml.SafeLoader)

    # Use the recursive orderer.
    newOrder = reorder_recurse(ordered_data)
    reordered_yaml = ordered_dump(newOrder, Dumper=MyDumper)

    new_yaml = ''
    # Ensure colors are all quoted, else HEX may become integer: 000000 -> 0
    for line in reordered_yaml.split('\n'):
        color_match = re.match(color_rx, line)
        if color_match:
            line = re.sub(color_rx, r"\g<pre>'\g<color>'", line)
        new_yaml += line + '\n'

    print new_yaml

# -----------------------------------------------------------------------------------------
#  Below this line is for testing the manual version only.
#  Comment out the sys.exit()
# -----------------------------------------------------------------------------------------
    sys.exit()
    reordered_data = reorder(ordered_data)
    new_yaml = ordered_dump(reordered_data, Dumper=MyDumper)

    print new_yaml
