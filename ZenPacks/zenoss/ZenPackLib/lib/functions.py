import os
import importlib
import collections
import imp
import sys
import operator
import re
from Products.AdvancedQuery.AdvancedQuery import _BaseQuery as BaseQuery

from Products.ZenModel.Device import Device as BaseDevice
from Products.Zuul.infos.device import DeviceInfo as BaseDeviceInfo
from Products.ZenModel.DeviceComponent import DeviceComponent as BaseDeviceComponent
from Products.Zuul.infos.component import ComponentInfo as BaseComponentInfo

from .utils import yaml_installed
from .helpers.ZenPackLibLog import ZenPackLibLog


ZPLOG = ZenPackLibLog()
LOG = ZPLOG.defaultlog


# Default log settings
QUIET=True
LEVEL=0


# Private Functions ######################################################### 


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
        LOG.debug("Catalog {}Search not found at {}.  It should be created when the first included component is indexed".format(name, scope))
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
            raise ValueError("parse error in relationships_from_yuml at {}".format(line))

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



