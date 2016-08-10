import os
import importlib
import collections
import imp
import sys
import operator
import re
import yaml
import time
import keyword
import logging
from collections import OrderedDict
from Products.AdvancedQuery.AdvancedQuery import _BaseQuery as BaseQuery

from .utils import yaml_installed
from .helpers.Loader import Loader
from .helpers.ZenPackLibLog import ZenPackLibLog


ZPLOG = ZenPackLibLog()
LOG = ZPLOG.defaultlog


# Default log settings
QUIET=True
LEVEL=0


def load_yaml(yaml_filename=None, verbose=False, level=0):
    """Load YAML from yaml_filename.
    Loads from zenpack.yaml in the current directory if
    yaml_filename isn't specified.
    """

    # these control logging on a per-ZenPack basis
    global QUIET, LEVEL
    QUIET = not verbose
    LEVEL = level

    start = time.time()
    CFG = None
    if yaml_installed():
        if yaml_filename is None:
            yaml_filename = os.path.join(
                os.path.dirname(__file__), 'zenpack.yaml')

        try:
            LOG.info("Loading YAML from %s" % yaml_filename)
            CFG = yaml.load(file(yaml_filename, 'r'), Loader=Loader)
        except Exception as e:
            if not [x for x in LOG.handlers if not isinstance(x, logging.NullHandler)]:
                # Logging has not ben initialized yet- LOG.error may not be
                # seen.
                logging.basicConfig()
            LOG.error(e)
    else:
        zenpack_name = None

        # Guess ZenPack name from the path.
        dirname = __file__

        while dirname != '/':
            dirname = os.path.dirname(dirname)
            basename = os.path.basename(dirname)
            if basename.startswith('ZenPacks.'):
                zenpack_name = basename
                break

        LOG.error(
            '%s requires PyYAML. Run "easy_install PyYAML".',
            zenpack_name or 'ZenPack')

        from spec.ZenPackSpec import ZenPackSpec
        # Create a simple ZenPackSpec that should be harmless.
        CFG = ZenPackSpec(name=zenpack_name or 'NoYAML')

    if CFG:
        CFG.create()
    else:
        LOG.error("Unable to load %s", yaml_filename)

    end = time.time() - start
    LOG.info("Loaded %s in %0.2f s" % (yaml_filename, end))
    return CFG


# Private Functions #########################################################


def get_zenpack_path(zenpack_name):
    """Return filesystem path for given ZenPack."""
    zenpack_module = importlib.import_module(zenpack_name)
    if hasattr(zenpack_module, '__file__'):
        return os.path.dirname(zenpack_module.__file__)
    else:
        return None


def ordered_values(iterable):
    """Return ordered list of values for iterable of OrderAndValue instances."""
    return [
        x.value for x in sorted(iterable, key=operator.attrgetter('order'))]


def pluralize(text):
    """Return pluralized version of text.

    Totally naive implementation currently. Could use a third party
    library if we knew it would be installed.
    """
    if text.endswith('s'):
        return '{}es'.format(text)

    return '{}s'.format(text)


def fix_kwargs(kwargs):
    """Return kwargs with reserved words suffixed with _."""
    new_kwargs = {}
    for k, v in kwargs.items():
        if k in ('class', 'type'):
            new_kwargs['{}_'.format(k)] = v
        else:
            new_kwargs[k] = v

    return new_kwargs


def catalog_search(scope, name, *args, **kwargs):
    """Return iterable of matching brains in named catalog."""

    catalog = getattr(scope, '{}Search'.format(name), None)
    if not catalog:
        LOG.debug("Catalog %sSearch not found at %s.  It should be created when the first included component is indexed" % (name, scope))
        return []

    if args:
        if isinstance(args[0], BaseQuery):
            return catalog.evalAdvancedQuery(args[0])
        elif isinstance(args[0], dict):
            return catalog(args[0])
        else:
            raise TypeError(
                "search() argument must be a BaseQuery or a dict, "
                "not {0!r}"
                .format(type(args[0]).__name__))

    return catalog(**kwargs)


def get_symbol_name(*args):
    """Return fully-qualified symbol name given path args.

    Example usage:

        >>> get_symbol_name('ZenPacks.example.Name')
        'ZenPacks.example.Name'

        >>> get_symbol_name('ZenPacks.example.Name', 'schema')
        'ZenPacks.example.Name.schema'

        >>> get_symbol_name('ZenPacks.example.Name', 'schema', 'APIC')
        'ZenPacks.example.Name.schema.APIC'

        >>> get_symbol_name('ZenPacks.example.Name', 'schema.Pool')
        'ZenPacks.example.Name.schema.Pool'

    No verification is done. Names for symbols that don't exist may
    be returned.

    """
    return '.'.join(x for x in args if x)


def create_module(*args):
    """Import and return module given path args.

    See get_symbol_name documentation for usage. May raise ImportError.

    """
    module_name = get_symbol_name(*args)
    try:
        return importlib.import_module(module_name)
    except ImportError:
        module = imp.new_module(module_name)
        module.__name__ = module_name
        sys.modules[module_name] = module

        module_parts = module_name.split('.')

        if len(module_parts) > 1:
            parent_module_name = get_symbol_name(*module_parts[:-1])
            parent_module = create_module(parent_module_name)
            setattr(parent_module, module_parts[-1], module)

    return importlib.import_module(module_name)


def relationships_from_yuml(yuml):
    '''This function is used by pre-YAML relation definitions'''
    """Return schema relationships definition given yuml text.

    The yuml text required is a subset of what is supported by yUML
    (http://yuml.me). See the following example:

        // Containing relationships.
        [APIC]++ -[FabricPod]
        [APIC]++ -[FvTenant]
        [FvTenant]++ -[VzBrCP]
        [FvTenant]++ -[FvAp]
        [FvAp]++ -[FvAEPg]
        [FvAEPg]++ -[FvRsProv]
        [FvAEPg]++ -[FvRsCons]
        // Non-containing relationships.
        [FvBD]1 -.- *[FvAEPg]
        [VzBrCP]1 -.- *[FvRsProv]
        [VzBrCP]1 -.- *[FvRsCons]

    The created relationships are given default names that orginarily
    should be used. However, in some cases such as when one class has
    multiple relationships to the same class, relationships must be
    explicitly named. That would be done as in the following example:

        // Explicitly-Named Relationships
        [Pool]*default_sr -.-default_for_pools 0..1[SR]
        [Pool]*suspend_image_sr -.-suspend_image_for_pools *[SR]
        [Pool]*crash_dump_sr -.-crash_dump_for_pools *[SR]

    The yuml parameter can be specified either as a newline-delimited
    string, or as a tuple or list of relationships.

    """
    classes = []
    match_comment = re.compile(r'^//').search

    match_line = re.compile(
        r'\[(?P<left_classname>[^\]]+)\]'
        r'(?P<left_cardinality>[\.\*\+\d]*)'
        r'(?P<left_relname>[a-zA-Z_]*)'
        r'\s*?'
        r'(?P<relationship_separator>[\-\.]+)'
        r'(?P<right_relname>[a-zA-Z_]*)'
        r'\s*?'
        r'(?P<right_cardinality>[\.\*\+\d]*)'
        r'\[(?P<right_classname>[^\]]+)\]'
        ).search

    if isinstance(yuml, basestring):
        yuml_lines = yuml.strip().splitlines()

    for line in yuml_lines:
        line = line.strip()

        if not line:
            continue

        if match_comment(line):
            continue

        match = match_line(line)
        if not match:
            raise ValueError("parse error in relationships_from_yuml at %s" % line)

        left_class = match.group('left_classname')
        right_class = match.group('right_classname')
        left_relname = match.group('left_relname')
        left_cardinality = match.group('left_cardinality')
        right_relname = match.group('right_relname')
        right_cardinality = match.group('right_cardinality')

        if '++' in left_cardinality:
            left_type = 'ToManyCont'
        elif '*' in right_cardinality:
            left_type = 'ToMany'
        else:
            left_type = 'ToOne'

        if '++' in right_cardinality:
            right_type = 'ToManyCont'
        elif '*' in left_cardinality:
            right_type = 'ToMany'
        else:
            right_type = 'ToOne'

        if not left_relname:
            left_relname = relname_from_classname(
                right_class, plural=left_type != 'ToOne')

        if not right_relname:
            right_relname = relname_from_classname(
                left_class, plural=right_type != 'ToOne')
        
        from spec.RelationshipSchemaSpec import RelationshipSchemaSpec
        # Order them correctly (larger one on the right)
        if RelationshipSchemaSpec.valid_orientation(left_type, right_type):
            classes.append(dict(
                left_class=left_class,
                left_relname=left_relname,
                left_type=left_type,
                right_type=right_type,
                right_class=right_class,
                right_relname=right_relname
            ))
        else:
            # flip them around
            classes.append(dict(
                left_class=right_class,
                left_relname=right_relname,
                left_type=right_type,
                right_type=left_type,
                right_class=left_class,
                right_relname=left_relname
            ))

    return classes

# Public Functions #########################################################

from Products.ZenModel.Device import Device as BaseDevice
from Products.Zuul.infos.device import DeviceInfo as BaseDeviceInfo
from Products.ZenModel.DeviceComponent import DeviceComponent as BaseDeviceComponent
from Products.Zuul.infos.component import ComponentInfo as BaseComponentInfo

def getZenossKeywords(klasses):
    kwset = set()
    for klass in klasses:
        for k in klass.__dict__.keys():
            if callable(getattr(klass, k)):
                kwset = kwset.union([k])
        for attribute in dir(klass):
            if callable(getattr(klass, attribute)):
                kwset = kwset.union([attribute])
    return kwset

ZENOSS_KEYWORDS = getZenossKeywords([BaseDevice,
                                    BaseDeviceInfo,
                                    BaseDeviceComponent,
                                    BaseComponentInfo])

JS_WORDS = set(['uuid', 'uid', 'meta_type', 'monitor', 'severity', 'monitored', 'locking'])


def find_keyword_cls(keyword):
    names = []
    for k in [BaseDevice, BaseDeviceComponent, BaseDeviceInfo, BaseComponentInfo]:
        if keyword in dir(k):
            names.append(k.__name__)
    return names


def relschemaspec_to_str(spec):
    # Omit relation names that are their defaults.
    left_optrelname = "" if spec.left_relname == spec.default_left_relname else "(%s)" % spec.left_relname
    right_optrelname = "" if spec.right_relname == spec.default_right_relname else "(%s)" % spec.right_relname

    return "%s%s %s:%s %s%s" % (
        spec.left_class,
        left_optrelname,
        spec.left_cardinality,
        spec.right_cardinality,
        right_optrelname,
        spec.right_class
    )


def str_to_relschemaspec(schemastr):
    schema_pattern = re.compile(
        r'^\s*(?P<left>\S+)'
        r'\s+(?P<cardinality>1:1|1:M|1:MC|M:M)'
        r'\s+(?P<right>\S+)\s*$',
    )

    class_rel_pattern = re.compile(
        r'(\((?P<pre_relname>[^\)\s]+)\))?'
        r'(?P<class>[^\(\s]+)'
        r'(\((?P<post_relname>[^\)\s]+)\))?'
    )

    m = schema_pattern.search(schemastr)
    if not m:
        raise ValueError("RelationshipSchemaSpec '{}' is not valid".format(schemastr))

    ml = class_rel_pattern.search(m.group('left'))
    if not ml:
        raise ValueError("RelationshipSchemaSpec '{}' left side is not valid".format(m.group('left')))

    mr = class_rel_pattern.search(m.group('right'))
    if not mr:
        raise ValueError("RelationshipSchemaSpec '{}' right side is not valid".format(m.group('right')))

    reltypes = {
        '1:1': ('ToOne', 'ToOne'),
        '1:M': ('ToMany', 'ToOne'),
        '1:MC': ('ToManyCont', 'ToOne'),
        'M:M': ('ToMany', 'ToMany')
    }

    left_class = ml.group('class')
    right_class = mr.group('class')
    left_type = reltypes.get(m.group('cardinality'))[0]
    right_type = reltypes.get(m.group('cardinality'))[1]

    left_relname = ml.group('pre_relname') or ml.group('post_relname')
    if left_relname is None:
        left_relname = relname_from_classname(right_class, plural=left_type != 'ToOne')

    right_relname = mr.group('pre_relname') or mr.group('post_relname')
    if right_relname is None:
        right_relname = relname_from_classname(left_class, plural=right_type != 'ToOne')

    return dict(
        left_class=left_class,
        left_relname=left_relname,
        left_type=left_type,
        right_type=right_type,
        right_class=right_class,
        right_relname=right_relname
    )


def str_to_class(classstr):
    if classstr == 'object':
        return object

    if "." not in classstr:
        # TODO: Support non qualfied class names, searching zenpack, zenpacklib,
        # and ZenModel namespaces

        # An unqualified class name is assumed to be referring to one in
        # the classes defined in this ZenPackSpec.   We can't validate this,
        # or return a class object for it, if this is the case.  So we
        # return no class object, and the caller will assume that it
        # it refers to a class being defined.
        return None

    modname, classname = classstr.rsplit(".", 1)
    # ensure that 'zenpacklib' refers to *this* zenpacklib, if more than
    # one is loaded in the system.
    if modname == 'zenpacklib':
        modpath = '.'.join(__name__.split('.')[:-1])
        modname = '%s.base.%s' % (modpath, classname)
    try:
        class_ = getattr(importlib.import_module(modname), classname)
    except Exception, e:
        raise ValueError("Class '{}' is not valid: {}".format(classstr, e))

    return class_


def severity_to_str(value):
    '''
    Return string representation for severity given a numeric value.
    '''
    severity = {
        5: 'crit',
        4: 'err',
        3: 'warn',
        2: 'info',
        1: 'debug',
        0: 'clear'
        }.get(value, None)

    if severity is None:
        raise ValueError("'{}' is not a valid value for severity.".format(value))

    return severity


def str_to_severity(value):
    '''
    Return numeric severity given a string representation of severity.
    '''
    try:
        severity = int(value)
    except (TypeError, ValueError):
        severity = {
            'crit': 5, 'critical': 5,
            'err': 4, 'error': 4,
            'warn': 3, 'warning': 3,
            'info': 2, 'information': 2, 'informational': 2,
            'debug': 1, 'debugging': 1,
            'clear': 0,
            }.get(value.lower())

    if severity is None:
        raise ValueError("'{}' is not a valid value for severity.".format(value))

    return severity


def format_message(e):
    message = []

    mark = e.context_mark or e.problem_mark
    if mark:
        name = mark.name.split('/')[-1]
        position = "({} line {}:{})".format(name, mark.line + 1, mark.column + 1)
    else:
        position = "[unknown]"
    if e.context is not None:
        message.append(e.context)

    if e.problem is not None:
        message.append(e.problem)

    if e.note is not None:
        message.append("(note: " + e.note + ")")

    return "{} {}".format(position, ' '.join(message))


def yaml_warning(loader, e):
    """
        Given a MarkedYAMLError exception, log
        the error
    """
    LOG.warn(format_message(e))


def yaml_error(loader, e, exc_info=None):
    """
        Given a MarkedYAMLError exception, either log or raise
        the error, depending on the 'fatal' argument.
    """
    fatal = not getattr(loader, 'warnings', False)
    setattr(loader, 'yaml_errored', True)

    if exc_info:
        # When we're given the original exception (which was wrapped in
        # a MarkedYAMLError), we can provide more context for debugging.

        from traceback import format_exc
        e.note = "\nOriginal exception:\n" + format_exc(exc_info)

    if fatal:
        raise e

    LOG.error(format_message(e))


def verify_key(loader, cls, params, key, start_mark):
    # always ok to use a param name (description, name, etc.)
    if key in params.keys():
        return True

    # never use a python reserved word
    if key in keyword.kwlist:
        yaml_error(loader, yaml.constructor.ConstructorError(
            None, None,
            "Found reserved python keyword '{}' while processing {}".format(key, cls.__name__),
            start_mark))
    elif key in ZENOSS_KEYWORDS.union(JS_WORDS):
        # should be ok to use a zenoss word to define these
        # some items, like sysUpTime are pretty common datapoints
        if cls.__name__ not in ['RRDDatasourceSpec',
                                'RRDDatapointSpec',
                                'RRDTemplateSpec',
                                'GraphDefinitionSpec',
                                'GraphPointSpec']:
            klasses = ', '.join(find_keyword_cls(key))
            yaml_warning(loader, yaml.constructor.ConstructorError(
                None, None,
                "Found reserved Zenoss keyword '{}' from {}".format(key, klasses),
                start_mark))

    return False


def construct_specsparameters(loader, node, spectype):
    from spec.Spec import Spec

    spec_class = {x.__name__: x for x in Spec.__subclasses__()}.get(spectype, None)

    if not spec_class:
        yaml_error(loader, yaml.constructor.ConstructorError(
            None, None,
            "Unrecognized Spec class %s" % spectype,
            node.start_mark))
        return

    if not isinstance(node, yaml.MappingNode):
        yaml_error(loader, yaml.constructor.ConstructorError(
            None, None,
            "expected a mapping node, but found %s" % node.id,
            node.start_mark))
        return

    param_defs = spec_class.init_params()
    specs = OrderedDict()
    for spec_key_node, spec_value_node in node.value:
        try:
            spec_key = str(loader.construct_scalar(spec_key_node))
            verify_key(loader, spec_class, param_defs, spec_key, spec_key_node.start_mark)

        except yaml.MarkedYAMLError, e:
            yaml_error(loader, e)

        specs[spec_key] = construct_spec(spec_class, loader, spec_value_node)

    return specs


def represent_relschemaspec(dumper, data):
    """
    Generic representer for serializing relation specs to YAML.
    """
    return dumper.represent_str(relschemaspec_to_str(data))


def represent_spec(dumper, obj, yaml_tag=u'tag:yaml.org,2002:map', defaults=None):
    """
    Generic representer for serializing specs to YAML.  Rather than using
    the default PyYAML representer for python objects, we very carefully
    build up the YAML according to the parameter definitions in the __init__
    of each spec class.  This same format is used by construct_spec (the YAML
    constructor) to ensure that the spec objects are built consistently,
    whether it is done via YAML or the API.
    """
    from spec.RRDDatapointSpec import RRDDatapointSpec
    if isinstance(obj, RRDDatapointSpec) and obj.shorthand:
        # Special case- we allow for a shorthand in specifying datapoints
        # as specs as strings rather than explicitly as a map.
        return dumper.represent_str(str(obj.shorthand))

    mapping = OrderedDict()
    cls = obj.__class__
    param_defs = cls.init_params()
    for param in param_defs:
        type_ = param_defs[param]['type']

        try:
            value = getattr(obj, param)
        except AttributeError:
            raise yaml.representer.RepresenterError(
                "Unable to serialize %s object: %s, a supported parameter, is not accessible as a property." %
                (cls.__name__, param))
            continue

        # Figure out what the default value is.  First, consider the default
        # value for this parameter (globally):
        default_value = param_defs[param].get('default', None)

        # Now, we need to handle 'DEFAULTS'.  If we're in a situation
        # where that is supported, and we're outputting a spec that
        # would be affected by it (not DEFAULTS itself, in other words),
        # then we look at the default value for this parameter, in case
        # it has changed the global default for this parameter.
        if hasattr(obj, 'name') and obj.name != 'DEFAULTS' and defaults is not None:
            default_value = getattr(defaults, param, default_value)

        if value == default_value:
            # If the value is a default value, we can omit it from the export.
            continue

        # If the value is null and the type is a list or dictionary, we can
        # assume it was some optional nested data and omit it.
        if value is None and (
           type_.startswith('dict') or
           type_.startswith('list') or
           type_.startswith('SpecsParameter')):
            continue

        if type_ == 'ZPropertyDefaultValue':
            # For zproperties, the actual data type of a default value
            # depends on the defined type of the zProperty.
            try:
                type_ = {
                    'boolean': "bool",
                    'int': "int",
                    'float': "float",
                    'string': "str",
                    'password': "str",
                    'lines': "list(str)"
                }.get(obj.type_, 'str')
            except KeyError:
                type_ = "str"

        yaml_param = dumper.represent_str(param_defs[param]['yaml_param'])
        try:
            if type_ == "bool":
                mapping[yaml_param] = dumper.represent_bool(value)
            elif type_.startswith("dict"):
                mapping[yaml_param] = dumper.represent_dict(value)
            elif type_ == "float":
                mapping[yaml_param] = dumper.represent_float(value)
            elif type_ == "int":
                mapping[yaml_param] = dumper.represent_int(value)
            elif type_ == "list(class)":
                # The "class" in this context is either a class reference or
                # a class name (string) that refers to a class defined in
                # this ZenPackSpec.
                classes = [isinstance(x, type) and class_to_str(x) or x for x in value]
                mapping[yaml_param] = dumper.represent_list(classes)
            elif type_.startswith("list(ExtraPath)"):
                # Represent this as a list of lists of quoted strings (each on one line).
                paths = []
                for path in list(value):
                    # Force the regular expressions to be quoted, so we don't have any issues with that.
                    pathnodes = [dumper.represent_scalar(u'tag:yaml.org,2002:str', x, style="'") for x in path]
                    paths.append(yaml.SequenceNode(u'tag:yaml.org,2002:seq', pathnodes, flow_style=True))
                mapping[yaml_param] = yaml.SequenceNode(u'tag:yaml.org,2002:seq', paths, flow_style=False)
            elif type_.startswith("list"):
                mapping[yaml_param] = dumper.represent_list(value)
            elif type_ == "str":
                mapping[yaml_param] = dumper.represent_str(value)
            elif type_ == 'RelationshipSchemaSpec':
                mapping[yaml_param] = dumper.represent_str(relschemaspec_to_str(value))
            elif type_ == 'Severity':
                mapping[yaml_param] = dumper.represent_str(severity_to_str(value))
            elif type_ == 'ExtraParams':
                # ExtraParams is a special case, where any 'extra'
                # parameters not otherwise defined in the init_params
                # definition are tacked into a dictionary with no specific
                # schema validation.  This is meant to be used in situations
                # where it is impossible to know what parameters will be
                # needed ahead of time, such as with a datasource
                # that has been subclassed and had new properties added.
                #
                # Note: the extra parameters are required to have scalar
                # values only.
                for extra_param in value:
                    # add any values from an extraparams dict onto the spec's parameter list directly.
                    yaml_extra_param = dumper.represent_str(extra_param)

                    mapping[yaml_extra_param] = dumper.represent_data(value[extra_param])
            else:
                m = re.match('^SpecsParameter\((.*)\)$', type_)
                if m:
                    spectype = m.group(1)
                    specmapping = OrderedDict()
                    keys = sorted(value)
                    defaults = None
                    if 'DEFAULTS' in keys:
                        keys.remove('DEFAULTS')
                        keys.insert(0, 'DEFAULTS')
                        defaults = value['DEFAULTS']
                    for key in keys:
                        spec = value[key]
                        if type(spec).__name__ != spectype:
                            raise yaml.representer.RepresenterError(
                                "Unable to serialize %s object (%s):  Expected an object of type %s" %
                                (type(spec).__name__, key, spectype))
                        else:
                            specmapping[dumper.represent_str(key)] = represent_spec(dumper, spec, defaults=defaults)

                    specmapping_value = []
                    node = yaml.MappingNode(yaml_tag, specmapping_value)
                    specmapping_value.extend(specmapping.items())
                    mapping[yaml_param] = node
                else:
                    raise yaml.representer.RepresenterError(
                        "Unable to serialize %s object: %s, a supported parameter, is of an unrecognized type (%s)." %
                        (cls.__name__, param, type_))
        except yaml.representer.RepresenterError:
            raise
        except Exception, e:
            raise yaml.representer.RepresenterError(
                "Unable to serialize %s object (param %s, type %s, value %s): %s" %
                (cls.__name__, param, type_, value, e))

        if param in param_defs and param_defs[param]['yaml_block_style']:
            mapping[yaml_param].flow_style = False

    mapping_value = []
    node = yaml.MappingNode(yaml_tag, mapping_value)
    mapping_value.extend(mapping.items())

    # Return a node describing the mapping (dictionary) of the params
    # used to build this spec.
    return node


def construct_spec(cls, loader, node):
    """
    Generic constructor for deserializing specs from YAML.   Should be
    the opposite of represent_spec, and works in the same manner (with its
    parsing and validation directed by the init_params of each spec class)
    """
    from spec.RRDDatapointSpec import RRDDatapointSpec
    if issubclass(cls, RRDDatapointSpec) and isinstance(node, yaml.ScalarNode):
        # Special case- we allow for a shorthand in specifying datapoint specs.
        return dict(shorthand=loader.construct_scalar(node))

    param_defs = cls.init_params()
    params = {}
    if not isinstance(node, yaml.MappingNode):
        yaml_error(loader, yaml.constructor.ConstructorError(
            None, None,
            "expected a mapping node, but found %s" % node.id,
            node.start_mark))

    params['_source_location'] = "%s: %s-%s" % (
        os.path.basename(node.start_mark.name),
        node.start_mark.line+1,
        node.end_mark.line+1)

    # TODO: When deserializing, we should check if required properties are present.

    param_name_map = {}
    for param in param_defs:
        param_name_map[param_defs[param]['yaml_param']] = param

    extra_params = None
    for key in param_defs:
        if param_defs[key]['type'] == 'ExtraParams':
            if extra_params:
                yaml_error(loader, yaml.constructor.ConstructorError(
                    None, None,
                    "Only one ExtraParams parameter may be specified.",
                    node.start_mark))
            extra_params = key
            params[extra_params] = {}

    for key_node, value_node in node.value:
        yaml_key = str(loader.construct_scalar(key_node))
        verify_key(loader, cls, param_defs, yaml_key, key_node.start_mark)

        if yaml_key not in param_name_map:
            if extra_params:
                # If an 'extra_params' parameter is defined for this spec,
                # we take all unrecognized paramters and stuff them into
                # a single parameter, which is a dictonary of "extra" parameters.
                #
                # Note that the values of these extra parameters need to be
                # scalars, not nested maps or something like that.
                params[extra_params][yaml_key] = loader.construct_scalar(value_node)
                continue
            else:
                yaml_error(loader, yaml.constructor.ConstructorError(
                    None, None,
                    "Unrecognized parameter '%s' found while processing %s" % (yaml_key, cls.__name__),
                    key_node.start_mark))
                continue

        key = param_name_map[yaml_key]
        expected_type = param_defs[key]['type']

        if expected_type == 'ZPropertyDefaultValue':
            # For zproperties, the actual data type of a default value
            # depends on the defined type of the zProperty.

            try:
                zPropType = [x[1].value for x in node.value if x[0].value == 'type'][0]
            except Exception:
                # type was not specified, so we assume the default (string)
                zPropType = 'string'

            try:
                expected_type = {
                    'boolean': "bool",
                    'int': "int",
                    'float': "float",
                    'string': "str",
                    'password': "str",
                    'lines': "list(str)"
                }.get(zPropType, 'str')
            except KeyError:
                yaml_error(loader, yaml.constructor.ConstructorError(
                    None, None,
                    "Invalid zProperty type_ '%s' for property %s found while processing %s" % (zPropType, key, cls.__name__),
                    key_node.start_mark))
                continue

        try:
            if expected_type == "bool":
                params[key] = loader.construct_yaml_bool(value_node)
            elif expected_type.startswith("dict(SpecsParameter("):
                m = re.match('^dict\(SpecsParameter\((.*)\)\)$', expected_type)
                if m:
                    spectype = m.group(1)

                    if not isinstance(node, yaml.MappingNode):
                        yaml_error(loader, yaml.constructor.ConstructorError(
                            None, None,
                            "expected a mapping node, but found %s" % node.id,
                            node.start_mark))
                        continue
                    specs = OrderedDict()
                    for spec_key_node, spec_value_node in value_node.value:
                        spec_key = str(loader.construct_scalar(spec_key_node))

                        specs[spec_key] = construct_specsparameters(loader, spec_value_node, spectype)
                    params[key] = specs
                else:
                    raise Exception("Unable to determine specs parameter type in '%s'" % expected_type)
            elif expected_type.startswith("dict"):
                params[key] = loader.construct_mapping(value_node)
            elif expected_type == "float":
                params[key] = float(loader.construct_scalar(value_node))
            elif expected_type == "int":
                params[key] = int(loader.construct_scalar(value_node))
            elif expected_type == "list(class)":
                classnames = loader.construct_sequence(value_node)
                classes = []
                for c in classnames:
                    class_ = str_to_class(c)
                    if class_ is None:
                        # local reference to a class being defined in
                        # this zenpack.  (ideally we should verify that
                        # the name is valid, but this is not possible
                        # in a one-pass parsing of the yaml).
                        classes.append(c)
                    else:
                        classes.append(class_)
                # ZPL defines "class" as either a string representing a
                # class in this definition, or a class object representing
                # an external class.
                params[key] = classes
            elif expected_type == 'list(ExtraPath)':
                if not isinstance(value_node, yaml.SequenceNode):
                    raise yaml.constructor.ConstructorError(
                        None, None,
                        "expected a sequence node, but found %s" % value_node.id,
                        value_node.start_mark)
                extra_paths = []
                for path_node in value_node.value:
                    extra_paths.append(loader.construct_sequence(path_node))
                params[key] = extra_paths
            elif expected_type == "list(RelationshipSchemaSpec)":
                schemaspecs = []
                for s in loader.construct_sequence(value_node):
                    schemaspecs.append(str_to_relschemaspec(s))
                params[key] = schemaspecs
            elif expected_type.startswith("list"):
                params[key] = loader.construct_sequence(value_node)
            elif expected_type == "str":
                params[key] = str(loader.construct_scalar(value_node))
            elif expected_type == 'RelationshipSchemaSpec':
                schemastr = str(loader.construct_scalar(value_node))
                params[key] = str_to_relschemaspec(schemastr)
            elif expected_type == 'Severity':
                severitystr = str(loader.construct_scalar(value_node))
                params[key] = str_to_severity(severitystr)
            else:
                m = re.match('^SpecsParameter\((.*)\)$', expected_type)
                if m:
                    spectype = m.group(1)
                    params[key] = construct_specsparameters(loader, value_node, spectype)
                else:
                    raise Exception("Unhandled type '%s'" % expected_type)

        except yaml.constructor.ConstructorError, e:
            yaml_error(loader, e)
        except Exception, e:
            yaml_error(loader, yaml.constructor.ConstructorError(
                None, None,
                "Unable to deserialize %s object (param %s): %s" % (cls.__name__, key_node.value, e),
                value_node.start_mark), exc_info=sys.exc_info())

    return params


def represent_zenpackspec(dumper, obj):
    return represent_spec(dumper, obj, yaml_tag=u'!ZenPackSpec')


def construct_zenpackspec(loader, node):
    # create a unique log for this ZenPack
    name = find_name_from_node(loader)
    if name:
        log = ZPLOG.add_log(name, QUIET, LEVEL)
        # set the global LOG variable to ths instance for things like YAML errors
        global LOG
        LOG = log

    from spec.ZenPackSpec import ZenPackSpec

    params = construct_spec(ZenPackSpec, loader, node)
    name = params.pop("name")
    params['log'] = LOG

    fatal = not getattr(loader, 'warnings', False)
    yaml_errored = getattr(loader, 'yaml_errored', False)

    try:
        return ZenPackSpec(name, **params)
    except Exception, e:
        if yaml_errored and not fatal:
            LOG.error("(possibly because of earlier errors) %s" % e)
        else:
            raise

    return None

def find_name_from_node(loader):
    '''determine zenpack name'''
    for k in loader.recursive_objects.keys():
        for v in k.value:
            if isinstance(v, tuple) and len(v) == 2:
                key, value = str(v[0].value), str(v[1].value)
                if key == 'name':
                    return value
    return None

def relname_from_classname(classname, plural=False):
    """Return relationship name given classname and plural flag."""

    if '.' in classname:
        classname = classname.replace('.', '_').lower()

    relname = list(classname)
    for i, c in enumerate(classname):
        if relname[i].isupper():
            relname[i] = relname[i].lower()
        else:
            break

    return ''.join((''.join(relname), 's' if plural else ''))


#### Deprecated? These appear to be unused 


def ucfirst(text):
    """Return text with the first letter uppercased.

    This differs from str.capitalize and str.title methods in that it
    doesn't lowercase the remainder of text.

    """
    return text[0].upper() + text[1:]


def update(d, u):
    """Return dict d updated with nested data from dict u."""
    for k, v in u.iteritems():
        if isinstance(v, collections.Mapping):
            r = update(d.get(k, {}), v)
            d[k] = r
        else:
            d[k] = u[k]
    return d


def class_to_str(class_):
    return class_.__module__ + "." + class_.__name__


def construct_relschemaspec(loader, node):
    schemastr = str(loader.construct_scalar(node))
    return str_to_relschemaspec(schemastr)

