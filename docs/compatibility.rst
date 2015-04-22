.. _compatibility:

#############
Compatibility
#############

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
1.0                 4.2, 5.0 :ref:`* <pyyaml-requirement>`
==================  ======================================

Compatibility only considers <major>.<minor> versions of both zenpacklib and
Zenoss. Maintenance or patch releases of each are always considered compatible.


.. _determining-version:

*******************
Determining Version
*******************

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

zenpacklib requires that PyYAML be installed in the Zenoss system. PyYAML was
not a standard part of a Zenoss system until Zenoss 5. To use zenpacklib, or to
use a ZenPack built with zenpacklib on a Zenoss 4.2 system you must first make
sure that PyYAML is installed.

.. note:: PyYAML has been added to Zenoss 4.2.5 as of SP457.

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
