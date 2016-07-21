OrderedDict = None

try:
    # included in standard lib from Python 2.7
    from collections import OrderedDict
except ImportError:
    # try importing the backported drop-in replacement
    # it's available on PyPI
    try:
        from ordereddict import OrderedDict
    except ImportError:
        OrderedDict = None