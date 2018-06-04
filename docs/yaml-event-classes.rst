.. _yaml-event-classes:

#############
Event Classes
#############

Event Classes are used to group together specific types of events.  This can be useful for situations where an event should be dropped or text should be altered to be more human readable.  This is typically done through a python transform.

To define a class, supply the path to the class or classes.  Then, for each event class, supply the appropriate properties for the class.  These include the option to remove the event class during ZenPack installation/uninstallation, description, and a transform.  You can also define mappings to apply to events based on a key and supply an explanation and/or resolution to an issue.


.. note::

     When you define an event class and/or mapping which already exists, any settings defined in your ZenPack 
     will overwrite existing settings.


The following example shows an example of a `zenpack.yaml` file with an example of a definition of an event class.

.. code-block:: yaml

    name: ZenPacks.acme.Events

    event_classes:
      /Status/Acme:
        remove: false
        description: Acme event class
        mappings:
          Widget:
            eventClassKey: WidgetEvent
            sequence:  10
            remove: true
            transform: |-
              if evt.message.find('Error reading value for') >= 0:
                  evt._action = 'drop'

.. note::

     When assigning values to multi-line fields such as **transform** or **example**, the best way to preserve whitespace 
     and readability is to use the 
     
     **transform: \|-**
       **if evt.message.find('Error reading value for') >= 0:**
           **evt._action = 'drop'**
     
     style convention demonstrated.  As this example demonstrates, the indented line following
     the **"\|-"** style character becomes the first line of the transform, with subsequent whitespace preserved.

Since this is a YAML "mapping", the minmal specification (name only) would look like:

.. code-block:: yaml

    event_classes:
      /Status/Acme: {}

.. _event-class-fields:

******************
Event Class Fields
******************

The following fields are valid for an event class entry.

path
  :Description: Path to the Event Class (e.g. /Status/Acme).  Must begin with "/".
  :Required: Yes
  :Type: string
  :Default Value: None

description
  :Description: Description of the event class
  :Required: No
  :Type: string
  :Default Value: None

create
  :Description: Should the event class be created when the ZenPack is installed?
  :Required: No
  :Type: boolean
  :Default Value: true

remove
  :Description: Should the event class be removed when the ZenPack is removed?  This will only apply to a ZenPack that has created the event class.  Any existing event classes not created by the ZenPack will not be removed.  Any event classes created by the platform will also never be removed.
  :Required: No
  :Type: boolean
  :Default Value: false

reset
  :Description: If true, any zProperties defined here will override those of the target event class, if it exists
  :Required: No
  :Type: boolean
  :Default Value: false

zProperties
  :Description: zProperty values to set on the event class.
  :Required: No
  :Type: map<name, value>
  :Default Value: {} *(empty map)*

transform
  :Description: A python expression for transformation.
  :Required: No
  :Type: string (multiline)
  :Default Value: None

mappings
  :Description: Event class mappings
  :Required: No
  :Type: map<name, :ref:`Event Class Mapping <event-class-mapping-fields>`>
  :Default Value: None

.. _event-class-mapping-fields:

**************************
Event Class Mapping Fields
**************************

The following fields are valid for an event class mapping entry.

name
  :Description: Name of the event class mapping (e.g. WidgetDown).
  :Required: Yes
  :Type: string
  :Default Value: None

zProperties
  :Description: zProperty values to set on the event class mapping.
  :Required: No
  :Type: map<name, value>
  :Default Value: {} *(empty map)*

eventClassKey
  :Description: Event class key
  :Required: No
  :Type: string
  :Default Value: None

explanation
  :Description:
    Textual description for matches of this event class mapping. Use in conjunction with the Resolution field.
  :Required: No
  :Type: string (multiline)
  :Default Value: None

resolution
  :Description: Use the Resolution field to enter resolution instructions for clearing the event.
  :Required: No
  :Type: string (multiline)
  :Default Value: None

sequence
  :Description: Define the match priority. Lower is a higher priority.
  :Required: No
  :Type: integer
  :Default Value: None

rule
  :Description: A python expression to match an event.
  :Required: No
  :Type: string
  :Default Value: None

regex
  :Description: A regular expression to match an event.
  :Required: No
  :Type: string
  :Default Value: None

transform
  :Description: A python expression for transformation.
  :Required: No
  :Type: string (multiline)
  :Default Value: None

example
  :Description: Debugging string to use in the regular expression ui testing.
  :Required: No
  :Type: string (multiline)
  :Default Value: None

remove
  :Description: Remove the Mapping when the ZenPack is removed.
  :Required: No
  :Type: boolean
  :Default Value: None
