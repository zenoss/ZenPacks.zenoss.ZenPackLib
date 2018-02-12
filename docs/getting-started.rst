.. _getting-started:

###############
Getting Started
###############

The first thing we'll need to do is install the ZenPackLib ZenPack into our
development system. This is done in the same way as it would be in any Zenoss
system.

The ZenPackLib ZenPack provides the zenpacklib command line tool, which will
allow us to create ZenPacks.

.. note::

    This tutorial assumes your system is already setup as described in
    :ref:`development-environment` and :ref:`getting-started`.


.. _installing-zenpacklib:

*********************
Installing ZenPackLib
*********************

The latest version of ZenPackLib can be downloaded from
`its entry <https://www.zenoss.com/product/zenpacks/zenpacklib>`_ in the
`ZenPack Catalog`_. The following commands show how you would download and
install version 2.0.10.

.. _ZenPack Catalog: https://www.zenoss.com/product/zenpacks

.. note::

    From here on all command should be run as the *zenoss* user on the host
    unless otherwise noted. If you don't login to the host as the *zenoss*
    user, use ``su - zenoss`` to get a login shell.

.. code-block:: bash

    cd /tmp
    wget http://wiki.zenoss.org/download/zenpacks/ZenPacks.zenoss.ZenPackLib/2.0.10/ZenPacks.zenoss.ZenPackLib-2.0.10.egg
    serviced service run zope zenpack-manager install ZenPacks.zenoss.ZenPackLib-2.0.10.egg

Executing *zenpacklib* requires a live Zenoss environment. Always executing it as the *zenoss* user in your Zope container is a good way to have the right environment setup. The following commands demonstrate how to do this.

.. code-block:: bash

    serviced service attach zope # attach to zope container
    su - zenoss # become zenoss user in zope container
    zenpacklib --version
    exit # back to root in container
    exit # back to host

These five commands can be reduced to the following single command if you setup
the helper aliases and functions your ``.bashrc`` recommended in
:ref:`helper-aliases-and-functions`.

.. code-block:: bash

    zenpacklib --version


.. _creating-a-zenpack:

******************
Creating a ZenPack
******************

There are two ways to get started with zenpacklib. You can either use it to
create a new ZenPack from the command line, or you can update an existing
ZenPack to use it. We'll start by creating a ZenPack from the command line.

Run the following commands to create a new ZenPack.

.. code-block:: bash

    # Create ZenPacks in /z so the host and containers can access them.
    cd /z
    zenpacklib --create ZenPacks.acme.Widgeter

This will print several lines to let you know what has been created. Note that
the ZenPack's source directory has been created, but it has not yet been
installed.

.. code-block:: text

    Creating source directory for ZenPacks.acme.Widgeter:
      - making directory: ZenPacks.acme.Widgeter/ZenPacks/acme/Widgeter
      - creating file: ZenPacks.acme.Widgeter/setup.py
      - creating file: ZenPacks.acme.Widgeter/MANIFEST.in
      - creating file: ZenPacks.acme.Widgeter/ZenPacks/__init__.py
      - creating file: ZenPacks.acme.Widgeter/ZenPacks/acme/__init__.py
      - creating file: ZenPacks.acme.Widgeter/ZenPacks/acme/Widgeter/datasources/__init__.py
      - creating file: ZenPacks.acme.Widgeter/ZenPacks/acme/Widgeter/thresholds/__init__.py
      - creating file: ZenPacks.acme.Widgeter/ZenPacks/acme/Widgeter/parsers/__init__.py
      - creating file: ZenPacks.acme.Widgeter/ZenPacks/acme/Widgeter/migrate/__init__.py
      - creating file: ZenPacks.acme.Widgeter/ZenPacks/acme/Widgeter/resources/__init__.py
      - creating file: ZenPacks.acme.Widgeter/ZenPacks/acme/Widgeter/modeler/__init__.py
      - creating file: ZenPacks.acme.Widgeter/ZenPacks/acme/Widgeter/tests/__init__.py
      - creating file: ZenPacks.acme.Widgeter/ZenPacks/acme/Widgeter/libexec/__init__.py
      - creating file: ZenPacks.acme.Widgeter/ZenPacks/acme/Widgeter/modeler/plugins/__init__.py
      - creating file: ZenPacks.acme.Widgeter/ZenPacks/acme/Widgeter/lib/__init__.py
      - creating file: ZenPacks.acme.Widgeter/ZenPacks/acme/Widgeter/__init__.py
      - creating file: ZenPacks.acme.Widgeter/ZenPacks/acme/Widgeter/zenpack.yaml

Now let's take a look at `zenpack.yaml`. This is the file that will define a
large part of what our ZenPack is.

.. code-block:: yaml

    name: ZenPacks.acme.Widgeter

Add Monitoring
--------------

Let's add a device class and a monitoring template to our ZenPack. Change
`zenpack.yaml` to contain the following:

.. code-block:: yaml

    name: ZenPacks.acme.Widgeter

    device_classes:
      /Server/ACME/Widgeter:
        zProperties:
          zDeviceTemplates:
            - WidgeterHealth

        templates:
          WidgeterHealth:
            description: ACME Widgeter monitoring.

            datasources:
              health:
                type: COMMAND
                parser: Nagios
                commandTemplate: "echo OK|percent=100"

                datapoints:
                  percent:
                    rrdtype: GAUGE
                    rrdmin: 0
                    rrdmax: 100

            thresholds:
              unhealthy:
                dsnames: [health_percent]
                eventClass: /Status
                severity: Warning
                minval: 90

            graphs:
              Health:
                units: percent
                miny: 0
                maxy: 0

                graphpoints:
                  Health:
                    dpName: health_percent
                    format: "%7.2lf%%"

Check for Correctness
---------------------

Now that we have a more interesting `zenpack.yaml`, let's have zenpacklib check
that it's correct. This can be done using the :ref:`zenpacklib-lint` command.

.. code-block:: bash

    zenpacklib --lint ZenPacks.acme.Widgeter/ZenPacks/acme/Widgeter/zenpack.yaml

Lint will print information about errors it finds in the YAML file. If nothing
is printed, lint thinks the YAML is correct.


.. _installing-a-zenpack:

********************
Installing a ZenPack
********************

Now that we've created a ZenPack called *ZenPacks.acme.Widgeter* in */z*, we can
install it into our Zenoss system by running the following command.

.. code-block:: bash

    z zenpack --link --install ZenPacks.acme.Widgeter

Zenoss must be restarted anytime a new ZenPack is installed. A full restart of
the entire system can be performed by running one of the following commands
depending on what distribution of Zenoss you have installed..

.. code-block:: bash

    serviced service restart Zenoss.core
    serviced service restart Zenoss.resmgr

Technically it isn't necessary to restart everything. A lot of the
infrastructure services don't use ZenPack code. The following is a smaller list
of services that you're likely to need to restart after installing and
modifying ZenPacks during development.

- Zope
- zenhub
- zeneventd
- zenactiond
- zenjobs

The following command will quickly restart just these services.

.. code-block:: bash

    echo Zope zenhub zeneventd zenactiond zenjobs | xargs -n1 serviced service restart

**********
What Next?
**********

You can either start with some :ref:`tutorials` or jump right into the
:ref:`yaml-reference`.
