###############
Getting Started
###############

zenpacklib is a single Python module designed to be packaged with every
ZenPack. There is a single file, `zenpacklib.py` that must be distributed with
each ZenPack.


***********
Downloading 
***********

Depending on what versions of Zenoss your ZenPack is supporting you may need
to get a specific version of zenpacklib. See :ref:`compatibility` for more
information. Since the latest version of zenpacklib is usually compatible with
recent versions of Zenoss it's usually safe to get the most recent release.
This can be done with the following command.

.. code-block:: bash

  wget https://raw.githubusercontent.com/zenoss/zenpacklib/master/zenpacklib.py

If you want a specific version, replace *master* in the above URL with the
specific version such as *1.0.0*. Replace *master* with *develop* if you want
to test with the absolute latest work-in-progress version.

.. warning::

  You should never release a ZenPack with a *develop* version of zenpacklib.


**********
Installing
**********

Now that you have `zenpacklib.py` you need to copy it into your ZenPack's
source directory. For example, creating the ZenPacks.acme.Widgeter ZenPack
will create the following directory.

  ZenPacks.acme.Widgeter/ZenPacks/acme/Widgeter

This directory is the source directory into which you should copy
`zenpacklib.py`.

.. code-block:: bash

  cp zenpacklib.py ZenPacks.acme.Widgeter/ZenPacks/acme/Widgeter

The `zenpacklib.py` file must be copied into this directory using commands such
as the following.

.. todo:: Note PyYAML requirement.


**********
First YAML
**********

Now you must create the YAML file that will describe your ZenPack. The
following example shows the most basic YAML file that can be created. Create
a file named `zenpack.yaml` in the same directory into which you copied
`zenpacklib.py`.

.. code-block:: yaml

  name: ZenPacks.acme.Widgeter

By itself, this doesn't accomplish anything. However, it is enough to
demonstrate zenpacklib's linting capability. Run the following command to lint
`zenpack.yaml`. The lint function validates the YAML file. Any syntax errors,
invalid entries or values will be printed. If nothing is printed, the YAML file
is valid. See :ref:`zenpacklib-lint` for more information on lint.

.. code-block:: bash

  python zenpacklib.py lint zenpack.yaml

Now that you've confirmed that your `zenpack.yaml` is valid you must edit
`__init__.py` in the same directory to cause your ZenPack to load it. Your
`__init__.py` should contain the following code.

.. code-block:: python

  from . import zenpacklib
  import os

  CFG = zenpacklib.load_yaml(os.path.join(os.path.dirname(__file__), 'zenpack.yaml'))

Now you're ready to add :doc:`zProperties`, :doc:`device_classes`,
:doc:`monitoring_templates`, and :doc:`classes_and_relationships` to your
ZenPack.
