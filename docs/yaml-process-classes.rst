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
zMonitor or zFailSeverity.  See the :ref:`_process-class-fields` section below.

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
  :Description: Description of the Process Class Organizer
  :Required: No
  :Type: string
  :Default Value: None

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

