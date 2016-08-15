import yaml
import os
import re
import sys
import importlib
import keyword
from collections import OrderedDict
from ..functions import ZENOSS_KEYWORDS, JS_WORDS, relname_from_classname, find_keyword_cls
from .ZenPackLibLog import ZPLOG, LOG
from .Dumper import get_zproperty_type


class Loader(yaml.Loader):
    """
        These subclasses exist so that each copy of zenpacklib installed on a
        zenoss system provide their own loader (for add_constructor and yaml.load)
        and its own dumper (for add_representer) so that the proper methods will
        be used for this specific zenpacklib.
    """

    LOG=LOG
    QUIET=False
    LEVEL=0

    def type_map(self, node):
        '''map yaml node to python data type'''
        map = {'int': int,
               'float': float, 
               'str': str,
               'unicode': unicode,
               'bool': bool,
               'binary': str,
               'set': set,
               'seq': list,
               'map': dict}
        if 'null' in node.tag:
            return None
        for k in map.keys():
            if k in node.tag:
                try:
                    return map.get(k,'str')(node.value)
                except:
                    pass
        return self.construct_scalar(node)

    def dict_constructor(self, node):
        """constructor for OrderedDict"""
        return OrderedDict(self.construct_pairs(node))

    def construct_specsparameters(self, node, spectype):
        """constructor for SpecsParameters"""
        from ..spec.Spec import Spec
        spec_class = {x.__name__: x for x in Spec.__subclasses__()}.get(spectype, None)

        if not spec_class:
            self.yaml_error(yaml.constructor.ConstructorError(
                None, None,
                "Unrecognized Spec class {}".format(spectype),
                node.start_mark))
            return

        if not isinstance(node, yaml.MappingNode):
            self.yaml_error(yaml.constructor.ConstructorError(
                None, None,
                "expected a mapping node, but found {}".format(node.id),
                node.start_mark))
            return

        param_defs = spec_class.init_params()
        specs = OrderedDict()
        for spec_key_node, spec_value_node in node.value:
            try:
                spec_key = str(self.construct_scalar(spec_key_node))
                self.verify_key(spec_class, param_defs, spec_key, spec_key_node.start_mark)

            except yaml.MarkedYAMLError, e:
                self.yaml_error(e)

            specs[spec_key] = self.construct_spec(spec_class, spec_value_node)

        return specs

    def construct_spec(self, cls, node):
        """
        Generic constructor for deserializing specs from YAML.   Should be
        the opposite of represent_spec, and works in the same manner (with its
        parsing and validation directed by the init_params of each spec class)
        """
        from ..spec.RRDDatapointSpec import RRDDatapointSpec
        if issubclass(cls, RRDDatapointSpec) and isinstance(node, yaml.ScalarNode):
            # Special case- we allow for a shorthand in specifying datapoint specs.
            return dict(shorthand=self.construct_scalar(node))

        param_defs = cls.init_params()
        params = {}
        if not isinstance(node, yaml.MappingNode):
            self.yaml_error(yaml.constructor.ConstructorError(
                None, None,
                "expected a mapping node, but found {}".format(node.id),
                node.start_mark))

        params['_source_location'] = "{}: {}-{}".format(
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
                    self.yaml_error(yaml.constructor.ConstructorError(
                        None, None,
                        "Only one ExtraParams parameter may be specified.",
                        node.start_mark))
                extra_params = key
                params[extra_params] = {}

        for key_node, value_node in node.value:
            yaml_key = str(self.construct_scalar(key_node))
            self.verify_key(cls, param_defs, yaml_key, key_node.start_mark)

            if yaml_key not in param_name_map:
                if extra_params:
                    # If an 'extra_params' parameter is defined for this spec,
                    # we take all unrecognized paramters and stuff them into
                    # a single parameter, which is a dictonary of "extra" parameters.
                    #
                    # Note that the values of these extra parameters need to be
                    # scalars, not nested maps or something like that.
                    #params[extra_params][yaml_key] = self.construct_scalar(value_node)
                    params[extra_params][yaml_key] = self.type_map(value_node)
                    continue
                else:
                    self.yaml_error(yaml.constructor.ConstructorError(
                        None, None,
                        "Unrecognized parameter '{}' found while processing {}".format(yaml_key, cls.__name__),
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
                    expected_type = get_zproperty_type(zPropType)

                except KeyError:
                    self.yaml_error(yaml.constructor.ConstructorError(
                        None, None,
                        "Invalid zProperty type_ '{}' for property {} found while processing {}".format(zPropType, key, cls.__name__),
                        key_node.start_mark))
                    continue

            try:
                if expected_type == "bool":
                    params[key] = self.construct_yaml_bool(value_node)
                elif expected_type.startswith("dict(SpecsParameter("):
                    m = re.match('^dict\(SpecsParameter\((.*)\)\)$', expected_type)
                    if m:
                        spectype = m.group(1)

                        if not isinstance(node, yaml.MappingNode):
                            self.yaml_error(yaml.constructor.ConstructorError(
                                None, None,
                                "expected a mapping node, but found {}".format(node.id),
                                node.start_mark))
                            continue
                        specs = OrderedDict()
                        for spec_key_node, spec_value_node in value_node.value:
                            spec_key = str(self.construct_scalar(spec_key_node))

                            specs[spec_key] = self.construct_specsparameters(spec_value_node, spectype)
                        params[key] = specs
                    else:
                        raise Exception("Unable to determine specs parameter type in '{}'".format(expected_type))
                elif expected_type.startswith("dict"):
                    params[key] = self.construct_mapping(value_node)
                elif expected_type == "float":
                    params[key] = float(self.construct_scalar(value_node))
                elif expected_type == "int":
                    params[key] = int(self.construct_scalar(value_node))
                elif expected_type == "list(class)":
                    classnames = self.construct_sequence(value_node)
                    classes = []
                    for c in classnames:
                        class_ = self.str_to_class(c)
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
                            "expected a sequence node, but found {}".format(value_node.id),
                            value_node.start_mark)
                    extra_paths = []
                    for path_node in value_node.value:
                        extra_paths.append(self.construct_sequence(path_node))
                    params[key] = extra_paths
                elif expected_type == "list(RelationshipSchemaSpec)":
                    schemaspecs = []
                    for s in self.construct_sequence(value_node):
                        schemaspecs.append(self.str_to_relschemaspec(s))
                    params[key] = schemaspecs
                elif expected_type.startswith("list"):
                    params[key] = self.construct_sequence(value_node)
                elif expected_type == "str":
                    params[key] = str(self.construct_scalar(value_node))
                elif expected_type == 'RelationshipSchemaSpec':
                    schemastr = str(self.construct_scalar(value_node))
                    params[key] = self.str_to_relschemaspec(schemastr)
                elif expected_type == 'Severity':
                    severitystr = str(self.construct_scalar(value_node))
                    params[key] = self.str_to_severity(severitystr)
                else:
                    m = re.match('^SpecsParameter\((.*)\)$', expected_type)
                    if m:
                        spectype = m.group(1)
                        params[key] = self.construct_specsparameters(value_node, spectype)
                    else:
                        raise Exception("Unhandled type '{}'".format(expected_type))

            except yaml.constructor.ConstructorError, e:
                self.yaml_error(e)
            except Exception, e:
                self.yaml_error(yaml.constructor.ConstructorError(
                    None, None,
                    "Unable to deserialize {} object (param {}): {}".format(cls.__name__, key_node.value, e),
                    value_node.start_mark), exc_info=sys.exc_info())

        return params

    def construct_zenpackspec(self, node):
        """"""
        log_name = self.find_name_from_node()
        if log_name:
            self.LOG = ZPLOG.add_log(log_name, quiet=self.QUIET, level=self.LEVEL)

        from ..spec.ZenPackSpec import ZenPackSpec
        params = self.construct_spec(ZenPackSpec, node)
        params['log'] = self.LOG
        name = params.pop("name")

        fatal = not getattr(self, 'warnings', False)
        yaml_errored = getattr(self, 'yaml_errored', False)

        try:
            return ZenPackSpec(name, **params)
        except Exception, e:
            if yaml_errored and not fatal:
                self.LOG.error("(possibly because of earlier errors) {}".format(e))
            else:
                raise

        return None

    def construct_relschemaspec(self, node):
        """"""
        schemastr = str(self.construct_scalar(node))
        return self.str_to_relschemaspec(schemastr)

    def str_to_class(self, classstr):
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
        if modname in ['zenpacklib', 'ZenPacks.zenoss.ZenPackLib.lib.factory.ModelTypeFactory']:
            modname = 'ZenPacks.zenoss.ZenPackLib.zenpacklib'
        try:
            class_ = getattr(importlib.import_module(modname), classname)
        except Exception, e:
            raise ValueError("Class '{}' is not valid: {}".format(classstr, e))

        return class_

    def str_to_relschemaspec(self, schemastr):
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
            raise ValueError("RelationshipSchemaSpec '{}' is not valid" .format(schemastr))

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

    def str_to_severity(self, value):
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

    def format_message(self, e):
        message = []

        mark = e.context_mark or e.problem_mark
        if mark:
            position = "{}:{}:{}".format(mark.name, mark.line + 1, mark.column + 1)
        else:
            position = "[unknown]"
        if e.context is not None:
            message.append(e.context)

        if e.problem is not None:
            message.append(e.problem)

        if e.note is not None:
            message.append("(note: {})".format(e.note))

        return "{}: {}".format(position, message)

    def yaml_warning(self, e):
        # Given a MarkedYAMLError exception, either log or raise
        # the error, depending on the 'fatal' argument.
        self.LOG.warn(self.format_message(e))

    def yaml_error(self, e, exc_info=None):
        # Given a MarkedYAMLError exception, either log or raise
        # the error, depending on the 'fatal' argument.
        fatal = not getattr(self, 'warnings', False)
        setattr(self, 'yaml_errored', True)
        if exc_info:
            # When we're given the original exception (which was wrapped in
            # a MarkedYAMLError), we can provide more context for debugging.
            from traceback import format_exc
            e.note = "\nOriginal exception:\n{}".format(format_exc(exc_info))
        if fatal:
            raise e
        self.LOG.error(self.format_message(e))

    def verify_key(self, cls, params, key, start_mark):
        # always ok to use a param name (description, name, etc.)
        if key in params.keys():
            return True
        # never use a python reserved word
        if key in keyword.kwlist:
            self.yaml_error(yaml.constructor.ConstructorError(
                None, None,
                "Found reserved keyword '{}' while processing {}".format(key, cls.__name__),
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
                self.yaml_warning(yaml.constructor.ConstructorError(
                    None, None,
                    "Found reserved Zenoss keyword '{}' from {}".format(key, klasses),
                    start_mark))
        return False

    def find_name_from_node(self):
        '''determine zenpack name'''
        for k in self.recursive_objects.keys():
            for v in k.value:
                if isinstance(v, tuple) and len(v) == 2:
                    key, value = str(v[0].value), str(v[1].value)
                    if key == 'name':
                        return value
        return None


Loader.add_constructor(u'tag:yaml.org,2002:map', Loader.dict_constructor)
Loader.add_constructor(u'!ZenPackSpec', Loader.construct_zenpackspec)
yaml.add_path_resolver(u'!ZenPackSpec', [], Loader=Loader)

