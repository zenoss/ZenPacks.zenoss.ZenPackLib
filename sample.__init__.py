##############################################################################
#
# Copyright (C) Zenoss, Inc. 2013-2014, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

"""ZenPacks.zenoss.Cisco.APIC - Cisco APIC monitoring for Zenoss.

This module contains initialization code for the ZenPack. Everything in
the module scope will be executed at startup by all Zenoss Python
processes.

The initialization order for ZenPacks is defined by
$ZENHOME/ZenPacks/easy-install.pth.

"""

from . import zenpacklib


RELATIONSHIPS_YUML = """
[APIC]++-[FabricPod]
[APIC]++-[FvTenant]
[FabricPod]++-[FabricNode]
[FabricNode]++-[CnwAggrIf]
[FabricNode]++-[CnwPhysIf]
[FabricNode]++-[EqptCPU]
[FabricNode]++-[EqptLC]
[EqptCPU]++-[EqptCore]
[EqptLC]++-[EqptFabP]
[FvTenant]++-[FvBD]
[FvTenant]++-[VzBrCP]
[FvTenant]++-[FvAp]
[FvAp]++-[FvAEPg]
[FvAEPg]++-[FvRsProv]
[FvAEPg]++-[FvRsCons]
// non-containing
[FvBD]1-.-*[FvAEPg]
[VzBrCP]1-.-*[FvRsProv]
[VzBrCP]1-.-*[FvRsCons]
"""

CFG = zenpacklib.ZenPackSpec(
    name=__name__,

    zProperties={
        'DEFAULTS': {'category': 'Cisco APIC'},

        'zCiscoAPICHost': {},
        'zCiscoAPICPort': {'type': 'int', 'default': 80},
        'zCiscoAPICUser': {'default': 'admin'},
        'zCiscoAPICPassword': {'default': 'password'},
        'zCiscoAPICHealthInterval': {'type': 'int', 'default': 300},
    },

    classes={
        'DEFAULTS': {'base': 'ManagedObject'},

        ## Device Types ###############################################

        'APIC': {
            'base': zenpacklib.Device,
            'meta_type': 'CiscoAPIC',
        },

        ## Component Base Types #######################################

        'ManagedObjectBase': {
            'base': object,

            'properties': {
                'apic_classname': {
                    'label': 'ACI Object Class',
                },
                'apic_dn': {
                    'label': 'ACI Distinguished Name (DN)',
                    'index_type': 'field',
                },
                'apic_health_dn': {
                    'label': 'ACI Health Distinguished Name (DN)',
                },
            },
        },

        'ManagedObject': {
            'base': ('ManagedObjectBase', zenpacklib.Component),
        },

        'ManagedHardwareObject': {
            'base': ('ManagedObjectBase', zenpacklib.HardwareComponent),
        },

        ## Component Types ############################################

        ### uni/... ###################################################

        'FvTenant': {
            'meta_type': 'CiscoAPICTenant',
            'label': 'Tenant',
            'order': 11,
            'impacted_by': ['fvAps'],
        },

        'FvAp': {
            'meta_type': 'CiscoAPICApplication',
            'label': 'Application',
            'order': 12,
            'impacted_by': ['fvAEPgs'],
        },

        'FvAEPg': {
            'meta_type': 'CiscoAPICApplicationEndpointGroup',
            'label': 'Application Endpoint Group',
            'short_label': 'Endpoint Group',
            'label_width': 80,
            'order': 13,
            'impacted_by': ['fvBD', 'fvRsConss'],
        },

        'VzBrCP': {
            'meta_type': 'CiscoAPICContract',
            'label': 'Contract',
            'order': 14,
            'impacted_by': ['fvRsProvs'],
        },

        'FvRsProv': {
            'meta_type': 'CiscoAPICContractProvided',
            'label': 'Contract Provided',
            'plural_label': 'Contracts Provided',
            'short_label': 'Provides',
            'plural_short_label': 'Provides',
            'order': 14.1,
            'impacted_by': ['fvAEPg'],
        },

        'FvRsCons': {
            'meta_type': 'CiscoAPICContractConsumed',
            'label': 'Contract Consumed',
            'plural_label': 'Contracts Consumed',
            'short_label': 'Consumes',
            'plural_short_label': 'Consumes',
            'order': 14.2,
            'impacted_by': ['vzBrCP'],
        },

        'FvBD': {
            'meta_type': 'CiscoAPICBridgeDomain',
            'label': 'Bridge Domain',
            'order': 15,
            'impacted_by': ['fabricPods'],  # TODO: Only for demo.
        },

        ### topology/... ##############################################

        'FabricPod': {
            'meta_type': 'CiscoAPICFabricPod',
            'label': 'Fabric Pod',
            'order': 20,
            'impacted_by': ['fabricNodes'],
        },

        'FabricNode': {
            'meta_type': 'CiscoAPICFabricNode',
            'label': 'Fabric Node',
            'label_width': 65,
            'content_width': 100,
            'order': 21,
            'properties': {
                'role': {
                    'label': 'Role',
                },
            },
            'impacted_by': ['eqptCPUs'],
            'monitoring_templates': ['Health', 'FabricNode'],
        },

        'EqptLC': {
            'base': 'ManagedHardwareObject',
            'meta_type': 'CiscoAPICEqptLC',
            'label': 'Line Card',
            'order': 22,
            'impacted_by': ['fabricNode'],
            'monitoring_templates': ['Health', 'LineCard'],
        },

        'EqptFabP': {
            'base': 'ManagedHardwareObject',
            'meta_type': 'CiscoAPICEqptFabP',
            'label': 'Fabric Port',
            'order': 23,
            'impacted_by': ['eqptLC'],
            'monitoring_templates': ['Health', 'FabricPort'],
        },

        'CnwAggrIf': {
            'meta_type': 'CiscoAPICAggregateInterface',
            'label': 'Aggregate Interface',
            'short_label': 'Agg. Interface',
            'order': 24,
            'impacted_by': ['fabricNode'],
        },

        'CnwPhysIf': {
            'meta_type': 'CiscoAPICPhysicalInterface',
            'label': 'Physical Interface',
            'short_label': 'Phys. Interface',
            'order': 25,
            'impacted_by': ['fabricNode'],
        },

        'EqptCPU': {
            'meta_type': 'CiscoAPICCPU',
            'label': 'CPU',
            'order': 26,
            'impacted_by': ['eqptCores'],
        },

        'EqptCore': {
            'meta_type': 'CiscoAPICCPUCore',
            'label': 'CPU Core',
            'order': 27,
        },
    },

    class_relationships=zenpacklib.relationships_from_yuml(RELATIONSHIPS_YUML),
)

CFG.create()
