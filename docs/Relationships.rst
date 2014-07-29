==============================================================================
Relationship Management in the ZPL
==============================================================================

Within the context of Zenoss, a relationship establishes a connection between
Zope objects. A relationship MUST be bi-directional: a left side object and a
right side object. However, if one side is containing, then the other side is
contained.

Currently ZenPacks supports three types of relationships:

* ToMany
* ToOne
* ToManyCont

Read zenosslabs section Background Information for an explanation of Relationship,
and what is meant to be 'containing'. Here is the webpage link:
http://docs.zenosslabs.com/en/latest/zenpack_development/background.html#relationship-types

The Relationship classes are defined in /opt/zenoss/Products/ZenRelations/RelSchema.py.
A relationship is expressed via a yUML statement in ZenPack's __init__.py.

* For a left side to be ToManyCont, there must be ‘++’ on the left.
* For a right side to be ToManyCont, there must be ‘++’ on the right.

* For a left side to be ToMany, there must be ‘*’ on the right.
* For a right side to be ToMany, there must be ‘*’ on the left.

* If there is no ‘++’ on the left AND no ‘*’ on the right, the left is ToOne.
* If there is no ‘++’ on the right AND no ‘*’ on the left, the right is ToOne.

* You can specify a number for a fixed quantify for a non-containing
* You can also specify a numerical range (0..2) on ends of non-containing 
  relationships.

Example 1:
-----------------------------------------------------------------

:: 

    [Image]1-.-*[Instance]

Here Image and Instance are class names.
This yUML statement says an Image object can have many Instance objects;
whereas an Instance object can only have one Image object.
An Image object has a ToMany relationship w.r.t Instance objects;
whereas an Instance object a ToOne relationship w.r.t. Image object.
The relationship between Image and Instance is non-containing.

'-' and/or '.' separates left side from right side.


Example 2:
------------------------------------------------------------------

[Endpoint]++components-endpoint1[OpenstackComponent]

* Endpoint and OpenstackComponent are again class names.
  components and endpoint here are relationship names. As pointed out in
  zenosslabs, relationships are themselves objects.

* This yUML statement says Endpoint can contain multiple OpenstackComponent(s);
  whereas an OpenstackComponent can only belong to one Endpoint.

* Endpoint has a containing ToMany relationship w.r.t.
  OpenstackComponent; whereas OpenstackComponent has a contained ToOne
  relationship w.r.t. Endpoint.
* The relationship between Endpoint and OpenstackComponent is containing.

zendmd can be used to find the relationship object components::

   >>> dev=find('stack')
   >>> dev.components
   <ToManyContRelationship at /zport/dmd/Devices/OpenStack/devices/stack/components>

Example 3:
---------------------------------------------------------------------

::

    [Hypervisor]1-.-1[Host]

* Hypervisor and Host has a mutual ToOne non-containing relationship.
* Hypervisor and Host are class names.
* The relationship between Hypervisor and Host is non-containing.

For those who went through the SNMP ZenPack Development guide,
http://docs.zenosslabs.com/en/latest/zenpack_development/index.html,
just as a comparison, the relation expressed in NetBotzDevice.py::

    _relations = Device._relations + (
        ('temperature_sensors', ToManyCont(ToOne,
            'ZenPacks.training.NetBotz.TemperatureSensor',
            'sensor_device',
            )),
        )

and in TemperatureSensor.py::

    _relations = ManagedEntity._relations + (
        ('sensor_device', ToOne(ToManyCont,
            'ZenPacks.training.NetBotz.NetBotzDevice',
            'temperature_sensors',
            )),
        )

is equivalent to::

    [NetBotzDevice]++temperature_sensors-.-sensor_device1[TemperatureSensor]

Example 4:
---------------------------------------------------------------------

::

    [EtherCard]0..1 switches -.-ecards 0..1 [Switch]

* The endpoint relationships are now named
* Named relationships can have their properties changes (GUI, order, etc)
* Each side can handle 0 or 1 connections


TODO: Examples of illegal yUML statements.
------------------------------------------

