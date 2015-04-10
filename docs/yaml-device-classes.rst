.. _device-classes:

##############
Device Classes
##############

Device classes are the functional categorization mechanism for Zenoss devices.
Everything about how a device is modeled and monitored is controlled by its
device class unless the device class configuration is overridden specifically
for the device.

Example device classes that are a default part of every Zenoss system:

* /Discovered
* /Network
* /Server

Device classes are one of the most common items a ZenPack would add to Zenoss.


.. _adding-device-classes:

*********************
Adding Device Classes
*********************

To add a device class to your ZenPack you must include a *device_classes*
section to your YAML file. The following example shows an example of adding a
device class.

.. code-block:: yaml

   device_classes:
     /Server/ACME/Widgeter:
       remove: true

The *remove* field controls whether the device class will be removed from
Zenoss if the ZenPack is removed. It defaults to false. In this example we set
it to true because we do want our custom device class removed if the ZenPack
that supports it is removed.

Each device class listed in *device_classes* will be created when the ZenPack
is installed. The device classes will be created recursively if necessary.
Meaning that if the /Server or /Server/ACME device classes don't already exist,
they will be automatically created.

.. _setting-zProperties:

Setting zProperties
===================

You can also set zProperty values for each device class. These values will be
set each time the ZenPack is installed.

.. code-block:: yaml

   device_classes:
     /Server/ACME/Widgeter:
       remove: true
       zProperties:
         zWidgeterEnable: true
         zWidgeterInterval: 60

The referenced zProperties must already exist in the Zenoss system, or be
added by your ZenPack via a global :ref:`zProperties` entry.

Adding Monitoring Templates
===========================

Within each device class entry you can add monitoring templates. See the
following example for adding a simple monitoring template with a single
COMMAND datasource.

.. code-block:: yaml

   device_classes:
     /Server/ACME/Widgeter:
       zProperties:
         zDeviceTemplates:
           - Device

       templates:
         Device:
           description: ACME Widgeter monitoring.

           datasources:
             phony:
               type: COMMAND
               parser: Nagios
               commandTemplate: "echo OK|percent=100"

               datapoints:
                 percent: {}

           graphs:
             Phoniness:
               units: percent
               miny: 0
               maxy: 100

               graphpoints:
                 Phoniness:
                   dpName: phony_percent
                   format: "%7.2lf%%"
                   lineType: AREA

This *Device* monitoring template will be added to the /Server/ACME/Widgeter
device class each time the ZenPack is installed. This doesn't explicitly bind
the monitoring template to the device class. To do that you need to set
*zDeviceTemplates* as shown in the example.

See :ref:`monitoring-templates` for more information on creating monitoring
templates.


.. _device-class-fields:

*******************
Device Class Fields
*******************

The following fields are valid for a device class entry.

path
  :Description: Path (e.g. /Server/ACME/Widgeter). Must begin with "/".
  :Required: Yes
  :Type: string
  :Default Value: *(implied from key in device_classes map)*

remove
  :Description: Should the device class be removed when the ZenPack is removed?
  :Required: No
  :Type: boolean
  :Default Value: false

zProperties
  :Description: zProperty values to set on the device class.
  :Required: No
  :Type: map<name, value>
  :Default Value: {} *(empty map)*

templates
  :Description: Monitoring templates to add to the device class.
  :Required: No
  :Type: map<name, :ref:`Monitoring Template <monitoring-template-fields>`>
  :Default Value: {} *(empty map)*
