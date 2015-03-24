.. _zProperties:

###########
zProperties
###########

zProperties are one part of Zenoss' hierarchical configuration system. They are
configuration properties that can be specified on any device class including
the root /Devices class, and on any individual device.


.. _zProperty-inheritance:

*********************
zProperty Inheritance
*********************

The most-specific value for a zProperty within the hierarchy will be used for
any given device. For instance, given a device *linux1* in the /Server/Linux
device class. The value for zSnmpMonitorIgnore will be checked first on the
linux1 device. If it is not set locally on the device, the /Server/Linux device
class will then be checked. If not set there, /Server will be checked. Finally
the value at / (or /Devices) will be checked as a final resort. Since all
zProperties must have a default values that is set at the root device class,
there will always be a value for the zProperty. Even if it is an empty string.


.. _adding-zProperties:

******************
Adding zProperties
******************

To add a zProperty to your ZenPack you must include a *zProperties* section in
your YAML file. The following example shows an example of adding two
zProperties.

.. code-block:: yaml

   zProperties:
     zWidgeterEnable:
       category: ACME Widgeter
       type: boolean
       default: true

     zWidgeterInterval:
       category: ACME Widgeter
       type: string
       default: 300

Each of these zProperty entries specifies a *category*, *type* and *default*.
These are the only valid fields of the a zProperty entry. However, each of
these fields has a default value that will be used if the field isn't
explicitly specified. For example, the default value for *type* is string. So
the above example could be shortened slightly by omitting the explicit *type*
on zWidgeterInterval.

.. code-block:: yaml

   zProperties:
     zWidgeterEnable:
       category: ACME Widgeter
       type: boolean
       default: true

     zWidgeterInterval:	
       category: ACME Widgeter
       default: 300

There is a special zProperty entry named *DEFAULT* that can be used to further
shorten definitions in cases where you're adding many zProperties. The
following example shows how *DEFAULT* can be used to replace the duplicated
*category* property.

.. code-block:: yaml

   zProperties:
     DEFAULT:
       category: ACME Widgeter

     zWidgeterEnable:
       type: boolean
       default: true

     zWidgeterInterval:
       default: 300

Each zProperty listed in *zProperties* will be created when the ZenPack is
installed, and removed when the ZenPack is removed.


.. _zProperty-reference:

*******************
zProperty Reference
*******************

The following fields are valid for a zProperty entry.

name
  :Description: Name (e.g. zWidgeterEnable). Must be begin with a lowercase "z".
  :Required: Yes
  :Type: string
  :Default Value: *implied from key in zProperties map*

type
  :Description: Type of property: *string*, *password*, *lines* or *boolean*.
  :Required: No
  :Type: string
  :Default Value: string

default
  :Description: Default value. The default value depends on the type: string="", password="", lines=[], boolean=false.
  :Required: No
  :Type: *varies*
  :Default Value: *varies*

category
  :Description: Category name. (e.g. ACME Widgeter). Used to group related zProperties in the UI.
  :Required: No
  :Type: string
  :Default Value: "" (empty string)
