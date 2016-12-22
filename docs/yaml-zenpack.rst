.. _zenpack:

#######
ZenPack
#######

The ZenPack YAML file, `zenpack.yaml`, contains the specification for a
ZenPack. It must at at least contain a `name` field. It may optionally contain
one each of `zProperties`, `device_classes`, `classes`, and
`class_relationships` fields.

The following example shows an example of a `zenpack.yaml` file with examples
of every supported field.

.. code-block:: yaml

    name: ZenPacks.acme.Widgeter

    zProperties:
      zWidgeterEnable: {}

    device_classes:
      /Server/ACME/Widgeter: {}

    classes:
      ACMEWidgeter:
        base: [zenpacklib.Device]

      ACMEWidget:
        base: [zenpacklib.Component]

    class_relationships:
      - Widgeter 1:MC Widget
      
   link_providers:
     Virtual Machine:
       link_class: ZenPacks.example.XenServer
       catalog: device
       device_class: /Server/XenServer
       queries: [vm_id:manageIp]
     XenServer:
       global_search: True
       queries: [manageIp:vm_id]
       
   event_classes:
     /Status/Acme:
       remove: false
       description: Acme event class
       mappings:
         Widget:
           eventClassKey: WidgetEvent
           sequence:  10
           remove: true
           transform: "if evt.message.find('Error reading value for') >= 0:\n\
             \   evt._action = 'drop'"
             
   process_class_organizers:
     Widget:
       description: Organizer for Widget process classes
       process_classes:
         widget:
           description: Widget process class
           includeRegex: sbin\/widget
           excludeRegex: "\\b(vim|tail|grep|tar|cat|bash)\\b"
           replaceRegex: .*
           replacement: Widget
           
           
See the following for more information on each of these fields.

* :ref:`zProperties`
* :ref:`device-classes`
* :ref:`classes-and-relationships`
* :ref:`device-link-providers`
* :ref:`yaml-event-classes`
* :ref:`yaml-process-classes`


.. _zenpack-fields:

**************
ZenPack Fields
**************

The following fields are valid for a ZenPack entry.

name
  :Description: Name (e.g. ZenPacks.acme.Widgeter). Must begin with "ZenPacks.".
  :Required: Yes
  :Type: string
  :Default Value: None

.. todo:: Better explain zenpack.name syntax.

zProperties
  :Description: zProperties added by the ZenPack
  :Required: No
  :Type: map<name, :ref:`zProperty <zProperty-fields>`>
  :Default Value: {} *(empty map)*

device_classes
  :Description: Device classes added by the ZenPack.
  :Required: No
  :Type: map<path, :ref:`Device Class <device-class-fields>`>
  :Default Value: {} *(empty map)*

classes
  :Description: Classes for device and component types added by this ZenPack.
  :Required: No
  :Type: map<name, :ref:`Class <class-fields>`>
  :Default Value: {} *(empty map)*

class_relationships
  :Description: Relationships between classes.
  :Required: No
  :Type: list<:ref:`Class Relationship <zenpacklib-relationships>`>
  :Default Value: [] *(empty list)*

link_providers
  :Description: Device Link Providers.
  :Required: No
  :Type: list<:ref:`Link Provider <device-link-provider-fields>`>
  :Default Value: [] *(empty list)*
  
event_classes
  :Description: Event Class organizers and mappings
  :Required: No
  :Type: list<:ref:`Event Class <event-class-fields>`>
  :Default Value: [] *(empty list)*
  
process_class_organizers
  :Description: Process Class organizers and mappings
  :Required: No
  :Type: list<:ref:`Process Class <process-class-organizer-fields>`>
  :Default Value: [] *(empty list)*
  