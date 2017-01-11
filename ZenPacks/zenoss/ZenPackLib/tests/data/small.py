RELATIONSHIPS_YUML = """
// containing
[SmallDevice]++-[ComponentA]
// non-containing 1:M
[ComponentA]*parentComponent-childComponents1[ComponentA]
// non-containing 1:1
[ComponentA]1-.-1[ComponentB]
"""

CFG = dict(
    name=__name__,

    zProperties={
        'zSmall':    {}
    },

    device_classes={
        '/Small': {
            'create': True,
            'remove': False
        }
    },

    classes={
        'SmallDevice': {
            'base': zenpacklib.Device,
            'label': 'Small Device',
        },

        'ComponentA': {
            'base': zenpacklib.Component,
            'properties': {
                'sizeInBytes':  {'type_': 'int',
                                 'renderer': 'Zenoss.render.bytesString',
                                 'label': 'Size'},
            }
        },

        'ComponentB': {
            'base': zenpacklib.Component,
            'properties': {
                'color':  {'label': 'Color'},
            }
        }
    },

    class_relationships=zenpacklib.relationships_from_yuml(RELATIONSHIPS_YUML),
)
