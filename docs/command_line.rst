.. _command-line-usage:

##################
Command Line Usage
##################

While most of zenpacklib's functionality is as a Python module to be used as a
library for helping build ZenPacks, `zenpacklib.py` also acts as a command line
script to perform some useful actions.

You can choose to make `zenpacklib.py` executable then execute it as as script.

.. code-block:: bash

    chmod 755 zenpacklib.py
    ./zenpacklib.py

Or you can leave it non-executable and execute it through python.

.. code-block:: bash

    python zenpacklib.py

In either case you will get the following help.

.. code-block:: text

    Usage: zenpacklib.py <command> [options]

    Available commands and example options:

      # Check zenpack.yaml for errors.
      lint zenpack.yaml

      # Print yUML (http://yuml.me/) class diagram source based on zenpack.yaml.
      class_diagram yuml zenpack.yaml

      # Export existing monitoring templates to yaml.
      dump_templates ZenPacks.example.AlreadyInstalled

      # Convert a pre-release zenpacklib.ZenPackSpec to yaml.
      py_to_yaml ZenPacks.example.AlreadyInstalled

      # Print zenpacklib version.
      version

The following commands are supported:

* :ref:`create <zenpacklib-create>`: Create a new zenpacklib-enabled ZenPack source directory.
* :ref:`lint <zenpacklib-lint>`: Provides syntax and correctness on a YAML file.
* :ref:`class_diagram <zenpacklib-class_diagram>`: Export yUML (yuml.me) class diagram from a YAML file.
* :ref:`dump_templates <zenpacklib-dump_templates>`: Export existing monitoring templates to YAML.
* :ref:`py_to_yaml <zenpacklib-py_to_yaml>`: Converts the Python syntax used in pre-release versions of zenpacklib to YAML.
* :ref:`list_paths <device name>`: Using the specified device, print a report of paths between objects.
* :ref:`version <zenpacklib-version>`: Print zenpacklib version.


.. _zenpacklib-create:

******
create
******

The *create* command will create a source directory for a zenpacklib-enabled
ZenPack. This will include a setup.py, MANIFEST.in, the namespace and module
directories, and a zenpack.yaml in the module directory. It will also make a
copy of zenpacklib.py inside the module directory. This ZenPack will be ready to
be installed immediately though it will contain no functionality yet.

Example usage:

.. code-block:: bash

    python zenpacklib.py create ZenPacks.example.MyNewPack

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
      - copying: ../../../zenpacklib.py to ZenPacks.test.ZPLTest2/ZenPacks/test/ZPLTest2


.. _zenpacklib-lint:

****
lint
****

The *lint* command will check the provided YAML file for correctness. It checks
that the provided file is syntactically-valid YAML, and it will also perform
many others checks that validate that the contained entries, fields and their
values are valid.

The following example shows an example of using an unrecognized parameter in a
monitoring template.

.. code-block:: bash

    python zenpacklib.py lint zenpack.yaml
    zenpack.yaml:47:9: Unrecognized parameter 'targetPythnoClass' found while processing RRDTemplateSpec

.. note:: *lint* will provide no output if the provided YAML file is found to be correct.


.. _zenpacklib-class_diagram:

*************
class_diagram
*************

The *class_diagram* command will use :doc:`classes_and_relationships` in the
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

    python zenpacklib.py class_diagram yuml zenpack.yaml

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


.. _zenpacklib-py_to_yaml:

**********
py_to_yaml
**********

The *py_to_yaml* command is designed for a very specific purpose that most
people will not find useful. Earlier pre-release versions of zenpacklib required
that the ZenPack be defined via a call to zenpacklib.ZenPackSpec() with Python
data structures instead of via a YAML file. *py_to_yaml* converts this style of
definition to a YAML file suitable for use with current versions of zenpacklib.

Example usage:

.. code-block:: bash

    python zenpacklib.py py_to_yaml ZenPacks.example.BetterAlreadyBeInstalled

.. _zenpacklib_list_paths:

**********
list_paths
**********

The *list_paths* command shows the paths between defined component classes
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

    python zenpacklib.py list_paths mydevice



.. _zenpacklib-dump_templates:

**************
dump_templates
**************

The *dump_templates* command is designed to export monitoring templates already
loaded into your Zenoss instance and associated with a ZenPack. It will export
them to the YAML format required for `zenpack.yaml`. It is up to you to merge
that YAML with your existing `zenpack.yaml`. file.

Example usage:

.. code-block:: bash

    python zenpacklib.py dump_templates ZenPacks.example.BetterAlreadyBeInstalled


.. _zenpacklib-version:

*******
version
*******

The *version* command prints the zenpacklib version.

Example usage:

.. code-block:: bash

    python zenpacklib.py version
