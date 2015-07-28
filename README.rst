######################
Welcome to zenpacklib!
######################

zenpacklib is a Python library that makes building common types of ZenPacks
simpler, faster, more consistent and more accurate.

ZenPacks are a plugin mechanism for Zenoss. Most commonly they're used to
extend Zenoss to monitor new types of targets. It is specifically this common
case that zenpacklib is designed to simplify.


************************
What does zenpacklib do?
************************

Specifically zenpacklib allows all of the following to be described in YAML, and
extended in Python only if necessary.

* zProperties (a.k.a. Configuration Properties)
* Device Classes
* Monitoring Templates
* New Device and Component Types
* Relationships between Device and Component Types

It is this combination of declarative YAML and imperative Python extension that
allows zenpacklib to make easy things easy and hard things possible.


**************************
Who should use zenpacklib?
**************************

You should consider using zenpacklib if any of the following statements apply
to you.

* Your ZenPack will only contain monitoring templates, but you prefer creating
  YAML files over creating monitoring templates by clicking around the Zenoss
  web interface.
* Your ZenPack needs to add zProperties.
* Your ZenPack needs to add new device or component types and relationships
  between them.

You should even consider using zenpacklib if you are an experience ZenPack
developer and already know how to create new device and component types. You
will find that the amount of boilerplate code you need to write is drastically
reduced, if not elimited, by using zenpacklib. You will still have all of the
power of Python to extend upon the functionality provided by zenpacklib.

If your ZenPack only consists of configuration you can create and add to a
ZenPack using the Zenoss web interface, and you're more comfortable clicking
through the web interface than create a YAML file, you probably should use
Zenoss' built-in capabilities instead of zenpacklib.

********************************
How do I start using zenpacklib?
********************************

Create a skeleton ZenPack in the Zenoss UI

Go to the Advanced -> Settings -> ZenPacks in the Zenoss web interface.
Choose Create a ZenPack... from the gear menu above the list of ZenPacks.

*******************
Download zenpacklib
*******************

Creating the ZenPack will create the ZenPack’s source directory under $ZENHOME/ZenPacks/ZenPacks.acme.Widgeter. Run the following commands as the zenoss user to make this directory, and it’s important subdirectory more easily accessible:

$ export ZP_TOP_DIR=$ZENHOME/ZenPacks/ZenPacks.acme.Widgeter
$ export ZP_DIR=$ZP_TOP_DIR/ZenPacks/acme/Widgeter

Then download the latest zenpacklib from GitHub into the ZenPack’s main code directory with the following commands.

cd $ZP_DIR
wget https://raw.githubusercontent.com/zenoss/zenpacklib/master/zenpacklib.py

**********************
Create the ZenPackSpec
**********************

Once zenpacklib.py is in $ZP_DIR you can create what is called a ZenPackSpec in the ZenPack’s __init__.py. This ZenPackSpec will define the specification for the ZenPack. Specifically its name, zProperties, classes and class relationships.

********************
ZenPackSpec examples
********************

The following example shows an example of adding new zProperties. Note the
special *DEFAULTS* entry. You'll find that this is supported in many places as
a way to set default properties for all other entries in a section. In this
case it will set *category* to ACME Widgeter for the zWidgeterEnable and
zWidgeterInterval zProperties.

.. code-block:: yaml

    name: ZenPacks.acme.Widgeter

    zProperties:
      DEFAULTS:
        category: ACME Widgeter

      zWidgeterEnable:
        type: boolean
        default: true

      zWidgeterInterval:
        type: string
        default: 300

Extending upon that example we can add a device class and monitoring template
complete with a datasource, threshold and graph.

.. code-block:: yaml

    device_classes:
      /Server/ACME/Widgeter:
          templates:
            Device:
              description: ACME Widgeter monitoring.
              targetPythonClass: ZenPacks.acme.Widgeter.Widgeter

              datasources:
                status:
                  type: COMMAND
                  parser: Nagios
                  commandTemplate: "echo OK|available=1"

                  datapoints:
                    available:
                      rrdtype: GAUGE
                      rrdmin: 0
                      rrdmax: 1

              thresholds:
                unavailable:
                  dsnames: [status_available]
                    eventClass: /Status
                    severity: Critical
                    minval: 1

              graphs:
                Availability:
                  units: percent
                  miny: 0
                  maxy: 100

                  graphpoints:
                    Availability:
                      dpName: status_available
                      rpn: 100,*
                      format: "%7.2lf%%"
                      lineType: AREA

Finally we can add a new device type, component type and relationship between
them.

.. code-block:: yaml

    classes:
      Widgeter:
        base: [zenpacklib.Device]
        meta_type: ACMEWidgeter

      Widget:
        base: [zenpacklib.Component]
        meta_type: ACMEWidget
        properties:
          flavor:
            label: Flavor
            type: string

    class_relationships:
      - Widgeter 1:MC Widget
