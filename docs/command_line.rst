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

In either case you will get the following single line of help.

.. code-block:: text

    Usage: zenpacklib.py lint <file.yaml> | py_to_yaml <zenpack name> | dump_templates <zenpack_name> | class_diagram [yuml] <file.yaml>

As you can see there are four supported actions. 

* :ref:`lint <zenpacklib-lint>`: Provides syntax and correctness on a YAML file.
* :ref:`class_diagram <zenpacklib-class_diagram>`: Export yUML (yuml.me) class diagram from a YAML file.
* :ref:`py_to_yaml <zenpacklib-py_to_yaml>`: Converts the Python syntax used in pre-release versions of zenpacklib to YAML.
* :ref:`dump_templates <zenpacklib-dump_templates>`: Export existing monitoring templates to YAML.

*lint* and class_diagram require a YAML file, whereas *py_to_yaml* and
*dump_templates* require the name of a ZenPack that's already installed because
they're designed to help convert existing ZenPacks to zenpacklib.


.. _zenpacklib-lint:

****
lint
****

The *lint* action will check the provided YAML file for correctness. It checks
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

The *class_diagram* action will use :doc:`classes_and_relationships` in the
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

The *py_to_yaml* action is designed for a very specific purpose that most people
will not find useful. Earlier pre-release versions of zenpacklib required that
the ZenPack be defined via a call to zenpacklib.ZenPackSpec() with Python data
structures instead of via a YAML file. *py_to_yaml* converts this style of
definition to a YAML file suitable for use with current versions of zenpacklib.

Example usage:

.. code-block:: bash

    python zenpacklib.py py_to_yaml ZenPacks.example.BetterAlreadyBeInstalled


.. _zenpacklib-dump_templates:

**************
dump_templates
**************

The *dump_templates* action is designed to export monitoring templates already
loaded into your Zenoss instance and associated with a ZenPack. It will export
them to the YAML format required for `zenpack.yaml`. It is up to you to merge
that YAML with your existing `zenpack.yaml`. file.

Example usage:

.. code-block:: bash

    python zenpacklib.py dump_templates ZenPacks.example.BetterAlreadyBeInstalled
