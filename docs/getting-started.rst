.. _getting-started:

###############
Getting Started
###############

zenpacklib is a single Python module designed to be packaged with every ZenPack.
There is a single file, `zenpacklib.py` that must be distributed with each
ZenPack.


.. _downloading:

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
  wget http://zenpacklib.zenoss.com/zenpacklib.py
  chmod 755 zenpacklib.py

After downloading you can check the version by running the following command as
the *zenoss* user.

.. code-block:: bash

    ./zenpacklib.py version


.. _create-a-zenpack:

******************
Creating a ZenPack
******************

There are two ways to get started with zenpacklib. You can either use it to
create a new ZenPack from the command line, or you can copy it into an existing
ZenPack. We'll start by creating a ZenPack from the command line.

Run the following command to create a new ZenPack.

.. code-block:: bash

    ./zenpacklib.py create ZenPacks.acme.Widgeter

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

    cd ZenPacks.acme.Widgeter/ZenPacks/acme/Widgeter
    ./zenpacklib.py lint zenpack.yaml

Lint will print information about errors it finds in the YAML file. If nothing
is printed, lint thinks the YAML is correct.

**********
What Next?
**********

You can either start with some :ref:`tutorials` or jump right into the
:ref:`yaml-reference`.
