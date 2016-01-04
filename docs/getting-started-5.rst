.. _getting-started-5:

###############
Getting Started
###############

zenpacklib is a single Python module designed to be packaged with every ZenPack.
There is a single file, `zenpacklib.py` that must be distributed with each
ZenPack.

.. note::

    Be sure that you have a good :ref:`development-environment-5` setup before
    proceeding.

.. note::

    All commands in this section should be run as the *zenoss* user on the host
    unless otherwise noted. If you don't login to the host as the *zenoss* user,
    use ``su - zenoss`` to get a login shell.


.. _downloading-zenpacklib-5:

***********
Downloading
***********

Depending on what versions of Zenoss your ZenPack is supporting you may need to
get a specific version of zenpacklib. See :ref:`compatibility` for more
information. Since the latest version of zenpacklib is usually compatible with
recent versions of Zenoss it's usually safe to get the most recent release. This
can be done with the following commands.

.. code-block:: bash

    su - zenoss
    cd /z
    wget http://zenpacklib.zenoss.com/zenpacklib.py
    chmod 755 zenpacklib.py

Executing *zenpacklib.py* requires a live Zenoss environment. Always executing
it as the *zenoss* user in your Zope container is a good way to have the right
environment setup. The following commands show how to do this.

.. code-block:: bash

    serviced service attach zope # attach to zope container
    su - zenoss # become zenoss user in zope container
    /z/zenpacklib.py version
    exit # back to root in container
    exit # back to host

These five commands can be reduced to the following single command if you setup
the helper aliases and functions your ``.bashrc`` recommended in
:ref:`helper-aliases-and-functions-5`.

.. code-block:: bash

    zenpacklib version


.. _creating-a-zenpack-5:

******************
Creating a ZenPack
******************

There are two ways to get started with zenpacklib. You can either use it to
create a new ZenPack from the command line, or you can copy it into an existing
ZenPack. We'll start by creating a ZenPack from the command line.

Run the following commands to create a new ZenPack.

.. code-block:: bash

    # Create ZenPacks in /z so the host and containers can access them.
    cd /z
    zenpacklib create ZenPacks.acme.Widgeter

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
      - creating file: ZenPacks.acme.Widgeter/ZenPacks/acme/Widgeter/__init__.py
      - creating file: ZenPacks.acme.Widgeter/ZenPacks/acme/Widgeter/zenpack.yaml
      - copying: ./zenpacklib.py to ZenPacks.acme.Widgeter/ZenPacks/acme/Widgeter

Now let's take a look at `zenpack.yaml`. This is the file that will define what
our ZenPack does.

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

    zenpacklib lint ZenPacks.acme.Widgeter/ZenPacks/acme/Widgeter/zenpack.yaml

Lint will print information about errors it finds in the YAML file. If nothing
is printed, lint thinks the YAML is correct.


.. _installing-a-zenpack-5:

********************
Installing a ZenPack
********************

Now that we've created a ZenPack called *ZenPacks.acme.Widgeter* in */z*, we can
install it into our Zenoss system by running the following command.

.. code-block:: bash

    z zenpack --link --install ZenPacks.acme.Widgeter

Zenoss must be restarted anytime a new ZenPack is installed. A full restart of
the entire system can be performed by running one of the following command.

.. code-block:: bash

    serviced service restart Zenoss.core
    serviced service restart Zenoss.resmgr

Technically it isn't necessary to restart everything. A lot of the
infrastructure services don't use ZenPack code. The following is a smaller list
of services that you're likely to need to restart after installing and modifying
ZenPacks during development.

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

You can either start with some :ref:`tutorials-5` or jump right into the
:ref:`yaml-reference`.
