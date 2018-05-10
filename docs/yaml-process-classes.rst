.. _yaml-process-classes:

###############
Process Classes
###############

Process Classes are used to define sets of similar running processes using a regular
expression.  You can then monitor various aspects of the running processes, such as
cpu and memory usage, with a datasource.

To define a class, supply the Process Class Organizer under which the Process Class
will reside.  Optionally add a description of the organizer.  Then, for each Process
Class, supply the processes to include/exclude, description, and replacement text.
You can also optionally override specific zProperties of a process class, such as
zMonitor or zFailSeverity.  See the :ref:`Process Class Fields <process-class-fields>` section below.

The following example shows an example of a `zenpack.yaml` file with an example
of a definition of a process class.

.. code-block:: yaml

    name: ZenPacks.acme.Processes

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

.. note::

  When you define a process class organizer and/or class which already exists, any settings defined in your ZenPack will overwrite existing settings.

Since this is a YAML "mapping", the minmal specification (name only) would look like:

.. code-block:: yaml

    process_class_organizers:
      Widget: {}

.. _process-class-organizer-fields:

******************************
Process Class Organizer Fields
******************************

The following fields are valid for a process class organizer entry.

name
  :Description: Name (e.g. Widget or "Widget/ACME").
  :Required: Yes
  :Type: string
  :Default Value: None

description
  :Description: Description of the process class organizer
  :Required: No
  :Type: string
  :Default Value: None

create
  :Description: Should the process class organizer be created when the ZenPack is installed?
  :Required: No
  :Type: boolean
  :Default Value: true

remove
  :Description: Should the process class organizer be removed when the ZenPack is removed?  This will only apply to a ZenPack that has created the process class organizer.  Any existing process class organizers not created by the ZenPack will not be removed.  Any process class organizer created by the platform will also never be removed.
  :Required: No
  :Type: boolean
  :Default Value: false

reset
  :Description: If true, any zProperties defined here will override those of the target process class organizer, if it exists
  :Required: No
  :Type: boolean
  :Default Value: false

zProperties
  :Description: zProperty values to set on the process class organizer.
  :Required: No
  :Type: map<name, value>
  :Default Value: {} *(empty map)*

.. _process-class-fields:

********************
Process Class Fields
********************

The following fields are valid for a process class entry.

name
  :Description: Name of the process class (e.g. widget).
  :Required: Yes
  :Type: string
  :Default Value: None

description
  :Description: Description of the Process Class Organizer
  :Required: No
  :Type: string
  :Default Value: None

includeRegex
  :Description: Include processes matching this regular expression
  :Required: No
  :Type: string
  :Default Value: Name of the process class

excludeRegex
  :Description: Exclude processes matching this regular expression
  :Required: No
  :Type: string
  :Default Value: None

replaceRegex
  :Description: Replace command line text matching this regular expression
  :Required: No
  :Type: string
  :Default Value: None

replacement
  :Description: Text which will replace the command line text that matches replaceRegex
  :Required: No
  :Type: string
  :Default Value: None

monitor
  :Description: Enable monitoring?  Overrides parent process class organizer setting.
  :Required: No
  :Type: boolean
  :Default Value: None

alert_on_restart
  :Description: Send event on restart?  Overrides parent process class organizer setting. 
  :Required: No
  :Type: boolean
  :Default Value: None

fail_severity
  :Description: 
    Failure event severity.  Overrides parent process class organizer setting.  Valid values:
      * 0=Clear
      * 1=Debug
      * 2=Info
      * 3=Warning
      * 4=Error
      * 5=Critical)
  :Required: No
  :Type: integer
  :Default Value: None

modeler_lock
  :Description:
    Lock process components.  Overrides parent process class organizer setting.  Valid values:
      * 0: Unlocked
      * 1: Lock from Deletes
      * 2: Lock from Updates
  :Required: No
  :Type: integer
  :Default Value: None

send_event_when_blocked
  :Description: Send and event when action is blocked?  Overrides parent class organizer setting.
  :Required: No
  :Type: boolean
  :Default Value: None

