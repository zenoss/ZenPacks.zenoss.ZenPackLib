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
