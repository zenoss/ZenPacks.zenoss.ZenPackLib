.. _monitoring-templates:

####################
Monitoring Templates
####################

Monitoring templates are containers for monitoring configuration. Specifically
datasources, thresholds and graphs. A monitoring template must be created to
perform periodic collection of data, associate thresholds with that data, or
define how that data should be graphed.


.. _location-and-binding:

********************
Location and Binding
********************

Two important concepts in understanding how monitoring templates are used are
location and binding. Location is the device class in which a monitoring
template is contained. Binding is the device class, device or component to
which a monitoring template is bound.

A monitoring template's location is important because it restricts to which
devices a the template may be bound. Assume you have a device named *widgeter1*
in the /Server/ACME/Widgeter device class that as a monitoring template named
*WidgeterHealth* bound. Zenoss will attempt to find a monitoring template
named *WidgeterHealth* in the following places in the following order.

1. On the *widgeter1* device.
2. In the /Server/ACME/Widgeter device class.
3. In the /Server/ACME device class.
4. In the /Server device class.
5. In the / device class.

The first template that matches by name will be used for the device. No
template will be bound if no matching template is found in any of these
locations.

It is because of this search up the hierarchy that allows the monitoring
template's location to be used to restrict to which devices it can be bound.
For example, by locating our monitoring template in the /Server/ACME device
class we make it available to be bound for all devices in /Server/ACME and
/Server/ACME/Widgeter, but we also make unavailable to be bound in other device
classes such as /Server or /Network/Cisco.

After deciding on the right location for a monitoring template should then
decide where it should be bound. Remember that to cause the template to be used
it must be bound. This is done by adding the template's name to the
*zDeviceTemplates* zProperty of a device class. See the following example that
shows how to bind the *WidgeterHealth* monitoring template to the
/Server/ACME/Widgeter device class.

.. code-block:: yaml

    name: ZenPacks.acme.Widgeter

    device_classes:
      /Server/ACME/Widgeter:
        zProperties:
          zDeviceTemplates:
            - WidgeterHealth
          
        templates:
          WidgeterHealth: {}

Note that zDeviceTemplates didn't have to be declared in the ZenPack's
zProperties field because it's a standard Zenoss zProperty.

.. note::

    Binding templates using zDeviceTemplates is only applicable for monitoring
    templates that should be bound to devices. See
    :ref:`classes-and-relationships` for information on how monitoring
    templates are bound to components.


.. _alternatives-to-yaml:

********************
Alternatives to YAML
********************

It's possible to create monitoring templates and add them to a ZenPack entirely
through the Zenoss web interface. If you don't have complex or many monitoring
templates to create and prefer to click through the web interface, you may
choose to create your monitoring templates this way instead of through the
`zenpack.yaml` file.

There are some advantages to defining monitoring templates in YAML.

* Using text-editor features such as search can be an easier way to make
  changes than clicking through the web interface.

* Having monitoring templates defined in the same document as the zProperties
  they use, and the device classes they're bound to can be easier to
  understand.

* Changes made to monitoring templates in YAML are much more diff-friendly than
  the same changes made through the web interface then exported to objects.xml.
  For those keeping ZenPack source in version control this can make changes
  clearer. For the same reason it can also be of benefit when multiple authors
  are working on the same ZenPack.

See :ref:`command-line-reference` for information on the `dump_templates` option
if you're interested in exporting monitoring templates already created in the
web interface to YAML.


.. _adding-monitoring-templates:

***************************
Adding Monitoring Templates
***************************

To add a monitoring template to `zenpack.yaml` you must first add the device
class where it is to be located. Then within this device class entry you must
add a templates field. The following example shows a *WidgeterHealth*
monitoring template being added to the /Server/ACME/Widgeter device class. It
also shows that template being bound to the device class by setting
zDeviceTemplates.

.. code-block:: yaml

    name: ZenPacks.acme.Widgeter

    device_classes:
      /Server/ACME/Widgeter:
        zProperties:
          zDeviceTemplates:
            - WidgeterHealth
          
        templates:
          WidgeterHealth:
            description: ACME Widgeter monitoring.

            datasources:
              health:
                type: COMMAND
                parser: Nagios
                commandTemplate: "echo OK|percent=100"

                datapoints:
                  percent:
                    rrdtype: GAUGE
                    rrdmin: 0
                    rrdmax: 100

            thresholds:
              unhealthy:
                dsnames: [health_percent]
                eventClass: /Status
                severity: Warning
                minval: 90

            graphs:
              Health:
                units: percent
                miny: 0
                maxy: 0

                graphpoints:
                  Health:
                    dpName: health_percent
                    format: "%7.2lf%%"


Many different entry types are shown in the above example. See the references below for more information on each.


.. _monitoring-template-fields:

**************************
Monitoring Template Fields
**************************

The following fields are valid for a monitoring template entry.

name
  :Description: Name (e.g. WidgeterHealth). Must be a valid Zenoss object ID.
  :Required: Yes
  :Type: string
  :Default Value: *(implied from key in templates map)*

description
  :Description: Description of the templates purpose and function.
  :Required: No
  :Type: string
  :Default Value: "" *(empty string)*

targetPythonClass
  :Description: Python module name (e.g. ZenPacks.acme.Widgeter.Widgeter) to which this template is intended to be bound.
  :Required: No
  :Type: string
  :Default Value: "" (empty string is equivalent to Products.ZenModel.Device)

datasources
  :Description: Datasources to add to the template.
  :Required: No
  :Type: map<name, :ref:`Datasource <datasource-fields>`>
  :Default Value: {} *(empty map)*

thresholds
  :Description: Thresholds to add to the template.
  :Required: No
  :Type: map<name, :ref:`Threshold <threshold-fields>`>
  :Default Value: {} *(empty map)*

graphs
  :Description: Graphs to add to the template.
  :Required: No
  :Type: map<name, :ref:`Graph <graph-fields>`>
  :Default Value: {} *(empty map)*

.. note::

  ZenPackLib also allows for defining a replacement or additional template by adding "-replacement" or "-additional" to the end of the template name.  For example, a defined *Device-replacement* template will replace the existing Device template on a device class.  A defined *Device-addition* template will be applied in addition to the existing Device template on a device class.


.. _datasource-fields:

Datasource Fields
=================

The following fields are valid for a datasource entry.

name
  :Description: Name (e.g. health). Must be a valid Zenoss object ID.
  :Required: Yes
  :Type: string
  :Default Value: *(implied from key in datasources map)*

type
  :Description: Type of datasource. See :ref:`datasource-types`.
  :Required: Yes
  :Type: string *(must be a valid source type)*
  :Default Value: None. Must be specified.

enabled
  :Description: Should the datasource be enabled by default?
  :Required: No
  :Type: boolean
  :Default Value: true

component
  :Description: Value for the *component* field on events generated by the datasource. Accepts TALES expressions.
  :Required: No
  :Type: string
  :Default Value: "" *(empty string)* -- can vary depending on type.

eventClass
  :Description: Value for the *eventClass* field on events generated by the datasource.
  :Required: No
  :Type: string
  :Default Value: "" *(empty string)* -- can vary depending on type.

eventKey
  :Description: Value for the *eventKey* field on events generated by the datasource.
  :Required: No
  :Type: string
  :Default Value: "" *(empty string)* -- can vary depending on type.

severity
  :Description: Value for the *severity* field on events generated by the datasource.
  :Required: No
  :Type: integer
  :Default Value: 3 *(0=Clear, 1=Debug, 2=Info, 3=Warning, 4=Error, 5=Critical)* -- can vary depending on type.

cycletime
  :Description: How often the datasource will be executed in seconds.
  :Required: No
  :Type: integer -- can vary depending on type.
  :Default Value: 300 -- can vary depending on type.

datapoints
  :Description: Datapoints to add to the datasource.
  :Required: No
  :Type: map<name, :ref:`Datapoint <datapoint-fields>`>
  :Default Value: {} *(empty map)*

Datasources also allow other ad-hoc options to be added not referenced in the
above list. This is because datasources are an extensible type in Zenoss, and
depending on the value of *type*, other fields may be valid.

.. _datasource-types:

Datasource Types
----------------

The following datasource types are valid on any Zenoss system. They are the
default types that are part of the platform. This list is not exhaustive as
datasources types are commonly added by ZenPacks.

SNMP
  :Description: Performs an SNMP GET operation using the *oid* field.
  :Availability: Zenoss Platform
  :Additional Fields:
    oid
      :Description: The SNMP OID to get.
      :Required: Yes
      :Type: string
      :Default Value: "" *(empty string)*

COMMAND
  :Description: Runs command in *commandTemplate* field.
  :Availability: Zenoss Platform
  :Additional Fields:
    commandTemplate
      :Description: The command to run.
      :Required: Yes
      :Type: string
      :Default Value: "" *(empty string)*

    usessh:
      :Description: Run command on bound device using SSH, or run it on the Zenoss collector server?
      :Required: No
      :Type: boolean
      :Default Value: false

    parser:
      :Description: Parser used to parse output from command.
      :Required: No
      :Type: string *(must be a valid parser name)*
      :Default Value: Nagios

.. todo:: Document COMMAND datasource parsers.

PING
  :Description: Pings (ICMP echo-request) an IP address.
  :Availability: Zenoss Platform
  :Additional Fields:
    cycleTime
      :Description: How many seconds between ping attempts. (note capitalization)
      :Required: No
      :Type: integer
      :Default Value: 60

    attempts:
      :Description: How many ping attempts to perform each cycle.
      :Required: No
      :Type: integer
      :Default Value: 2

    sampleSize
      :Description: How many echo requests to send with each attempt.
      :Required: No
      :Type: integer
      :Default Value: 1

Built-In
  :Description: No collection. Assumes associated data will be populated by an external mechanism.
  :Availability: Zenoss Platform
  :Additional Fields:
    None

.. todo:: Document commonly-used types added by ZenPacks.

.. _custom-datasource-types:

Custom Datasource and Datapoint Types
-------------------------------------

Some datasource (and datapoint) types are provided by a particular ZenPack and only available 
if that ZenPack is installed.  These types often have unique paramters that control their function.
ZenPackLib allows the specification of these parameters, but the degree of documentation for each 
varies.  As a result, designing YAML templates using these requires a bit of investigation.  The 
available properties depend on the datasource or datapoint type being used.  Currently, examination of 
the related source code is a good way to investigate them, but an alternative is given below.

The following exmaple demonstrates how to create a YAML template that relies on the 
ZenPacks.zenoss.CalculatedPerformance ZenPack.  Please note that the datasource properties used are 
not documented below, since they are provided by the CalculatedPerformance ZenPack.  

First, we want to determine a list of available parameters, and we can use ZenDMD to display them as follows:

.. code-block:: python

      # This is the reference class and its properties are documented here.
      from Products.ZenModel.RRDDataSource import RRDDataSource as Reference
      # replace the import path and class with the class you are interested in 
      from ZenPacks.zenoss.CalculatedPerformance.datasources.AggregatingDataSource \
         import AggregatingDataSource as Comparison
      # this prints out the list of non-standard properties and their types
      props = [p for p in Comparison._properties if p not in Reference._properties]
      print '\n'.join(['{} ({})'.format(p['id'], p['type']) for p in props])

In this case, we should see the following output:

.. code-block:: python

      targetMethod (string)
      targetDataSource (string)
      targetDataPoint (string)
      targetRRA (string)
      targetAsRate (boolean)
      debug (boolean)

An example tempalte using the CalculatedPerformance datasources might resemble the following:

.. code-block:: yaml

      name: ZenPacks.zenoss.ZenPackLib
      device_classes:
        /Device:
          templates:
            ExampleCalculatedPerformanceTemplate:
              datasources:
                # standard SNMP datasources
                memAvailReal:
                  type: SNMP
                  oid: 1.3.6.1.4.1.2021.4.6.0
                  datapoints:
                    memAvailReal: GAUGE
                memAvailSwap:
                  type: SNMP
                  oid: 1.3.6.1.4.1.2021.4.4.0
                  datapoints:
                    memAvailSwap: GAUGE
                # CalculatedPerformance datasources
                totalAvailableMemory
                  type: Calculated Performance
                  # "expression" paramter is unique to the 
                  # CalculatedPerformance datasource
                  expression: memAvailReal + memAvailSwap
                  datapoints:
                    totalAvailableMemory: GAUGE
                # Aggregated Datasource
                agg_out_octets:
                  # These are standard parameters
                  type: Datapoint Aggregator
                  # The following parameters are "extra" parameters,
                  # attributes of the "Datapoint Aggregator" datasource 
                  targetDataSource: ethernetcmascd_64
                  targetDataPoint: ifHCOutOctets
                  targetMethod: os.interfaces
                  # AggregatingDataPoint is subclassed from RRDDataPoint and 
                  # has the unique "operation" paramter
                  datapoints:
                    aggifHCOutOctets:
                      operation: sum

Further experimentation, though, is required to determine workable values for these properties, and creating
templates manually using the Zenoss GUI is a good way to do so.


.. _datapoint-fields:

Datapoint Fields
================

The following fields are valid for a datapoint entry.

name
  :Description: Name (e.g. percent). Must be a valid Zenoss object ID.
  :Required: Yes
  :Type: string
  :Default Value: *(implied from key in datapoints map)*

description
  :Description: Description of the datapoint's purpose and function.
  :Required: No
  :Type: string
  :Default Value: "" *(empty string)*

rrdtype
  :Description: Type of datapoint. Must be GAUGE or DERIVE.
  :Required: No
  :Type: string *(must be either GAUGE or DERIVE)*
  :Default Value: GAUGE

rrdmin
  :Description: Minimum allowable value that can be written to the datapoint. Any lower values will be ignored.
  :Required: No
  :Type: int
  :Default Value: None *(no lower-bound on acceptable values)*

rrdmax
  :Description: Maximum allowable value that can be written to the datapoint. Any higher values will be ignored.
  :Required: No
  :Type: int
  :Default Value: None *(no upper-bound on acceptable values)*

aliases
  :Description: Analytics aliases for the datapoint with optional RPN calculation. Learn more about `Reverse Polish Notiation <https://en.wikipedia.org/wiki/Reverse_Polish_notation>`_
  :Required: No
  :Type: map<name, formula>
  :Default Value: {} *(empty map)*
  :Example 1: aliases: { datapointName: '1024,*' }
  :Example 2: aliases: datapointName

Datapoints also allow other ad-hoc options to be added not referenced in the
above list. This is because datapoints are an extensible type in Zenoss, and
depending on the value of the datasource's *type*, other fields may be valid.

YAML datapoint specification also supports the use of an alternate "shorthand" notation for brevity.  Shorthand 
notation follows a pattern of `RRDTYPE_MIN_X_MAX_X` where RRDTYPE is one of "GAUGE, DERIVE, COUNTER, RAW", 
and the "MIN_X"/"MAX_X" parameters are optional.  

For example, DERIVE, DERIVE_MIN_0, and DERIVE_MIN_0_MAX_100 are all valid shorthand notation.

.. _threshold-fields:

Threshold Fields
================

The following fields are valid for a threshold entry.

name
  :Description: Name (e.g. unhealthy). Must be a valid Zenoss object ID.
  :Required: Yes
  :Type: string
  :Default Value: *(implied from key in thresholds map)*

type
  :Description: Type of threshold. See :ref:`Threshold Types <threshold-types>`.
  :Required: No
  :Type: string *(must be a valid threshold type)*
  :Default Value: MinMaxThreshold

enabled
  :Description: Should the threshold be enabled by default?
  :Required: No
  :Type: boolean
  :Default Value: true

dsnames
  :Description: List of *datasource_datapoint* combinations to threshold.
  :Required: No
  :Type: list
  :Default Value: [] *(empty list)*
  :Example: dsnames: ['status_status']

eventClass
  :Description: Value for the *eventClass* field on events generated by the threshold.
  :Required: No
  :Type: string
  :Default Value: /Perf/Snmp -- can vary depending on type.

severity
  :Description: Value for the *severity* field on events generated by the threshold.
  :Required: No
  :Type: int
  :Default Value: 3 *(0=Clear, 1=Debug, 2=Info, 3=Warning, 4=Error, 5=Critical)* -- can vary depending on type.

escalateCount:
  :Description: Event count after which severity increases
  :Required: No
  :Type: int
  :Default Value: None

optional:
  :Description: The threshold will not be created if the threshold type is not available and *optional* is set to true. Installation will fail if the type is not available and *optional* is set to false.
  :Required: No
  :Type: boolean
  :Default Value: False

Thresholds also allow other ad-hoc options to be added not referenced in the
above list. This is because thresholds are an extensible type in Zenoss, and
depending on the value of the threshold's *type*, other fields may be valid.

.. _threshold-types:

Threshold Types
---------------

The following threshold types are valid on any Zenoss system. They are the
default types that are part of the platform. This list is not exhaustive as
additional threshold types can be added by ZenPacks.

MinMaxThreshold:
  :Description: Creates an event if values are below or above specified limits.
  :Availability: Zenoss Platform
  :Additional Fields:
    minval
      :Description: The minimum allowable value. Values below this will raise an event.
      :Required: No
      :Type: string -- Must evaluate to a number. Accepts Python expressions.
      :Default Value: None *(no lower-bound on allowable values)*

    maxval
      :Description: The maximum allowable value. Values above this will raise an event.
      :Required: No
      :Type: string -- Must evaluate to a number. Accepts Python expressions.
      :Default Value: None *(no upper-bound on allowable values)*

ValueChangeThreshold
  :Description: Creates an event if the value is different than last time it was checked. 
  :Availability: Zenoss Platform
  :Additional Fields: None

.. _graph-fields:

Graph Fields
============

The following fields are valid for a graph entry.

name
  :Description: Name (e.g. Health). Must be a valid Zenoss object ID.
  :Required: Yes
  :Type: string
  :Default Value: *(implied from key in graphs map)*

units
  :Description: Units displayed on graph. Used as the y-axis label.
  :Required: No
  :Type: string
  :Default Value: None

miny
  :Description: Value for bottom of y-axis.
  :Required: No
  :Type: integer
  :Default Value: -1 *(-1 causes the minimum y-axis to conform to the plotted data)*

maxy
  :Description: Value for top of y-axis.
  :Required: No
  :Type: integer
  :Default Value: -1 *(-1 causes the maximum y-axis to conform to the plotted data)*

log
  :Description: Should the y-axis be a logarithmic scale?
  :Required: No
  :Type: boolean
  :Default Value: false

base
  :Description: Is the plotted data in base 1024 like storage or memory size?
  :Required: No
  :Type: boolean
  :Default Value: false

hasSummary
  :Description: Should the graph legend be shown?
  :Required: No
  :Type: boolean
  :Default Value: true

height
  :Description: The graph's height in pixels.
  :Required: No
  :Type: integer
  :Default Value: 100

width
  :Description: The graph's width in pixels.
  :Required: No
  :Type: integer
  :Default Value: 500

graphpoints
  :Description: Graphpoints to add to the graph.
  :Required: No
  :Type: map<name, :ref:`Graphpoint <graphpoint-fields>`>
  :Default Value: {} *(empty map)*

comments
  :Description: List of comments to display in the graph's legend.
  :Required: No
  :Type: list<string>
  :Default Value: [] *(empty list)*

.. _graphpoint-fields:

Graphpoint Fields
=================

The following fields are valid for a graphpoint entry.

name
  :Description: Name (e.g. Health). Must be a valid Zenoss object ID.
  :Required: Yes
  :Type: string
  :Default Value: *(implied from key in templates map)*

legend
  :Description: Label to be shown for this graphpoint in the legend. The name field will be used if legend is not set.
  :Required: No
  :Type: string
  :Default Value: None

dpName
  :Description: *datasource_datapoint* combination to plot.
  :Required: Yes
  :Type: string
  :Default Value: None
  :Example: dpName: 'status_status'

lineType
  :Description: How to plot the data: "LINE", "AREA" or "DONTDRAW".
  :Required: No
  :Type: string
  :Default Value: LINE

lineWidth
  :Description: How thick the line should be for the line type.
  :Required: No
  :Type: integer
  :Default Value: 1

stacked
  :Description: Should this graphpoint be stacked (added) to the last? Ideally both area "AREA" types.
  :Required: No
  :Type: boolean
  :Default Value: false

color
  :Description: Color for the line. Specified as RRGGBB (e.g. 1f77b4).
  :Required: No
  :Type: string
  :Default Value: Cycles through a preset list depending on graphpoint's sequence.

colorindex
  :Description: Color index for the line. Can be used instead of color to specify the color sequence number rather than the specific color.
  :Required: No
  :Type: integer
  :Default Value: None

format
  :Description: String format for this graphpoint in the legend (e.g. %7.2lf%s).  The format option follows the `RRDTool PRINT Format <https://oss.oetiker.ch/rrdtool/doc/rrdgraph_graph.en.htm>`_
  :Required: No
  :Type: string
  :Default Value: "%5.2lf%s"

cFunc
  :Description: Consolidation function. One of AVERAGE, MIN, MAX, LAST.
  :Required: No
  :Type: string
  :Default Value: AVERAGE

limit
  :Description: Maximum permitted value. Value larger than this will be nulled. Not used if negative.
  :Required: No
  :Type: integer
  :Default Value: -1

rpn
  :Description: RPN (Reverse Polish Notation) calculation to apply to datapoint. Learn more about `Reverse Polish Notiation <https://en.wikipedia.org/wiki/Reverse_Polish_notation>`_
  :Required: No
  :Type: string
  :Default Value: None

includeThresholds
  :Description: Should thresholds associated with *dpName* be automatically added to the graph?
  :Required: No
  :Type: boolean
  :Default Value: false

thresholdLegends
  :Description: Mapping of threshold id to legend (string) and color (RRGGBB)
  :Required: No
  :Type: map
  :Default Value: None
  :Example: thresholdLegends: {threshold_id: {legend: Legend, color: OO1122}}
