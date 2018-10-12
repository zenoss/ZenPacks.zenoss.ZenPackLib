.. _compatibility:

#############
Compatibility
#############

Starting with version 2.0, zenpacklib.py will ship as a separately installed ZenPack.
This change offers several advantages over the earlier distribution method along with 
many new features and fixes.  Existing ZenPacks based on earlier versions of zenpacklib.py
should coexist peacefully with those based on the newer version, and eventual migration to
version 2.0 should be relatively painless.  Future versions of Zenoss-provided ZenPacks will
use the newer ZenPackLib version as they are developed and released.

*************************
Migrating ZenPacks to 2.0
*************************

For the most part, migrating to ZenPackLib 2.0 should be straightforward and requires minimal changes
to your ZenPack.  These largely involve changing import statements where appropriate and removing the
older zenpacklib.py files

.. note::

   ZenPacks based on ZenPackLib 2.0 will need to have a dependency set to prevent potential issues when 
   installing or removing them.  If ZenPackLib 2.0 is not installed, a dependent ZenPack should refuse to
   install until the dependency is met.  Similarly, ZenPackLib 2.0 should refuse removal if dependent ZenPacks
   are still installed.  To achieve this, make sure that the INSTALL_REQUIRES variable in the setup.py file 
   contains the following:
   
   INSTALL_REQUIRES = ['ZenPacks.zenoss.ZenPackLib']
   
   Please note that "INSTALL_REQUIRES" may already contain entries, and these should be preserved if they exist.
   
   This can also be configured in the GUI if the dependent ZenPack is installed in develop mode.


The __init__.py file will need its import statements changed.

.. code-block:: python

   from . import zenpacklib

changes to:

.. code-block:: python

   from ZenPacks.zenoss.ZenPackLib import zenpacklib

while:

.. code-block:: python

   CFG = zenpacklib.load_yaml()

remains unchanged unless some of the new logging capabilities are desired such as:

.. code-block:: python

   CFG = zenpacklib.load_yaml(verbose=True, level=10)


In addition, the statement (if it exists):

.. code-block:: python

   from . import schema 

should be changed to:

.. code-block:: python

   schema = CFG.zenpack_module.schema

or added if it does not exist.

.. note::

   Care should also be taken to delete the zenpacklib.py and zenpacklib.pyc files in 
   the ZenPack's source directory, since leaving them in place may cause unforseen behavior.

.. note::

   Import statements should also be checked throughout any class overrides or 
   other python files, since the statements will fail if they refer to the older zenpacklib.py.

.. note::

   The tag *!ZenPackSpec* is not necessary and should be removed from your yaml definitions.

Convert Relations
-----------------

Class relationships need to be redefined when converting from prior ZP versions to ZP2.
Below is the old style of defining class relationships; Note that the relationship must be defined in both python classes.  For instance, class 'Lightsaber' has a definition for the relation to class 'KyberCrystal'. But you will also find the inverted relation defined in the class 'KyberCrystal' for class "Lightsaber'.

.. code-block:: python
   from StarWars.weapons.Device import Saber as LightSaberDevice

   class Lightsaber (LightSaberDevice)
       _relations = ManagedEntity._relations + (
           ('crystal', ToMany(
               ToOne, MODULE_NAME['KyberCrystal'], 'saber')),
           ('diatium', ToOne(
               ToOne, MODULE_NAME['DiatiumPowerCell'], 'saber')),
           ('emitter', ToMany(
               ToOne, MODULE_NAME['BladeEmitter'], 'saber')),
           ('energizers', ToMany(
               ToOne, MODULE_NAME['CyclingFieldEnergizers'], 'saber')),        
       )


   from StarWars.items.Component import Crystal as KyberCrystalComponent

   class KyberCrystal (KyberCrystalComponent)
       _relations = ManagedEntity._relations + (
           ('saber', ToOne(
               ToMany, MODULE_NAME['Lightsaber'], 'crystal')),
           ('color', ToManyCont(
               ToOne, MODULE_NAME['BladeColor'], 'crystal')),
       )


The syntax for defining relations is not pretty, but is redundent, inverted, and error prone.
To resolve this, class relations are now defined just once in the ZP2 yaml file as seen below.

.. code-block:: python
   Defining class_relationships in the yaml:
     - Lightsaber(crystal) 1:M KyberCrystal(saber)
     - Lightsaber(diatium) 1:1 DiatiumPowerCell(saber)
     - Lightsaber(emitter) 1:M BladeEmitter(saber)
     - Lightsaber(energizers) 1:M CyclingFieldEnergizers(saber)
     - KyberCrystal(color) 1:MC BladeColor(crystal)

For each class in your ZenPack, you'll need to convert the _relations section to yaml definitions.
Once the relations have been defined you can comment out or delete the code from the python code.

Convert Classes
---------------

Any classes defined in the class_relationships section or has older zp1 style properties and/or meta_types (seen in below sections)
should be updated to ZP2.  To do this, we'll add a 'classes' section to the yaml.  The classes definition must have a 'DEFAULTS' section with a base that inherites from zenpacklib.Component.  From there, python classes can be defined in the yaml, as seen here.
If the python class is derived from a parent object, be sure to define the parent as the base.

.. code-block:: python
   classes:
     DEFAULTS:
       base: [zenpacklib.Component]
     Lightsaber:
       base: [StarWars.weapons.Device.Saber]
     KyberCrystal:
       base: [StarWars.items.Component.Crystal]

Then, back in the python class def, we'll need to make a couple changes.  First, import the yaml defined schema.  Second, have the class now inherite from the schema class.

.. code-block:: python
   import schema from .
   class Lightsaber (schema.LightSaber)
     ...

   import schema from .
   class KyberCrystal (schema.KyberCrystal)
     ...


In some cases, this inheritance pattern will do something a little different, essentially inheriting from zenpacklib. For example:

.. code-block:: python
   from Products.ZenModel.DeviceComponent import DeviceComponent
   class RestrainingBolt (DeviceComponent)
     ...

Will now resemble something closer to this:

.. code-block:: python
   from schema import .
   class RestrainingBolt (schema.RestrainingBolt)
     ...

   classes:
     ...
     RestrainingBolt:
       base: [zenpacklib.Component]
     ...

Here's a short list of a few classes that change the base inheritance:
  Products.ZenModel.DeviceComponent.DeviceComponent  -->  zenpacklib.Component
  Products.ZenModel.HWComponent.HWComponent          -->  zenpacklib.HWComponent
  Products.ZenModel.OSComponent.OSComponent          -->  zenpacklib.OSComponent


Convert Properties
------------------

Class properties were originally defined in the class, and referenced the variables of the class that were
accessable; ie, they defined what was visible in the console.  Below is an old style of defining properties in python.

.. code-block:: python
   class Lightsaber
       _properties = ManagedEntity._properties + LightsaberObject._properties + (
           {'id': 'owner', 'type': 'string', 'label': 'Jedi or Sith Owner'},
           {'id': 'color', 'type': 'string', 'label': 'Blade Color'},
           {'id': 'length', 'type': 'int', 'label': 'Length of Blade'},
       )
       owner = ""
       color = ""
       length = 0

However, with ZP2 style zenpacks these properties have been moved to the yaml file as part of the class definitions.
Hence the properties section can be commented out or removed from the class as well as any of the defined variables.
Note that 'type: string' is not transcribed, this is becuse 'string' is the default value for the field 'type'.

.. code-block:: python
   classes:
     ...
     Lightsaber:
       base: []
       properties:
         owner:
           label: Jedi or Sith Owner
         color:
           label: Blade Color
         length:
           type: int
           label: Blade Length
     ...

Update Z-Properties
-------------------

The __init__.py file may have additional zProperties defined.  These properties need to be transferred to the zenpack.yaml and removed from the __init__.py file.  

Update Meta Types
-----------------

Some classes may have a meta type defined. You can find the meta type definition in the class for older zenpacks.
.. code-block:: python
  portal_type = meta_type = 'SWLightSaber'

To updated this to be ZP2 compatible, simple add a 'meta_type' line to the yaml, then comment out or remove the old code.

.. code-block:: python
   classes:
     ...
     Lightsaber:
       meta_type: SWLightSaber
     ...

Debugging help and tools
------------------------

One of the most difficult and tedious pieces to converting a zenpack is getting all the relationships to load, build, and link correctly when modeling.  Especially when the ZenPack is inheriting from other zenpacks which are still using the older format.  If you cannot model the device without getting errors, first go into the console and disable all but one module.  It will be best to work through them one at a time.  In the associated source files to the active module, locate any of the following snipits of code and comment them out:

.. code-block:: python
	maps.Append( RelationshipMap( ... ) )
	updateToOne( ... )
	updateTOMany( ... )
	... etc.

Re-enable them one at a time, running the modeler, until errors are encountered.  There's no easy way to know exactly what is going wrong, however, most of the errors can be fixed by changing the relationship names in the yaml file. Check through the source code and any base classes for clues and hints as to what names should be set to.  

To check whether or not the yaml files contain errors you can use the zendmd command to import/load the zenpack:
.. code-block:: python
	from ZenPacks.zenoss.Lightsaber import CFG,schema

After the zenpack has been loaded you can check various aspects, such as the defined yaml relationships, use the following commands:
.. code-block:: python
	spec = CFG.classes.get("KyberCrystal")
	ob = spec.model_class
	ob._relations

Once a device has been modeled, you can inspect the device, see a list of discovered components, view other properties such as the meta_type, and print any relationships that the component may retain:
.. code-block:: python
	dev=find('16.32.64.128')
	dc_list=dev.getDeviceComponents()
	comp=dc_list[0]
	comp.meta_type
	comp._relationships

.. _new-logging:

*******************
Version 2.0 Logging
*******************

Logging has been substantially enhanced for ZenPackLib version 2.0 and provides numerous
features to aid during development or troubleshooting.  Logging can now be controlled on 
a per-ZenPack basis by supplying additional paramters to the "load_yaml()" method call 
in the ZenPack's __init__.py.file:

The `verbose` parameter, if set to True, will enable logging for this particular ZenPack.  We recommend
setting `verbose` to `True` during ZenPack development so that various error messages can be seen.  We 
also recommend returning this value to `False` prior to release of your ZenPack as some warning messages
may not be useful to the end user.

The `level` paramter controls logging verbosity with the same numeric values used elsewhere in Zenoss.  The 
default value is 30 (WARNING), but setting this to 20 (INFO) or 10 (DEBUG) may be useful during ZenPack 
development.

.. code-block:: python

   CFG = zenpacklib.load_yaml(verbose=True, level=10)

In this example, logging verbosity is enabled with at the DEBUG level.

Every class in ZenPackLib has a "LOG" attribute that can be called within any class override
files you may have.  For example, given the file BasicComponent.py class extension, logging features
would be accessed as follows:


.. code-block:: python
      
      from . import schema
      
      class BasicComponent(schema.BasicComponent):
          """Class override for BasisComponent"""
          def hello_world(self):
              self.LOG.info("You called hello_world")
              return 'Hello World!'



.. note::

   Log messages generated within the new logging framework are written to the Zope logger (event.log) 
   and can be viewed there.  Logging used within class extension files will follow the verbosity 
   and level parameters provided to the "load_yaml" method.
   
   Please note that additional Zope configuration may be required to see log messages, since Zope 
   configuration determines what is accepted for writing to its event log.  For example, if Zope logging
   is set to "warn", then any "info" or "debug" messages will not be logged regardless of the load_yaml parameters
   used.  Zope logging in this case must be set to "info" for ZPL "info", "warning", and "critical" logging.

.. _older-versions:

*******************************
Older Versions of zenpacklib.py
*******************************

.. note::

    The following applies to pre-2.0 versions of zenpacklib.py only.  
    Starting with version 2.0, zenpacklib.py will ship as a separately installed 
    ZenPack designed for use by dependent ZenPacks

Distributing `zenpacklib.py` with each ZenPack allows different ZenPacks in
the same Zenoss system to use different versions of zenpacklib. This can make
things simpler for the ZenPack author as they know which version of zenpacklib
will be used. It will be the one that's shipped with the ZenPack.

This approach does have the drawback of potentially forcing ZenPacks to be
updated to include a new version of zenpacklib to support a new version of
Zenoss. Care will be taken to make each zenpacklib version compatible with as
many versions of Zenoss as possible. Furthermore, care will be taken to make
future versions of Zenoss compatible with existing zenpacklib versions within
reason.

The following table describes which versions of Zenoss are supported by
different versions of zenpacklib.

==================  ======================================
zenpacklib Version  Zenoss Versions
==================  ======================================
1.1                 4.2 :ref:`* <pyyaml-requirement>`, 5.0, 5.1, 5.2
1.0                 4.2 :ref:`* <pyyaml-requirement>`, 5.0, 5.1, 5.2
==================  ======================================

Compatibility only considers <major>.<minor> versions of both zenpacklib and
Zenoss. Maintenance or patch releases of each are always considered compatible.


.. _determining-version:

*******************
Determining Version
*******************

.. note::

    Beginning with version 2.0, you can check the zenpacklib version with either:
    
      zenpacklib --version
    
    from the command line, or by navigating to: 
      
      Advanced -> Settings -> ZenPacks 
    
    in the Zenoss GUI

You can check which version of zenpacklib you're using in two ways. The first is
by using the *version* command line option.

.. code-block:: bash

    python zenpacklib.py version

If you have ZenPack code that needs the version it can also be accessed from
Python code that has imported *zenpacklib* module through the module's
*__version__* property.

.. code-block:: python

    from . import zenpacklib
    zenpacklib.__version__


.. _pyyaml-requirement:

******************
PyYAML Requirement
******************
.. note::

    Beginning with version 2.0, the ZenPacks.zenoss.ZenPackLib ZenPack will refuse
    to install unless PyYAML is already installed

zenpacklib requires that PyYAML be installed in the Zenoss system. PyYAML was
not a standard part of a Zenoss system until Zenoss 5. To use zenpacklib, or to
use a ZenPack built with zenpacklib on a Zenoss 4.2 system you must first make
sure that PyYAML is installed.

.. note::

   PyYAML has been added to Zenoss 4.2.5 as of SP457, and Zenoss 4.2.4 as of
   SP776.

Checking for PyYAML
-------------------

On your main Zenoss 4.2 server run the following command to check for PyYAML.

.. code-block:: bash

    su - zenoss -c "python -c 'import yaml;print yaml.version'"

You will see the version of PyYAML if it installed.

.. code-block:: text

    3.11

You will see the following error if PyYAML is not installed.

.. code-block:: text

    Traceback (most recent call last):
      File "<string>", line 1, in <module>
    ImportError: No module named yaml

Installing PyYAML
-----------------

Run the following command to install PyYAML if it isn't already installed.

.. code-block:: bash

    su - zenoss -c "easy_install PyYAML"

It's normal for the *easy_install* command to print many errors and warnings
even when it successfully installs. Run the first command to verify it's
installed when complete.

If your Zenoss system is distributed to multiple servers for hubs, collectors,
or any other reason you will need to update those hubs and collectors after
installing PyYAML to make sure it also gets installed on them.
