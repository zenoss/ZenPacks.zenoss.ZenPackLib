from ..helpers.ZenPackLibLog import DEFAULTLOG as LOG
import string
from Products.ZenRelations.RelSchema import ToMany, ToManyCont, ToOne


class Property(object):
    """Represent _properties entry"""
    _property_map = {'boolean': 'bool',
                     'int': 'int',
                     'float': 'float',
                     'string': 'str',
                     'password': 'str',
                     'lines': 'list(str)',
                     'text': 'list(str)'
                     }

    def __new__(cls, value, type_='string', default=None):
        return object.__new__(cls, cls.validate(value, type_, default))

    @classmethod
    def validate(cls, value, type, default):
        # self._pytype = self._property_map.get(value, 'str')
        return value

    def __init__(self, value, type_='string', default=None):
        self.name = value
        self.type_ = type_
        self.py_type = self._property_map.get(self.type_)
        self.default = default or self.get_default()

    def get_default(self):
        return {'string': '',
                'password': '',
                'lines': [],
                'boolean': False,
            }.get(self.type_, None)


class Relationship(str):
    cls = None
    name = None
    cardinality = None

    _relTypeCardinality = {
        'ToOne': '1',
        'ToMany': 'M',
        'ToManyCont': 'MC'
    }

    _relTypeClasses = {
        "ToOne": ToOne,
        "ToMany": ToMany,
        "ToManyCont": ToManyCont
    }

    _relTypeNames = {
        ToOne: "ToOne",
        ToMany: "ToMany",
        ToManyCont: "ToManyCont"
    }

    def __new__(cls, value):
        return str.__new__(cls, cls.validate(value))

    @classmethod
    def validate(cls, value):
        if not value:
            raise ValueError('Relationship cannot be None')
        if not isinstance(value, str):
            raise ValueError('Invalid type ({}) given for Relationship'.format(type(value)))
        if value not in ['ToOne', 'ToMany', 'ToManyCont']:
            raise ValueError('Invalid value ({}) given for Relationship'.format(value))
        return value

    def __init__(self, value):
        self.name = value
        self.cls = self._relTypeClasses.get(value)
        self.cardinality = self._relTypeCardinality.get(value)


class Color(str):
    """Hexadecimal string representation for color"""
    LOG = LOG

    def __new__(cls, value):
        return str.__new__(cls, cls.validate(value))

    @classmethod
    def validate(cls, value):
        if not value:
            return value
        value = str(value)
        # truncate or pad with 0s
        def check_length(value):
            if len(value) > 6:
                cls.LOG.warning('Max length exceeded, truncating: {}'.format(value))
                value = value[:6]
            elif len(value) < 6:
                cls.LOG.warning('Min length not met, padding: {}'.format(value))
                value += '0'
                value = check_length(value)
            return value

        def is_hex(value):
            return all(v in string.hexdigits for v in value)

        def fix_hex(value):
            '''fix invalid hex values'''
            color = ''
            for v in value:
                if not v in string.hexdigits:
                    v = 'F'
                color += v
            return color

        value = check_length(value)

        if not is_hex(value):
            cls.LOG.warning('Invalid Hex value given: {}, returning {}'.format(value, fix_hex(value)))
            value = fix_hex(value)
        return value.upper()


class Severity(int):
    """Represent severity as number or text while preserving user designation"""

    orig = None
    num = None
    text = None
    LOG = LOG

    _valid_text = ['crit', 'critical', 'err', 'error',
                   'warn', 'warning', 'info', 'information', 'informational',
                   'debug', 'debugging', 'clear']

    _valid_num = [0, 1, 2, 3, 4, 5]

    to_text = {5: 'critical', 4: 'error', 3: 'warn',
               2: 'info', 1: 'debug', 0: 'clear'}

    to_num = {'crit': 5, 'critical': 5, 'err': 4, 'error': 4,
               'warn': 3, 'warning': 3,
               'info': 2, 'information': 2, 'informational': 2,
               'debug': 1, 'debugging': 1,
               'clear': 0}

    def __new__(cls, value):
        if not value:
            return value
        return int.__new__(cls, cls.validate(value))

    @classmethod
    def validate(cls, value):
        try:
            value = int(value)
            if value < 0:
                cls.LOG.warning("Invalid severity value ({}), increasing to 0".format(value))
                value = 0
            elif value > 5:
                cls.LOG.warning("Invalid severity value ({}), reducing to 5".format(value))
                value = 5
        except (TypeError, ValueError):
            if isinstance(value, str):
                if value.lower() in cls._valid_text:
                    value = cls.to_num.get(value.lower())
                else:
                    sev_num_txt = [str(x) for x in cls._valid_num]
                    cls.LOG.warning("Invalid severity value ({}), "\
                        "must be one of: ({}) or ({}).".format(value,
                                                ', '.join(cls._valid_text),
                                                ', '.join(sev_num_txt)))
                    value = 3
        return value

    def __init__(self, value):
        self.orig = value
        self.text = self.to_text.get(self)

