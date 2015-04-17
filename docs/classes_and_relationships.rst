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
    * Software (os/software)


.. _zenpacklib-classes:

*******
Classes
*******

If you need more than the standard classes provide, you will need to extend one
of the following two base classes provided by zenpacklib.

* zenpacklib.Device
* zenpacklib.Component

You use *zenpacklib.Device* to create new device types of which instances will
appear on the *Infrastructure* screen. You use *zenpacklib.Component* to create
new component types of which instances will appear under *Components* on a
device's left navigation pane. Frequently when ZenPacks need to add new classes,
they will add a single new device type with many new components types. For
example, a XenServer ZenPack would add a new device type called *Endpoint* which
represents the XenAPI management interface. That *Endpoint* device type would
have many components of types such as *Pool*, *StorageRepository* and
*VirtualMachine*.


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


.. _class-reference:

***************
Class Reference
***************

The following fields are valid for a class entry.

name
  :Description: Name (e.g. XenServerEndpoint). Must be a valid Python class name.
  :Required: Yes
  :Type: string
  :Default Value: *(implied from key in classes map)*

base
  :Description: List of base classes to extend.
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
  :Default Value: *(same as name with a ".png" suffix)*
  
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
  :Type: map<name, :ref:`Class Property <class-property-reference>`>
  :Default Value: {} *(empty map)*
  
relationships
  :Description: Relationship overrides for this class.
  :Required: No
  :Type: map<name, :ref:`Relationship Override <relationship-override-reference>`>
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
  
dynamicview_views
  :Description: Names of Dynamic Views objects of this class can appear in.
  :Required: No
  :Type: list<*dynamicview_view_name*>
  :Default Value: [] *(empty list)*
  
dynamicview_groups
  :Description: Dynamic View group name for objects of this class.
  :Required: No
  :Type: string
  :Default Value: *(same as plural_short_label)*
  
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

.. todo:: Add section on Impact & DynamicView.

.. todo:: Add more detailed explanation of extra_paths, based on comments in zenpacklib.py

.. _class-property-reference:

************************
Class Property Reference
************************

The following fields are valid for a class property entry.

name
  :Description: Name (e.g. ha_enabled). Must be a valid Python variable name.
  :Required: Yes
  :Type: string
  :Default Value: *(implied from key in properties map)*
  
type
  :Description: Type of property: *string*, *int*, *float*, *boolean*, *lines*, *password* or *entity*.
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


.. _relationship-override-reference:

*******************************
Relationship Override Reference
*******************************

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
