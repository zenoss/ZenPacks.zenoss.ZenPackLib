from ..helpers.ZenPackLibLog import DEFAULTLOG as LOG

import string

class Color(str):
    """Hexadecimal string representation for color"""
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
                LOG.warning('Max length exceeded, truncating: {}'.format(value))
                value = value[:6]
            elif len(value) < 6:
                LOG.warning('Min length not met, padding: {}'.format(value))
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
            LOG.warning('Invalid Hex value given: {}, returning {}'.format(value, fix_hex(value)))
            value = fix_hex(value)
        return value.upper()


class Severity(int):
    """Represent severity as number or text while preserving user designation"""

    orig = None
    num = None
    text = None

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
                LOG.warning("Invalid severity value ({}), increasing to 0".format(value))
                value = 0
            elif value > 5:
                LOG.warning("Invalid severity value ({}), reducing to 5".format(value))
                value = 5
        except (TypeError, ValueError):
            if isinstance(value, str):
                if value.lower() in cls._valid_text:
                    value = cls.to_num.get(value.lower())
                else:
                    sev_num_txt = [str(x) for x in cls._valid_num]
                    LOG.warning("Invalid severity value ({}), "\
                        "must be one of: ({}) or ({}).".format(value,
                                                ', '.join(cls._valid_text),
                                                ', '.join(sev_num_txt)))
                    value = 3
        return value

    def __init__(self, value):
        self.orig = value
        self.text = self.to_text.get(self)

