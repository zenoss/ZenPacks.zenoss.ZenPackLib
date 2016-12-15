.. _classes-and-relationships:

#########################
Classes and Relationships
#########################

Classes and relationships form the model that forms the basis for everything
Zenoss does. Classes are things like *Device*, *FileSystem*, *IpInterface* and
*OSProcess*. Relationships state things like a *Device* contains many
*FileSystems*. You will need to extend this model when the standard classes and
relationships don't adequately represent the model of a target your ZenPack is
attempting to monitor. For example, a XenServer ZenPack needs to represent
concepts like pools, storage repositories and virtual machines.


.. _standard-classes:

****************
Standard Classes
****************

The standard classes exist on all Zenoss systems. If these are the only types of
things you care to model and monitor then you may not need to create your own
classes or relationships.

* Device

  * DeviceHW (hw)

    * CPU (hw/cpus)
    * ExpansionCard (hw/cards)
    * Fan (hw/fans)
    * HardDisk (hw/harddisks)
    * PowerSupply (hw/powersupplies)
    * TemperatureSensor (hw/temperaturesensors)

  * OperatingSystem (os)

    * FileSystem (os/filesystems)
    * IpInterface (os/interfaces)
    * IpRouteEntry (os/routes)
    * OSProcess (os/processes)
    * IpService (os/ipservices)
    * WinService (os/winservices)


.. _zenpacklib-classes:

*******
Classes
*******

If you need more than the standard classes provide, you will need to extend one
of the following base classes provided by zenpacklib.

* zenpacklib.Device

* zenpacklib.Component

  * zenpacklib.HWComponent

    * zenpacklib.CPU
    * zenpacklib.ExpansionCard
    * zenpacklib.Fan
    * zenpacklib.HardDisk
    * zenpacklib.PowerSupply
    * zenpacklib.TemperatureSensor

  * zenpacklib.OSComponent

    * zenpacklib.FileSystem
    * zenpacklib.IpInterface
    * zenpacklib.IpRouteEntry
    * zenpacklib.OSProcess

    * zenpacklib.Service

      * zenpacklib.IpService
      * zenpacklib.WinService

You use *zenpacklib.Device* to create new device types of which instances will
appear on the *Infrastructure* screen. You use *zenpacklib.Component* to create
new component types of which instances will appear under *Components* on a
device's left navigation pane. Frequently when ZenPacks need to add new classes,
they will add a single new device type with many new components types. For
example, a XenServer ZenPack would add a new device type called *Endpoint* which
represents the XenAPI management interface. That *Endpoint* device type would
have many components of types such as *Pool*, *StorageRepository* and
*VirtualMachine*.

The other supported classes are proxies for their platform equivalents, and are
to be used when you want to extend one of the platform component types rather
than creating a totally new component type.


.. _zenpacklib-relationships:

*************
Relationships
*************

Relationships are Zenoss' way of saying objects are related to each other. For
example, the *DeviceHW* class contains many CPUs of the *CPU* class. You must
also declare relationships between classes in your ZenPack. If you only declare
types based on *zenpacklib.Device* you don't have to do this because they'll
automatically have a relationship to their containing device class among other
things. However, you must define at least a containing relationship for every
type based on *zenpacklib.Component* you create. This is because components
aren't contained in any relationship by default, and every object in Zenoss must
be contained somewhere.

zenpacklib supports the following types of relationships.

* One-to-Many Containing (1:MC)
* One-to-Many (1:M)
* Many-to-Many (M:M)
* One-to-One (1:1)

It's important to understand the different between containing and non-containing
relationships. Each component type must be contained by exactly one
relationship. Beyond that a device or component type may have as many non-
containing relationships as you like. This is because every object in Zenoss has
a single primary path that describes where it is stored in the tree that is the
Zenoss object database.

A simplified version of XenServer's classes and relationships provides for a
good example. The following list of relationship states the following: An
endpoint contains zero or more pools, each pool contains zero or more storage
repositories and virtual machines, and each storage repository is related to
zero or more virtual machines.

* Endpoint 1:MC Pool
* Pool 1:MC StorageRepository
* Pool 1:MC VirtualMachine
* StorageRepository M:M VirtualMachine


.. _adding-classes-and-relationships:

********************************
Adding Classes and Relationships
********************************

To add classes and relationships to `zenpack.yaml` you add entries to the
top-level *classes* and *class_relationships* fields. The following example
shows a XenServer *Endpoint* device type along with *Pool*, *StorageRepository*,
and *VirtualMachine* component types.

.. code-block:: yaml

    name: ZenPacks.example.XenServer

    classes:
      DEFAULTS:
        base: [zenpacklib.Component]

      XenServerEndpoint:
        base: [zenpacklib.Device]
        label: Endpoint

      XenServerPool:
        label: Pool

        properties:
          ha_enabled:
            type: boolean
            label: HA Enabled
            short_label: HA

          ha_allow_overcommit:
            type: boolean
            label: HA Allow Overcommit
            short_label: Overcommit

      XenServerStorageRepository:
        label: Storage Repository

        properties:
          physical_size:
            type: int
            label: Physical Size
            short_label: Size

      XenServerVirtualMachine:
        label: Virtual Machine

        properties:
          vcpus_at_startup:
            type: int
            label: vCPUs at Startup
            short_label: vCPUs

    class_relationships:
      - XenServerEndpoint 1:MC XenServerPool
      - XenServerPool 1:MC XenServerStorageRepository
      - XenServerPool 1:MC XenServerVirtualMachine
      - XenServerStorageRepository M:M XenServerVirtualMachine

.. note::

  DEFAULTS can be used in classes just like in zProperties to avoid repetitively
  setting the same field for many entries. Note specifically how XenServerPool,
  XenServerStorageRepository and XenServerVirtualMachine will inherit the
  default while XenServerEndpoint overrides it.

Classes and their properties allow for a wide range of control. See the
following section for details.

.. _extending-zenpacklib-classes:

****************************
Extending ZenPackLib Classes
****************************

Occasionally, you may wish to add your own custom methods to your YAML-defined classes 
or otherwise extend their functionality beyond ZenPackLib's current capabilities.  Doing 
so requires creating a Python file that imports and overrides the class you wish to modify,
and this is relatively straightforward.

Suppose we have a component class called "BasicComponent", and we want to provide
a method called "hello world" that, when called, will return the string "Hello World" and
display it in the component grid.

Our YAML file looks like this:

.. code-block:: yaml
      
      name: ZenPacks.zenoss.BasicZenPack
      class_relationships:
      - BasicDevice 1:MC BasicComponent
      classes:
        BasicDevice:
          base: [zenpacklib.Device]
        BasicComponent:
          base: [zenpacklib.Component]
          properties:
            hello_world:
              # this will appear as the column header 
              # in the component grid
              label: Hello World
              # this should be displayed in the component grid
              grid_display: true
              # tells ZenPackLib that this isn't a typical 
              # property like a string, integer, boolean, etc...
              api_only: true
              # this is the type of property
              api_backendtype: method

First, the ZenPack's init file:

.. code-block:: bash
      
      $ZPDIR/ZenPacks.zenoss.BasicZenPack/ZenPacks/zenoss/BasicZenPack/__init__.py

should contain the following lines:

.. code-block:: python
      
      from ZenPacks.zenoss.ZenPackLib import zenpacklib
      CFG = zenpacklib.load_yaml()
      schema = CFG.zenpack_module.schema

Next, we create the file:

.. code-block:: bash
      
      $ZPDIR/ZenPacks.zenoss.BasicZenPack/ZenPacks/zenoss/BasicZenPack/BasicComponent.py
      

and it should contain the lines:

.. code-block:: python
      
      from . import schema
      
      class BasicComponent(schema.BasicComponent):
          """Class override for BasisComponent"""

From here, we proceed to add our "hello_world" method to obtain:

.. code-block:: python
      
      from . import schema
      
      class BasicComponent(schema.BasicComponent):
          """Class override for BasisComponent"""
          def hello_world(self):
              return 'Hello World!'

And we're done.  

The "Hello World" column will now display in the component grid, 
and the string "Hello World!" will be printed in each row of component output.

We can also override ZenPackLib's built-in methods, but must be careful doing so
to avoid undesirable results.  Supposing that our YAML specifies some monitoring templates
(not defined here) for BasicComponent, and for some reason we want to randomly choose 
which ones are displayed in the GUI.  To do so, we need to override the 
"getRRDTemplates" method.

Our YAML file is modified:

.. code-block:: yaml
      
      name: ZenPacks.zenoss.BasicZenPack
      class_relationships:
      - BasicDevice 1:MC BasicComponent
      classes:
        BasicDevice:
          base: [zenpacklib.Device]
        BasicComponent:
          base: [zenpacklib.Component]
          properties:
            hello_world:
              label: Hello World
              api_only: true
              api_backendtype: method
              grid_display: true
          monitoring_templates: [ThisTemplate, ThatTemplate]

And we further modify our BaseComponent.py as follows:

.. code-block:: python
      
      import random
      from . import schema
      
      class BasicComponent(schema.BasicComponent):
          """Class override for BasisComponent"""
          def hello_world(self):
              return 'Hello World!'
      
          def getRRDTemplates(self):
              """ Safely override the ZenPackLib 
                  getRRDTemplates method, returning 
                  randomly chosen templates. """
              templates = []
              # make sure we call the base method when we override it
              for template in super(BasicComponent, self).getRRDTemplates():
                  # rolling the dice
                  if bool(random.randint(0,1)):
                      templates.append(template)
              return templates

The key point to remember here is the call to:

.. code-block:: python
      
      super(BasicComponent, self).getRRDTemplates()

which instructs Python to use the original method before we modify its output.  Similar care 
must be excercised when overriding built-in methods and properties, assuming a safer method
cannot be found.


.. _class-multi-file:

*********************************************
Support for multiple YAML files (Version 2.0)
*********************************************

For particularly complex ZenPacks the YAML file can grow to be quite large, potentially making 
management cumbersome.  To address this concern, ZenPackLib now supports splitting the zenpack.yaml
files into multiple files.  The following conditions should be observed when using multiple files:

* The YAML files should have a .yaml extension.

* The "load_yaml" method will detect and load yaml files automatically. This behavior can be overridden by calling load_yaml(yaml_doc=[doc1, doc2]).  In this case the full file paths will need to be specified: 

.. code-block:: python

      import os
      files = ['file1.yaml', 'file2.yaml']
      YAML_DOCS = [os.path.join(os.path.dirname(__file__), f) for f in files]
      from ZenPacks.zenoss.ZenPackLib import zenpacklib
      CFG = zenpacklib.load_yaml(yaml_doc=YAML_DOCS)
      schema = CFG.zenpack_module.schema


* The 'name' parameter (ZenPack name), if used in multiple files, should be identical between them

* If a given YAML section (device_classes, classes, device_classes, etc) is split between files, then each file should give the complete path to the defined objects.  The following is valid:

.. code-block:: yaml

      # File 1
      name: ZenPacks.zenoss.BasicZenPack
      class_relationships:
      - BaseComponent 1:MC AuxComponent
      classes:
        BasicDevice:
          base: [zenpacklib.Device]
          monitoring_templates: [BasicDevice]
        BasicComponent:
          base: [zenpacklib.Component]
          monitoring_templates: [BasicComponent]

.. code-block:: yaml

      # File 2
      class_relationships:
      - BaseDevice 1:MC BaseComponent
      classes:
        SubComponent:
          base: [BasicComponent]
          monitoring_templates: [SubComponent]
        AuxComponent:
          base: [SubComponent]
          monitoring_templates: [AuxComponent]

* Using conflicting parameters (like setting different DEFAULTS for the same entity in different files) will likely lead to undesirable results.


.. _class-fields:

************
Class Fields
************

The following fields are valid for a class entry.

name
  :Description: Name (e.g. XenServerEndpoint). Must be a valid Python class name.
  :Required: Yes
  :Type: string
  :Default Value: *(implied from key in classes map)*

base
  :Description: List of base classes to extend. See :ref:`Classes <zenpacklib-classes>`
  :Required: No
  :Type: list<classname>
  :Default Value: [zenpacklib.Component]

.. todo:: Better explanation of Class.base field.

meta_type
  :Description: Globally unique name for the class.
  :Required: No
  :Type: string
  :Default Value: *(same as name)*
  
label
  :Description: Human-friendly label for the class.
  :Required: No
  :Type: string
  :Default Value: *(same as meta_type)*
  
plural_label
  :Description: Plural form of label.
  :Required: No
  :Type: string
  :Default Value: *(same as label with an "s" suffix)*
  
short_label
  :Description: Short form of label. Used as a column header or where space is limited.
  :Required: No
  :Type: string
  :Default Value: *(same as label)*
  
plural_short_label
  :Description: Plural form of short_label.
  :Required: No
  :Type: string
  :Default Value: *(same as short_label with an "s" suffix)*
  
icon
  :Description: Filename (in resources/) for icon.
  :Required: No
  :Type: string
  :Default Value: *(same as name with a ".png" suffix in resources/icon/)*
  
label_width
  :Description: Width of label text in pixels.
  :Required: No
  :Type: integer
  :Default Value: 80
  
plural_label_width
  :Description: Width of plural_label text in pixels.
  :Required: No
  :Type: integer
  :Default Value: *(same as label_width + 7)*
  
content_width
  :Description: Expected width of object's title in pixels.
  :Required: No
  :Type: integer
  :Default Value: *(same as label_width)*
  
auto_expand_column
  :Description: Column (property) to auto-expand in component grid.
  :Required: No
  :Type: string
  :Default Value: name
  
initial_sort_column
  :Description: Column (property) to initially sort in component grid.
  :Required: No
  :Type: string
  :Default Value: name

order
  :Description: Order to display this class among other classes. (0-100)
  :Required: No
  :Type: integer
  :Default Value: 50
  
filter_display
  :Description: Will related components be filterable by components of this type?
  :Required: No
  :Type: boolean
  :Default Value: true

filter_hide_from
  :Description: Classes for which this class should not show in the filter dropdown.
  :Required: No
  :Type: list<classname>
  :Default Value: [] *(empty list)*

monitoring_templates
  :Description: List of monitoring template names to bind to components of this type.
  :Required: No
  :Type: list<string>
  :Default Value: [*(label with spaces removed)*]
  
properties
  :Description: Properties for this class.
  :Required: No
  :Type: map<name, :ref:`Class Property <class-property-fields>`>
  :Default Value: {} *(empty map)*
  
relationships
  :Description: Relationship overrides for this class.
  :Required: No
  :Type: map<name, :ref:`Relationship Override <relationship-override-fields>`>
  :Default Value: {} *(empty map)*
  
impacts
  :Description: Relationship or method names that when called return a list of objects that objects of this class could impact.
  :Required: No
  :Type: list<*relationship_or_method_name*>
  :Default Value: [] *(empty list)*
  
impacted_by
  :Description: Relationship or method names that when called return a list of objects that could impact objects of this class.
  :Required: No
  :Type: list<*relationship_or_method_name*>
  :Default Value: [] *(empty list)*
 
impact_triggers
  :Description: Impact trigger policy definitions for this class.
  :Required: No
  :Type: map<name, :ref:`Impact Trigger <impact-trigger-fields>`>
  :Default Value: {} *(empty map)*
 
dynamicview_views
  :Description: Names of Dynamic Views objects of this class can appear in.
  :Required: No
  :Type: list<*dynamicview_view_name*>
  :Default Value: [service_view]
  
dynamicview_group
  :Description: Dynamic View group name for objects of this class. Can be overridden by implementing getDynamicViewGroup() method on class.
  :Required: No
  :Type: string
  :Default Value: *(same as plural_short_label)*

dynamicview_weight
  :Description: Dynamic View weight for objects of this class. Higher numbers are further to the right. Can be overridden by implementing getDynamicViewGroup() method on class.
  :Required: No
  :Type: float or int
  :Default: 1000 + (order * 100)
  
dynamicview_relations
  :Description: Map of Dynamic View relationships for this class and the relationship or method names that when called populate them.
  :Required: No
  :Type: map<relationship_name, list<*relationship_or_method_name*>>
  :Default Value: {} *(empty map)*

extra_paths
  :Description: By default, components are indexed based upon paths that include objects they have a direct relationship to.  This option allows additional paths to be specified (this can be useful when indirect containment is used)
  :Required: No
  :Type: list<list<regexp>>
  :Default Value: [] *(empty list)*
  :Example 1: ['resourcePool', 'owner'] # from cluster or standalone
  :Example 2: ['resourcePool', '(parentResourcePool)+'] # from all parent resource pools, recursively.

.. note::

      Each item in extra_paths is expressed as a tuple of
      regular expression patterns that are matched
      in order against the actual relationship path structure
      as it is traversed and built up get_facets.
      
      To facilitate matching, we construct a compiled set of
      regular expressions that can be matched against the
      entire path string, from root to leaf.
      
      So:
        
        ('orgComponent', '(parentOrg)+')
        
      is transformed into a "pattern stream", which is a list
      of regexps that can be applied incrementally as we traverse
      the possible paths:
      
        (
        re.compile(^orgComponent), 
        re.compile(^orgComponent/(parentOrg)+), 
        re.compile(^orgComponent/(parentOrg)+/?$' 
        )
      
      Once traversal embarks upon a stream, these patterns are
      matched in order as the traversal proceeds, with the
      first one to fail causing recursion to stop.
      When the final one is matched, then the objects on that
      relation are matched.  Note that the final one may
      match multiple times if recursive relationships are
      in play.

.. todo:: Add section on Impact & DynamicView.

.. todo:: Add more detailed explanation of extra_paths, based on comments in zenpacklib.py

.. _class-property-fields:

*********************
Class Property Fields
*********************

The following fields are valid for a class property entry.

name
  :Description: Name (e.g. ha_enabled). Must be a valid Python variable name.
  :Required: Yes
  :Type: string
  :Default Value: *(implied from key in properties map)*
  
type
  :Description: Type of property: *string*, *int*, *float*, *boolean*, *lines*, *password* or *entity*.  All types are strictly enforced except for *entity*.
  :Required: No
  :Type: string
  :Default Value: string
  
default
  :Description: Default value for property.
  :Required: No
  :Type: *(varies depending on type)*
  :Default Value: None
  
label
  :Description: Human-friendly label for the property.
  :Required: No
  :Type: string
  :Default Value: *(same as name)*
  
short_label
  :Description: Short form of label. Used as a column header where space is limited.
  :Required: No
  :Type: string
  :Default Value: *(same as label)*
  
label_width
  :Description: Width of label text in pixels.
  :Required: No
  :Type: integer
  :Default Value: 80
  
content_width
  :Description: Expected width of property's value in pixels.
  :Required: No
  :Type: integer
  :Default Value: *(same as label_width)*
  
display
  :Description: Should this property be shown as a column and in details?
  :Required: No
  :Type: boolean
  :Default Value: true
  
details_display
  :Description: Should this property be shown in details?
  :Required: No
  :Type: boolean
  :Default Value: true
  
grid_display
  :Description: Should this property be shown as a column?
  :Required: No
  :Type: boolean
  :Default Value: true
  
order
  :Description: Order to display this property among other properties. (0-100)
  :Required: No
  :Type: integer
  :Default Value: 45

group
  :Description: Name of group in details.
  :Required: No
  :Type: string
  :Default Value: None
  
editable
  :Description: Should this property be editable in details?
  :Required: No
  :Type: boolean
  :Default Value: false
  
renderer
  :Description: JavaScript renderer for property value.
  :Required: No
  :Type: string
  :Default Value: None *(renders value as-is)*
  
api_only
  :Description: Should this property be for the API only? The property or method (according to api_backendtype) must be manually implemented if this is set to true.
  :Required: No
  :Type: boolean
  :Default Value: false
  
api_backendtype
  :Description: Implementation style for the property if *api_only* is true. Must be *property* or *method*.
  :Required: No
  :Type: string
  :Default Value: property
  
enum
  :Description: Enumeration map for property. Set to something like {1: 'OK', 2: 'ERROR'} for an int-type property to provide text representations for property values.
  :Required: No
  :Type: map<value, representation>
  :Default Value: {} *(empty map)*
  
datapoint
  :Description: *datasource_datapoint* value to use as the value for this property. Useful for displaying the most recent collected datapoint value in the grid or details as any modeled property would be.
  :Required: No
  :Type: string
  :Default Value: None
  
datapoint_default
  :Description: Default value for property if *datapoint* is set, but no data exists.
  :Required: No
  :Type: string, integer or float
  :Default Value: None
  
datapoint_cached
  :Description: Should the value for datapoint be cached for a limited time? Can improve UI performance.
  :Required: No
  :Type: boolean
  :Default Value: true
  
index_type
  :Description: Type of indexing for the property: *field* or *keyword*.
  :Required: No
  :Type: string
  :Default Value: None *(no indexing)*

index_scope
  :Description: Scope of index: *device* or *global*. Only applies if *index_type* is set.
  :Required: No
  :Type: string
  :Default Value: device

.. todo:: Section on indexing.


.. _relationship-override-fields:

****************************
Relationship Override Fields
****************************

The following fields are valid for a relationship override entry.

name
  :Description: Name (e.g. xenServerPools). Must match a relationship name defined in *class_relationships*.
  :Required: Yes
  :Type: string
  :Default Value: *(implied from key in relationships map)*
  
label
  :Description: Human-friendly label for the relationship.
  :Required: No
  :Type: string
  :Default Value: *(label of class to which the relationship refers)*
  
short_label
  :Description: Short form of label. Used as a column header where space is limited.
  :Required: No
  :Type: string
  :Default Value: *(same as label or referred class' short_label)*
  
label_width
  :Description: Width of label text in pixels.
  :Required: No
  :Type: integer
  :Default Value: *(same as referred class' label width)*
  
content_width
  :Description: Expected width of relationship's value in pixels. To-Many relationships are shown simply as a count and will have a shorter width. To-One relationships show a link to the object and will require a width long enough to accommodate the object's title.
  :Required: No
  :Type: integer
  :Default Value: *(varies depending on relationship type)*
  
display
  :Description: Should this relationship be shown as a column and in details?
  :Required: No
  :Type: boolean
  :Default Value: true
  
details_display
  :Description: Should this relationship be shown in details?
  :Required: No
  :Type: boolean
  :Default Value: true
  
grid_display
  :Description: Should this relationship be shown as a column?
  :Required: No
  :Type: boolean
  :Default Value: true
  
order
  :Description: Order to display this relationship among other relationships and properties. (0-10)
  :Required: No
  :Type: float
  :Default Value: 3.0 for To-One, 6.0 for To-Many.
  
renderer
  :Description: JavaScript renderer for relationship value.
  :Required: No
  :Type: string
  :Default Value: None
  
render_with_type
  :Description: Should related object be rendered with it's type? Only applies to To-One relationships.
  :Required: No
  :Type: boolean
  :Default Value: false


.. _impact-trigger-fields:

*********************
Impact Trigger Fields
*********************

The following fields are valid for an Impact trigger entry.

name
  :Description: Name (e.g. avail_pct_5). Must be a valid Python variable name.
  :Required: Yes
  :Type: string
  :Default Value: *(implied from key in properties map)*
  
policy
  :Description: Type of policy, one of: AVAILABILITY, PERFORMANCE, CAPACITY
  :Required: Yes
  :Type: string
  :Default Value: AVAILABILITY
  
trigger:
  :Description: Type of trigger, one of: policyPercentageTrigger, policyThresholdTrigger, or negativeThresholdTrigger
  :Required: Yes
  :Type: string
  :Default Value: policyPercentageTrigger
  
threshold:
  :Description: Numerical boundary for the trigger
  :Required: Yes
  :Type: int
  :Default Value: 50
  
state:
  :Description: State of this object when trigger criteria met (see note)
  :Required: Yes
  :Type: str
  :Default Value: UNKNOWN
  
dependent_state:
  :Description: State of dependent objects meeting trigger criteria (see note)
  :Required: Yes
  :Type: str
  :Default Value: UNKNOWN

.. note::
  
  Valid values for both **state** and **dependent_state** depend on the choice of
  **policy** parameter:
  
  * **AVAILABILITY**:  DOWN, UP, DEGRADED, ATRISK, or UNKNOWN
  * **PERFORMANCE**:  UNACCEPTABLE, DEGRADED, ACCEPTABLE, or UNKNOWN
  * **CAPACITY**:  UNACCEPTABLE, REDUCED, ACCEPTABLE, or UNKNOWN

