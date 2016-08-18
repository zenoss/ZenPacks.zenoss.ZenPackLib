##############################################################################
#
# Copyright (C) Zenoss, Inc. 2016, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################
import collections
import re
from .helpers.ZenPackLibLog import DEFAULTLOG


"""
    Deprecated? 
    The following code appears to be unused 
"""


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
    from .spec.Spec import Spec
    spec = Spec()

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
            left_relname = spec.relname_from_classname(
                right_class, plural=left_type != 'ToOne')

        if not right_relname:
            right_relname = spec.relname_from_classname(
                left_class, plural=right_type != 'ToOne')

        from .spec.RelationshipSchemaSpec import RelationshipSchemaSpec
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

