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
from .loaders import OrderedLoader, ZenPackSpecLoader
from ..base.ZenPack import ZenPack
import inspect


# list of yaml sections with DEFAULTS capability
YAML_HAS_DEFAULTS = ['classes', 'properties', 'thresholds', 'datasources',
                     'datapoints', 'graphs', 'relationships', 'graphpoints', 'zProperties']


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
    ZenPackSpecLoader.QUIET = not verbose
    ZenPackSpecLoader.LEVEL = level

    # determine caller directory and attempt to load from it
    if not yaml_doc:
        try:
            calling_dir = get_calling_dir()
            if calling_dir is None:
                raise RuntimeError('Unable to determine location of yaml files')

            return load_yaml(calling_dir, verbose, level)

        except Exception as e:
            DEFAULTLOG.error("YAML load error: %s" % e)
            raise e
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
                if not f.endswith('.yaml'):
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
        DEFAULTLOG.debug("Loaded {} in {:0.2f}s".format(CFG.name, end))
    else:
        DEFAULTLOG.error("Unable to load {}".format(yaml_doc))
    return CFG


def load_yaml_single(yaml_doc, loader=ZenPackSpecLoader):
    '''return YAML loaded from string or file with given loader.'''
    # if it's a string
    if os.path.isfile(yaml_doc):
        return yaml.load(file(yaml_doc, 'r'), Loader=loader)
    else:
        return yaml.load(yaml_doc, Loader=loader)


def get_merged_docs(docs=None):
    '''return recursively merged dictionnary'''
    if docs is None:
        docs = []
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
        cfg = load_yaml_single(doc, loader=OrderedLoader)
        # check for conflicting zenpack ids
        if zp_id:
            name = cfg.get('name')
            if name and name != zp_id:
                DEFAULTLOG.error('Skipping {} since conflicting ZenPack names '\
                    'found: {} vs {}'.format(doc, zp_id, name))
                continue
        merge_dict(new, cfg)
    return new


def optimize_yaml(orig_yaml):
    """optimize layout of YAML file"""
    # apply log verbosity settings
    ZenPackSpecLoader.QUIET = False
    ZenPackSpecLoader.LEVEL = 0
    # Load as data values
    orig_data = load_yaml_single(orig_yaml, loader=OrderedLoader)
    # create optimized YAML based on original data
    optimized_yaml = get_optimized_yaml(orig_data)
    # Load optimized data values
    optimized_data = load_yaml_single(optimized_yaml, loader=OrderedLoader)
    if not compare_zenpackspecs(orig_yaml, optimized_yaml):
        DEFAULTLOG.warn('OPTIMIZATION FAILED VERIFICATION!  Please review optimized YAML prior to use ')
        diff = compare_specparam_yaml_files(orig_yaml, optimized_yaml)
        if diff:
            print diff
    return optimized_yaml

def get_specparam_yaml_pair(orig_yaml, new_yaml):
    """return a pair of YAML files after loading"""
    orig_cfg = load_yaml_single(orig_yaml)
    orig_cfg.create()
    new_cfg = load_yaml_single(new_yaml)
    new_cfg.create()
    orig_dump = yaml.dump(orig_cfg.specparams, Dumper=Dumper)
    new_dump = yaml.dump(new_cfg.specparams, Dumper=Dumper)
    return orig_dump, new_dump

def compare_specparam_yaml_files(orig_yaml, new_yaml):
    """return diff between ZenPackSpecParams-derived YAML files"""
    orig_dump, new_dump = get_specparam_yaml_pair(orig_yaml, new_yaml)
    return ZenPack.get_yaml_diff(orig_dump, new_dump)

def compare_specparam_data(orig_yaml, new_yaml):
    """return diff between ZenPackSpecParams-derived YAML files"""
    orig_dump, new_dump = get_specparam_yaml_pair(orig_yaml, new_yaml)
    orig_data = load_yaml_single(orig_dump, loader=OrderedLoader)
    new_data = load_yaml_single(new_dump, loader=OrderedLoader)
    return dict_modified(orig_data, new_data)

def compare_zenpackspecs(orig_yaml, new_yaml):
    """report whether different YAML documents are identical"""
    # apply log verbosity settings
    ZenPackSpecLoader.QUIET = False
    ZenPackSpecLoader.LEVEL = 0
    # data should be unchanged
    if compare_specparam_data(orig_yaml, new_yaml):
        return False
    # dump back out to YAML for comparison
    if compare_specparam_yaml_files(orig_yaml, new_yaml):
        return False
    # our tests have passed
    return True

def dict_modified(d1, d2):
    """return False if the dictionary has been modified"""
    d1_keys = set(d1.keys())
    d2_keys = set(d2.keys())
    intersect_keys = d1_keys.intersection(d2_keys)
    added = d1_keys - d2_keys
    removed = d2_keys - d1_keys
    modified = {o : (d1[o], d2[o]) for o in intersect_keys if d1[o] != d2[o]}
    same = set(o for o in intersect_keys if d1[o] == d2[o])
    if added or removed or modified:
        return True
    return False


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
    # optimized output
    return yaml.dump(data, default_flow_style=False, Dumper=Dumper).replace('!!map', '')


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


def writeDataToFile(keywords=None):
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
    if keywords is None:
        keywords = []
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
