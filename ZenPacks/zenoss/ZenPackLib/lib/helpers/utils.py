##############################################################################
#
# Copyright (C) Zenoss, Inc. 2016, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################
import os
import logging
from collections import OrderedDict
import yaml
import time
from .ZenPackLibLog import LOG
from .Dumper import Dumper
from .Loader import Loader
import inspect


# list of yaml sections with DEFAULTS capability
YAML_HAS_DEFAULTS = ['classes', 'properties', 'thresholds', 'datasources',
                     'datapoints', 'graphs', 'relationships','graphpoints']

# preferred section ordering for YAML sections
YAML_PREFERRED_ORDER = ['zProperties', 'class_relationships', 'classes',
                        'device_classes', 'DEFAULTS', 'base',
                        'label', 'order', 'properties',
                        'monitoring_templates', 'dynamicview_views',
                        'dynamicview_relations', 'impacts', 'impacted_by',
                        'relationships']


def get_calling_dir():
    '''determine source directory of ZenPack's load_yaml call'''
    for i in inspect.stack():
        frame, filename, lineno, method_name, lines, idx = i
        if '__init__.py' not in filename:
            continue
        for line in lines:
            if 'load_yaml' in line:
                return os.path.dirname(filename)
    return None


def load_yaml(yaml_doc=None, verbose=False, level=0):
    ''''''
    Loader.QUIET= not verbose
    Loader.LEVEL = level

    # determine caller directory and attempt to load from it
    if not yaml_doc:
        try:
            return load_yaml(get_calling_dir(), verbose, level)
        except Exception as e:
            LOG.error("YAML load error %s" % e)
    # loading from multiple files
    if isinstance(yaml_doc, list):
        # build python dict of merged YAML data
        cfg_data = {}
        # this is to make sure ZP names don't conflict
        zp_id = None
        for f in yaml_doc:
            # load as a raw Python dictionary
            f_cfg = load_yaml_single(f, useLoader=False)
            name = f_cfg.get('name')
            if not zp_id:
                zp_id = name
            else:
                # if we already have a ZP id, but this yaml
                # has a different one, then there's a problem.
                if name and name != zp_id:
                    LOG.error('Skipping {} because multiple ZenPack names found: {} vs {}'.format(f, zp_id, name))
                    continue
            # update the python dict
            cfg_data.update(f_cfg)
        # once loaded, optimize
        optimized_yaml = get_optimized_yaml(cfg_data)
        # resubmit merged YAML
        return load_yaml(optimized_yaml, verbose, level)

    else:
        # load all YAML files in a directory
        if os.path.isdir(yaml_doc):
            files = []
            for f in os.listdir(yaml_doc):
                if '.yaml' not in f:
                    continue
                files.append('{}/{}'.format(yaml_doc, f))
            # resubmit multiple files
            return load_yaml(files, verbose, level)

    # load YAML and create ZenPackSpec
    start = time.time()
    CFG = None

    try:
        CFG = load_yaml_single(yaml_doc)
    except Exception as e:
        LOG.error(e)

    if CFG:
        CFG.create()
    else:
        LOG.error("Unable to load {}".format(yaml_doc))

    end = time.time() - start
    LOG.info("Loaded {} in {:0.2f}s".format(CFG.name, end))

    return CFG


def load_yaml_single(yaml_doc, useLoader=True):
    ''''''
    # if it's a string
    if os.path.isfile(yaml_doc):
        if useLoader:
            return yaml.load(file(yaml_doc, 'r'), Loader=Loader)
        return yaml.load(file(yaml_doc, 'r'))
    else:
        if useLoader:
            return yaml.load(yaml_doc, Loader=Loader)
        return yaml.load(yaml_doc)


def optimize_yaml(yaml_doc):
    """optimize layout of YAML file"""
    # apply log verbosity settings
    Loader.QUIET= False
    Loader.LEVEL = 0
    # original load
    CFG = load_yaml(yaml_doc)
    CFG.create()
    # original yaml dump
    orig_yaml = yaml.dump(CFG.specparams, Dumper=Dumper)
    # load original yaml back as a Python dictionary
    data = load_yaml_single(orig_yaml, useLoader=False)
    # optimized output
    optimized_yaml = get_optimized_yaml(data)
    # new load
    valid = compare_zenpackspecs(orig_yaml, optimized_yaml)
    if not valid:
        LOG.warn('OPTIMIZATION FAILED VERIFICATION!  Please review optimized YAML prior to use ')
    return optimized_yaml


def compare_zenpackspecs(orig_yaml, new_yaml):
    """report whether different YAML documents are identical"""
    # now load both yaml files and create ZenPackSpec configs
    # apply log verbosity settings
    Loader.QUIET= False
    Loader.LEVEL = 0
    orig = load_yaml_single(orig_yaml)
    new = load_yaml_single(new_yaml)
    orig.create()
    new.create()
    # SpecParams should be equal
    if orig != new:
        LOG.warn('ZenPackSpec mismatch between original and new')
        dict_compare(orig.__dict__, new.__dict__)
    # now dump new specs back out to yaml
    orig_dump = yaml.dump(orig.specparams, Dumper=Dumper)
    new_dump = yaml.dump(new.specparams, Dumper=Dumper)
    # load raw yaml into Python dictionaries
    orig_raw_yaml = load_yaml_single(orig_dump, useLoader=False)
    new_raw_yaml = load_yaml_single(new_dump, useLoader=False)
    # these should also be equivalent
    if orig_raw_yaml != new_raw_yaml:
        LOG.warn('YAML loaded Python dictionary mismatch between original and new')
        dict_compare(orig_raw_yaml, new_raw_yaml)
        return False
    return True

def dict_compare(d1, d2):
    d1_keys = set(d1.keys())
    d2_keys = set(d2.keys())
    intersect_keys = d1_keys.intersection(d2_keys)
    added = d1_keys - d2_keys
    removed = d2_keys - d1_keys
    modified = {o : (d1[o], d2[o]) for o in intersect_keys if d1[o] != d2[o]}
    same = set(o for o in intersect_keys if d1[o] == d2[o])
    LOG.warn('ADDED: {}'.format(added))
    LOG.warn('REMOVED: {}'.format(removed))
    LOG.warn('MODIFIED: {}'.format(modified))


def get_optimized_yaml(data):
    """
        return optimized YAML representing ZenPackSpec
    """
    # set DEFAULTS throughout
    descend_defaults(data)
    # sort
    ordered = sort_yaml_data(data)
    # optimized output
    return yaml.dump(ordered,  default_flow_style=False, Dumper=Dumper).replace('!!map','')


def descend_defaults(input):
    """
        descend YAML dictionary and optimize DEFAULTS
    """
    for k, v in input.items():
        if not isinstance(v, dict):
            continue
        if k == 'DEFAULTS': 
            continue
        if k in YAML_HAS_DEFAULTS:
            if len(v.keys()) > 1:
                set_defaults(v)
        descend_defaults(v)


def set_defaults(input):
    """
        if dict has multiple entries, look for identical key/value 
        pairs and move them to DEFAULTS
    """
    defaults = {}
    # get list of potential defaults
    for name, params in input.items():
        if not isinstance(params, dict): 
            continue
        for k,v in params.items():
            if isinstance(v, dict): 
                continue
            if k not in defaults.keys():
               defaults[k] = v
    # disqualify defaults if not universal
    for k, v in defaults.items():
        for name, params in input.items():
            if not isinstance(params, dict):
                continue
            value = params.get(k)
            if v != value and k in defaults.keys():
                defaults.pop(k)
    if len(defaults.keys()) == 0:
        return
    # remove universal parameters from individual spec
    for name, params in input.items():
        if not isinstance(params, dict): 
            continue
        for k in params.keys():
            if k in defaults.keys():
                params.pop(k)
    # add defaults to original data
    if 'DEFAULTS' in input.keys():
        input['DEFAULTS'].update(defaults)
    else:
        input['DEFAULTS'] = defaults


def sort_yaml_data(data):
    """
        Sort YAML data before outputting
    """
    if not isinstance(data, dict):
        return data
    ordered = OrderedDict()
    if 'name' in data.keys():
        ordered['name'] = data.get('name')
    for k in data.keys():
        if k.startswith('z'):
            ordered[k] = data.get(k)
    # this is the desired order
    for x in YAML_PREFERRED_ORDER:
        if x in data.keys():
            data_ = data.get(x)
            ordered[x] = sort_yaml_data(data_)
            # do further sorting
            if x == 'device_classes':
                # preferred ordering for device classes
                for k, v in data_.items():
                    ordered[x][k] = sort_yaml_data(v)
    # catch anything we missed
    for k in [x for x in data.keys() if x not in YAML_PREFERRED_ORDER]:
        ordered[k] = sort_yaml_data(data.get(k))
    return ordered

