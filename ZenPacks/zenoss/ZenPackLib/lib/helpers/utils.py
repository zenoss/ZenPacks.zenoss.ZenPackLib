##############################################################################
#
# Copyright (C) Zenoss, Inc. 2016, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################
import os
from collections import OrderedDict, Mapping
import yaml
import time
from .ZenPackLibLog import DEFAULTLOG
from .Dumper import Dumper
from .Loader import Loader
import inspect

# adding these so that yaml.Loader can handle !ZenPackSpec tag
yaml.Loader.add_constructor(u'!ZenPackSpec', yaml.Loader.construct_yaml_map)
yaml.Loader.add_path_resolver(u'!ZenPackSpec', [])


# list of yaml sections with DEFAULTS capability
YAML_HAS_DEFAULTS = ['classes', 'properties', 'thresholds', 'datasources',
                     'datapoints', 'graphs', 'relationships', 'graphpoints', 'zProperties']

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
    Loader.QUIET = not verbose
    Loader.LEVEL = level

    # determine caller directory and attempt to load from it
    if not yaml_doc:
        try:
            return load_yaml(get_calling_dir(), verbose, level)
        except Exception as e:
            DEFAULTLOG.error("YAML load error %s" % e)
    # loading from multiple files
    if isinstance(yaml_doc, list):
        if len(yaml_doc) == 1:
            return load_yaml(yaml_doc[0], verbose, level)
        # build python dict of merged YAML data
        cfg_data = get_merged_docs(yaml_doc)
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
        if os.path.isfile(yaml_doc):
            DEFAULTLOG.debug("Loading YAML from {}".format(yaml_doc))
        CFG = load_yaml_single(yaml_doc)
    except Exception as e:
        DEFAULTLOG.error(e)

    if CFG:
        CFG.create()
        end = time.time() - start
        DEFAULTLOG.info("Loaded {} in {:0.2f}s".format(CFG.name, end))
    else:
        DEFAULTLOG.error("Unable to load {}".format(yaml_doc))
    return CFG


def load_yaml_single(yaml_doc, useLoader=True, loader=Loader):
    ''''''
    # if it's a string
    if os.path.isfile(yaml_doc):
        if useLoader:
            return yaml.load(file(yaml_doc, 'r'), Loader=loader)
        return yaml.load(file(yaml_doc, 'r'))
    else:
        if useLoader:
            return yaml.load(yaml_doc, Loader=loader)
        return yaml.load(yaml_doc)


def get_merged_docs(docs=[]):
    '''return recursively merged dictionnary'''
    def merge_dict(target, source):
        for k, v in source.items():
            if (k in target and isinstance(target[k], dict)
                    and isinstance(source[k], Mapping)):
                merge_dict(target[k], source[k])
            elif (k in target and isinstance(target[k], list)
                  and isinstance(source[k], list)):
                target[k].extend(source[k])
            else:
                target[k] = source[k]
    new = {}
    for doc in docs:
        zp_id = new.get('name')
        cfg = load_yaml_single(doc, useLoader=False)
        # check for conflicting zenpack ids
        if zp_id:
            name = cfg.get('name')
            if name and name != zp_id:
                DEFAULTLOG.error('Skipping {} since conflicting ZenPack names '\
                    'found: {} vs {}'.format(doc, zp_id, name))
                continue
        merge_dict(new, cfg)
    return new


def optimize_yaml(yaml_doc):
    """optimize layout of YAML file"""
    # apply log verbosity settings
    Loader.QUIET = False
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
        DEFAULTLOG.warn('OPTIMIZATION FAILED VERIFICATION!  Please review optimized YAML prior to use ')
    return optimized_yaml


def compare_zenpackspecs(orig_yaml, new_yaml):
    """report whether different YAML documents are identical"""
    # now load both yaml files and create ZenPackSpec configs
    # apply log verbosity settings
    Loader.QUIET = False
    Loader.LEVEL = 0
    orig = load_yaml_single(orig_yaml)
    new = load_yaml_single(new_yaml)
    orig.create()
    new.create()
    # SpecParams should be equal
    if orig != new:
        DEFAULTLOG.warn('ZenPackSpec mismatch between original and new')
        dict_compare(orig.__dict__, new.__dict__)
    # now dump new specs back out to yaml
    orig_dump = yaml.dump(orig.specparams, Dumper=Dumper)
    new_dump = yaml.dump(new.specparams, Dumper=Dumper)
    # load raw yaml into Python dictionaries
    orig_raw_yaml = load_yaml_single(orig_dump, useLoader=False)
    new_raw_yaml = load_yaml_single(new_dump, useLoader=False)
    # these should also be equivalent
    if orig_raw_yaml != new_raw_yaml:
        DEFAULTLOG.warn('YAML loaded Python dictionary mismatch between original and new')
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
    DEFAULTLOG.warn('ADDED: {}'.format(added))
    DEFAULTLOG.warn('REMOVED: {}'.format(removed))
    DEFAULTLOG.warn('MODIFIED: {}'.format(modified))


def get_optimized_yaml(data):
    """
        return optimized YAML representing ZenPackSpec
    """
    # set DEFAULTS throughout
    descend_defaults(data)
    # sort
    ordered = sort_yaml_data(data)
    # optimized output
    return yaml.dump(ordered, default_flow_style=False, Dumper=Dumper).replace('!!map', '')


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
        for k, v in params.items():
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


def writeDataToFile(keywords=[]):
    '''
    This is a decorator that will save arguments sent to a function.
    It will write to the /tmp directory using the class name, method name
    and write time as the file name.  It depends upon the 'ZPL_DUMP_DATA' env
    variable existing to dump the pickle.  It then passes the args to the original
    function.  Be sure to unset ZPL_DUMP_DATA or you'll see a peck of pickles.

    keywords is a list of words that, if a match is found, will cause an object to not be pickled

    usage:
    class test1(object):
        my_password = ''
        my_datasource = ''
        def __init__(self, pw, ds):
            self.my_password = pw
            self.my_datasource = ds

    t1 = test1()

    class foo(object):
        @writeDataToFile()
        def bar1(self, x, y):
            print 'x: {}, y: {}'.format(x, y)

        @writeDataToFile(keywords=['my_password', 'my_datasource'])
        def bar2(self, x, y):
            print 'testing'

    f = foo()
    f.bar1(1, 2)
    # int(1) and int(2) will be pickled
    f.bar2(t1, 'bar2')
    # t1 will not be pickled, str('bar2') will be pickled

    $ export ZPL_DUMP_DATA=1; python foo.py; unset ZPL_DUMP_DATA
    '''
    def wrap(f):
        def dumper(self, *args, **kwargs):
            import os
            if os.environ.get('ZPL_DUMP_DATA', None):
                import pickle
                import time
                import logging
                words = keywords
                if not isinstance(words, list):
                    words = list(words)
                filetime = time.strftime('%H%M%S', time.localtime())
                fname = '_'.join((self.__class__.__name__, f.func_name, filetime))
                with open(os.path.join('/tmp', fname + '.pickle'), 'w') as pkl_file:
                    arguments = []
                    for count, thing in enumerate(args):
                        # ignore Logger, file objects, and user
                        # defined keywords
                        if (isinstance(thing, logging.Logger) or
                                isinstance(thing, file) or
                                [a for a in dir(thing) for kw in words if kw == a]):
                                    continue
                        arguments.append(thing)
                    for name, thing in kwargs.items():
                        # ignore Logger, file objects, and user
                        # defined keywords
                        if (isinstance(thing, logging.Logger) or
                                isinstance(thing, file) or
                                [a for a in dir(thing) for kw in words if kw == a]):
                                    continue
                        arguments.append('{}={}'.format(name, thing))
                    try:
                        pickle.dump(arguments, pkl_file)
                    except TypeError:
                        pass
                    pkl_file.close()
            return f(self, *args, **kwargs)
        return dumper
    return wrap
