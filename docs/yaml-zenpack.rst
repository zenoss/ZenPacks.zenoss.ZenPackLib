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

See the following for more information on each of these fields.

* :ref:`zProperties`
* :ref:`device-classes`
* :ref:`classes-and-relationships`


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
