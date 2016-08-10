import os
import logging
from collections import OrderedDict
import yaml
import time
from ..functions import LOG
from .Dumper import Dumper
from .Loader import Loader

def load_yaml(yaml_filename=None):
    """Load YAML from yaml_filename.

    Loads from zenpack.yaml in the current directory if
    yaml_filename isn't specified.

    """
    start = time.time()
    CFG = None
    if not yaml_filename:
        LOG.error("No YAML file specified")

    try:
        LOG.info("Loading YAML from {}".format(yaml_filename))
        CFG = yaml.load(file(yaml_filename, 'r'), Loader=Loader)
    except Exception as e:
        if not [x for x in LOG.handlers if not isinstance(x, logging.NullHandler)]:
            # Logging has not ben initialized yet- LOG.error may not be
            # seen.
            logging.basicConfig()
        LOG.error(e)

    if CFG:
        CFG.create()
    else:
        LOG.error("Unable to load {}".format(yaml_filename))

    end = time.time() - start
    LOG.info("Loaded {} in {:0.2f}s".format(yaml_filename, end))
    return CFG


def load_yaml_multi(files=[]):
    """
        load multiple YAML files
    """
    # load the first file (should have the name defined)
    cfg_data = {}
    zp_id = None
    for f in files:
        # load as a raw Python dictionary
        with open(f, 'r') as stream:
            f_cfg = yaml.load(stream)
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
    # now load as usual
    CFG = yaml.load(optimized_yaml, Loader=Loader)
    CFG.create()
    return CFG


def load_yaml_dir(dir):
    """ load all yaml files in a directory"""
    files = []
    for f in os.listdir(fdir):
        if '.yaml' not in f:
            continue
        files.append('{}/{}'.format(dir,f))
    return load_yaml_multi(files)


def optimize_yaml(filename):
    """optimize layout of YAML file"""
    # original load
    with open(filename, 'r') as stream:
        CFG = yaml.load(stream, Loader=Loader)
    CFG.create()
    # original yaml dump
    orig_yaml = yaml.dump(CFG.specparams, Dumper=Dumper)
    # load original yaml back as a Python dictionary
    data = yaml.load(orig_yaml)
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
    orig = yaml.load(orig_yaml, Loader=Loader)
    new = yaml.load(new_yaml, Loader=Loader)
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
    orig_raw_yaml = yaml.load(orig_dump)
    new_raw_yaml = yaml.load(new_dump)
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
        if k in ['classes', 'properties', 'thresholds', 'datasources', 'datapoints', 'graphs', 'relationships','graphpoints']:
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
        params = input.get(k)
        for name, params in input.items():
            if not isinstance(params, dict):
                continue
            value = params.get(k)
            if v != value:
                if k in defaults.keys():
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
    fields = ['zProperties', 'class_relationships', 'classes', 'device_classes', 'DEFAULTS',
              'base','label','order', 'properties', 'monitoring_templates', 
              'dynamicview_views', 'dynamicview_relations',
              'impacts', 'impacted_by', 
              'relationships']
    if 'name' in data.keys():
        ordered['name'] = data.get('name')
    for k in data.keys():
        if k.startswith('z'):
            ordered[k] = data.get(k)
    # this is the desired order
    for x in fields:
        if x in data.keys():
            data_ = data.get(x)
            ordered[x] = sort_yaml_data(data_)
            # do further sorting
            if x == 'device_classes':
                # preferred ordering for device classes
                for k, v in data_.items():
                    ordered[x][k] = sort_yaml_data(v)
    # catch anything we missed
    for k in [x for x in data.keys() if x not in fields]:
        ordered[k] = sort_yaml_data(data.get(k))
    return ordered

