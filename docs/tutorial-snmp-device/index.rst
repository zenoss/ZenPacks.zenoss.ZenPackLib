.. _tutorial-snmp-device:

#########################
Monitoring an SNMP Device
#########################

The following sections will describe a common approach to monitoring an SNMP-
enabled device. We'll start with the basics that can be done without writing a
line of code, and then move on to more sophisticated capabilities.

For purposes of this guide we'll be building a ZenPack to support a NetBotz
environmental sensor device. This device has a variety of sensors that monitor
temperature, humidity, dew point, audio levels and air flow.

.. note::

    This tutorial assumes your system is already setup as described in
    :ref:`development-environment` and :ref:`getting-started`.

.. toctree::
    :maxdepth: 2

    snmp-tools
    device-monitoring
    device-modeling
    component-modeling
    component-monitoring
    snmp-traps
