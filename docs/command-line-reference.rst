.. _command-line-reference:

######################
Command Line Reference
######################

While most of zenpacklib's functionality is as a Python module to be used as a
library for helping build ZenPacks, `zenpacklib` also acts as a command line
script to perform some useful actions.

The `zenpacklib` script can be run from the command line with: 

.. code-block:: bash

   `$ZENHOME/bin/zenpacklib` (usually `/opt/zenoss/bin/zenpacklib`)


Running the command alone or with `--help` will return the following (truncated):

.. code-block:: text

   Usage: zenpacklib.py [options] [FILENAME|ZENPACK|DEVICE]
   
   ZenPack Conversion:
    -t, --dump-templates
                        export existing monitoring templates to YAML
    -e, --dump-event-classes
                        export existing event classes to YAML
    -r, --dump-process-classes
                        export existing process classes to YAML
   
   ZenPack Development:
    -c, --create        Create a new ZenPack source directory
    -l, --lint          check zenpack.yaml syntax for errors
    -o, --optimize      optimize zenpack.yaml format and DEFAULTS
    -d, --diagram       print YUML (http://yuml.me/) class diagram source
                        based on zenpack.yaml
    -p, --paths         print possible facet paths for a given device and
                        whether currently filtered.


The following commands are supported:

* :ref:`-c, --create <zenpacklib-create>`: Create a new zenpacklib-enabled ZenPack source directory.
* :ref:`-l, --lint <zenpacklib-lint>`: Provides syntax and correctness on a YAML file.
* :ref:`-d, --diagram <zenpacklib-class_diagram>`: Export yUML (yuml.me) class diagram from a YAML file.
* :ref:`-t, --dump-templates <zenpacklib-dump_templates>`: Export existing monitoring templates to YAML.
* :ref:`-e, --dump-event-classes <zenpacklib-dump_event_classes>`: Export existing event classes and mappings to YAML.
* :ref:`-r, --dump-process-classes <zenpacklib-dump_process_classes>`: Export existing process classes to YAML.
* :ref:`-p, --paths <zenpacklib-list_paths>`: Using the specified device, print a report of paths between objects.
* :ref:`-o, --optimize <zenpacklib-optimize>`: Optimize the layout of an existing zenpack.yaml file
* :ref:`--version <zenpacklib-version>`: Print zenpacklib version.


.. _zenpacklib-create:

******
create
******

The *--create* command will create a source directory for a zenpacklib-enabled
ZenPack. This will include a setup.py, MANIFEST.in, the namespace and module
directories, and a zenpack.yaml in the module directory. It will also make a
copy of zenpacklib.py inside the module directory. This ZenPack will be ready to
be installed immediately though it will contain no functionality yet.

Example usage:

.. code-block:: bash

    zenpacklib --create ZenPacks.example.MyNewPack

Running the above command would result in the following output.

.. code-block:: text

    Creating source directory for ZenPacks.test.ZPLTest2:
      - making directory: ZenPacks.test.ZPLTest2/ZenPacks/test/ZPLTest2
      - creating file: ZenPacks.test.ZPLTest2/setup.py
      - creating file: ZenPacks.test.ZPLTest2/MAINFEST.in
      - creating file: ZenPacks.test.ZPLTest2/ZenPacks/__init__.py
      - creating file: ZenPacks.test.ZPLTest2/ZenPacks/test/__init__.py
      - creating file: ZenPacks.test.ZPLTest2/ZenPacks/test/ZPLTest2/__init__.py
      - creating file: ZenPacks.test.ZPLTest2/ZenPacks/test/ZPLTest2/zenpack.yaml


.. _zenpacklib-lint:

****
lint
****

The *--lint* command will check the provided YAML file for correctness. It checks
that the provided file is syntactically-valid YAML, and it will also perform
many others checks that validate that the contained entries, fields and their
values are valid.

The following example shows an example of using an unrecognized parameter in a
monitoring template.

.. code-block:: bash

    zenpacklib --lint zenpack.yaml
    zenpack.yaml:47:9: Unrecognized parameter 'targetPythnoClass' found while processing RRDTemplateSpec

.. note:: *lint* will provide no output if the provided YAML file is found to be correct.


.. _zenpacklib-class_diagram:

*************
class_diagram
*************

The *--diagram* command will use :ref:`classes-and-relationships` in the
provided YAML file to output the source for a yUML (http://yuml.me) class
diagram. For ZenPacks with a non-trivial class model this can provide a useful
view of the model.

Using this example `zenpack.yaml` with class_diagram..

.. code-block:: yaml

    name: ZenPacks.example.NetBotz

    classes:
      NetBotzDevice:
        base: [zenpacklib.Device]

      NetBotzEnclosure:
        base: [zenpacklib.Component]

      NetBotzSensor:
        base: [zenpacklib.Component]

    class_relationships:
      - NetBotzDevice 1:MC NetBotzEnclosure
      - NetBotzDevice 1:MC NetBotzSensor
      - NetBotzEnclosure 1:M NetBotzSensor

Then running the following command..

.. code-block:: bash

    zenpacklib --diagram zenpack.yaml

Would result in the following yUML class diagram source. You can now paste this
into http://yuml.me to see what it looks like.

.. code-block:: text

    # Classes
    [NetBotzDevice]
    [NetBotzEnclosure]
    [NetBotzSensor]

    # Inheritence
    [Device]^-[NetBotzDevice]
    [Component]^-[NetBotzEnclosure]
    [Component]^-[NetBotzSensor]

    # Containing Relationships
    [NetBotzDevice]++netBotzEnclosures-netBotzDevice[NetBotzEnclosure]
    [NetBotzDevice]++netBotzSensors-netBotzDevice[NetBotzSensor]

    # Non-Containing Relationships
    [NetBotzEnclosure]netBotzSensors-.-netBotzEnclosure++[NetBotzSensor]


.. _zenpacklib-list_paths:

**********
list_paths
**********

The *--paths* command shows the paths between defined component classes
in the zenpack, using the device name you have specified as a sample.  To
obtain useful results, ensure that the device has at least one component
of each type you are interested in.

The paths shown are those used to control which devices will show up in the
bottom grid of the zenoss UI when a component is selected and a target
class is selected from the filter dropdown.

The default behavior is to show component of that type that are directly
related to the selected component through 1:M or 1:MC relationships, but
additional objects that are indirectly related can be added through
the use of the 'extra_paths' configuration directive.   *list_paths* is
primarily intended as a debugging tool during the development of extra_paths
patterns to verify that they are having the intended effect.

Example usage:

.. code-block:: bash

    zenpacklib --paths mydevice



.. _zenpacklib-dump_templates:

**************
dump_templates
**************

The *--dump-templates* command is designed to export monitoring templates already
loaded into your Zenoss instance and associated with a ZenPack. It will export
them to the YAML format required for `zenpack.yaml`. It is up to you to merge
that YAML with your existing `zenpack.yaml`. file.

Example usage:

.. code-block:: bash

    zenpacklib --dump-templates ZenPacks.example.BetterAlreadyBeInstalled

.. _zenpacklib-dump_event_classes:

******************
dump_event_classes
******************

The *--dump-event-classes* command is designed to export event class organizers and
mappings already loaded into your Zenoss instance and associated with a ZenPack. It 
will export them to the YAML format required for `zenpack.yaml`. It is up to you to merge
that YAML with your existing `zenpack.yaml`. file.

Example usage:

.. code-block:: bash

    zenpacklib --dump-event-classes ZenPacks.example.BetterAlreadyBeInstalled

.. _zenpacklib-dump_process_classes:

********************
dump_process_classes
********************

The *--dump-process-classes* command is designed to export process class organizers and
classes already loaded into your Zenoss instance and associated with a ZenPack. It 
will export them to the YAML format required for `zenpack.yaml`. It is up to you to merge
that YAML with your existing `zenpack.yaml`. file.

Example usage:

.. code-block:: bash

    zenpacklib --dump-process-classes ZenPacks.example.BetterAlreadyBeInstalled

.. _zenpacklib-optimize:

********
optimize
********

The *--optimize* command (experimental) is designed to examine your `zenpack.yaml` file and 
rearrange it for brevity and use of DEFAULTS where detected.  Once optimized, the command compares
the original YAML file to the optimized version to ensure that the same objects are created.  The 
change detection, however, is still being improved and may output false warnings.  It is recommended to
double-check the optimized YAML output.

Example usage:

.. code-block:: bash

    zenpacklib --optimize zenpack.yaml


.. _zenpacklib-version:

*******
version
*******

The *version* command prints the zenpacklib version.

Example usage:

.. code-block:: bash

    zenpacklib --version
