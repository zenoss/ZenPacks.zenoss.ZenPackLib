.. _development-environment:

#######################
Development Environment
#######################

The process of developing a ZenPack can be made much faster and easier by
starting with a good development environment. A good development environment
should do the following.

- Isolate your changes from other users changes or a production systems.
- Allow you to quickly see the result of changes for faster iteration.
- Allow you to easily troubleshoot when changes don't have the desired effect.

The following recommendations provide a good starting point for anyone wanting
to do ZenPack development on Zenoss 5.


.. _installing:

**********
Installing
**********

You must have Zenoss installed to develop ZenPacks. I recommend starting by
creating a dedicated Zenoss installation for your own development. Start by
following the normal installation instructions available at docs.zenoss.com_
with the following notes.

- System requirements for development can be lower. See below.
- A single-host installation should be used for development.
- Any supported operating system can be used. This guide covers Enterprise Linux 5.
- Verify that Zenoss has been deployed and its web interface is working.

.. _docs.zenoss.com: http://docs.zenoss.com/


.. _system-requirements:

System Requirements
===================

A development system will usually have system requirements lower than those of a
production Zenoss system. This is because it likely won't be storing as much
data, supporting as many web users, or even performing continual monitoring.
Your development system should have at least the following resources.

- 4 CPU cores.
- 20 GB memory.
- 75 GB storage.


.. _configuring-system:

**********************
Configuring the System
**********************

We'll want to make the following changes to our development system to make
ourselves more productive. Each will be detailed in the following sections.

- Add a *zenoss* user to the host that matches the same user in containers.
- Create a */z* directory on the host to share with containers.
- Configure serviced to automatically share */z* with all containers.

First make sure that you have either the Zenoss.core or Zenoss.resmgr service
deployed and running, and that you're able to login to its web interface. All
commands in the following sections should be run as root or through sudo unless
otherwise noted.

Add a "zenoss" User
===================

To make development easier we're going to be sharing files between the host and
docker containers running on the host. We can create a *zenoss* user on the host
that matches the UID (user ID) and GID (group ID) of the zenoss user in the
containers to avoid having to worry about permissions problems with those shared
files.

.. code-block:: bash

    groupadd --gid=1206 zenoss
    adduser --uid=1337 --gid=1206 zenoss

It'll also be useful for our *zenoss* user to be able to use sudo and docker
commands. We can allow that by adding the user to the *wheel* and *docker*
groups respectively.

.. code-block:: bash

    usermod -a -G wheel zenoss
    usermod -a -G docker zenoss

If running Zenoss 5.2 or later, we need to add the user to the *serviced* group
as well, in order to interact with serviced containers.

.. code-block:: bash

    usermod -a -G serviced zenoss

.. _helper-aliases-and-functions:

Helper Aliases and Functions
----------------------------

A lot of the commands you'll use while developing ZenPacks must be executed
inside a Zenoss container. Constantly having to attach to the Zope container,
switch to the zenoss user, execute the command, and exit the container is
tedious. With a few additions to our zenoss user's ``.bashrc``, we can eliminate
those tedious steps.

Add the following lines to the end of ``/home/zenoss/.bashrc``.

.. code-block:: bash

    # ZenPack development helpers.
    alias zope='serviced service attach zope su zenoss -l'
    alias zenhub='serviced service attach zenhub su zenoss -l'
    z () { serviced service attach zope su zenoss -l -c "cd /z;$*"; }
    zenbatchload () { z zenbatchload $*; }
    zendisc () { z zendisc $*; }
    zendmd () { z zendmd $*; }
    zenmib () { z zenmib $*; }
    zenmodeler () { z zenmodeler $*; }
    zenpack () { z zenpack $*; }
    zenpacklib () { z zenpacklib $*; }
    zenpython () { z zenpython $*; }

Next time you login as the zenoss user, you'll have new commands available.

- *zope*: Opens the zenoss user shell in the running Zope container.
- *zenhub*: Opens the zenoss user shell in the running zenhub container.
- *z*: Run any command as zenoss user in running Zope container.

  - *zendisc*: Discovers new devices.
  - *zendmd*: Opens zendmd console.
  - *zenmib*: Import SNMP MIB files.
  - *zenmodeler*: Remodels existing devices.
  - *zenpack*: For installing and removing ZenPacks.
  - *zenpacklib*: Runs zenpacklib commands.

Authenticating as "zenoss"
--------------------------

You will likely want to login to the system as the *zenoss* user after getting
the system configured. That way you won't have to switch (su) to the user to
make sure files you create have the right permissions. I recommend either
setting a password for the user, or adding your public key to the user's
*authorized_keys* file to support this.

Optionally set the *zenoss* user's password:

.. code-block:: bash

    passwd zenoss

Optionally add your SSH public key to the *zenoss* user's *authorized_keys* file
to login without a password:

.. code-block:: bash

    mkdir -p /home/zenoss/.ssh
    chmod 700 /home/zenoss/.ssh
    cat >> /home/zenoss/.ssh/authorized_keys
    ... paste your public key, enter, ctrl-D ...
    chmod 600 /home/zenoss/.ssh/authorized_keys
    chown -R zenoss:zenoss /home/zenoss/.ssh

Create a "/z" Directory
=======================

Now we can create a directory to share that the zenoss user on the host and in
the container will be able to use. The specific path of this directory isn't
particularly important, but I like using */z* because it's as short as possible.

.. code-block:: bash

    mkdir -p /z
    chown -R zenoss:zenoss /z

Mount "/z" Into All Containers
==============================

Now we can configure serviced to automatically share (bind mount) the host's /z
directory into every container it starts. This will let us use the same files on
the host and in containers using the exact same path.

Edit */etc/default/serviced*. Find the existing *SERVICED_OPTS* line. It will
likely be commented out (with a #) and look like the following.

.. code-block:: text

    # Arbitrary serviced daemon args
    # SERVICED_OPTS=

Uncomment it, and add the bind mount configuration as follows.

.. code-block:: text

    # Arbitrary serviced daemon args
    SERVICED_OPTS="--mount *,/z,/z"

You must then restart serviced.

.. code-block:: bash

    systemctl restart serviced


Test "/z" Sharing
=================

Now you can verify that both the host and containers can read and write files in
*/z*.

On the host:

.. code-block:: bash

    su - zenoss # becomes zenoss user on host
    touch /z/host
    serviced service attach zenhub # attach to a container
    su - zenoss # becomes zenoss user in container
    rm /z/host
    touch /z/container
    exit # back to container root user
    exit # back to host zenoss user
    rm /z/container
    exit # back to host root user


.. _configuring-zenoss-services:

***************************
Configuring Zenoss Services
***************************

There are some optional tweaks you can make to Zenoss service definitions to
make development faster and easier. We'll go through the following here.

- Reducing Zope to a single instance so breakpoints can be used.
- Setting unnecessary services to not automatically launch.

Reducing Zope to a Single Instance
==================================

Out of the box, at least in Zenoss.resmgr, Zope is configured to run a minimum
of two instances. This is problematic when you insert a breakpoint
(pdb.set_trace()) in code run by Zope because you can't be sure the breakpoint
will occur in the instance of Zope you happen to be running in the foreground.

Run the following command to edit the Zope service definition. This will open
*vi* with Zope's JSON service definition.

.. code-block:: bash

    serviced service edit Zope

Search this file for "Instances" with the quotes. You should see a section that
looks something like the following. Change *Instances*, *Min*, and *Default* to
1. Then save and quit.

.. code-block:: text

    "Instances": 6,
    "InstanceLimits": {
      "Min": 2,
      "Max": 0,
      "Default": 6
    },

Run the following command to restart Zope and affect the change.

.. code-block:: bash

    serviced service restart Zope

Setting Services to Manual Launch
=================================

The default Zenoss service templates are configured to launch almost all
services they contain automatically. When developing ZenPacks it's usually
unnecessary to have all of the collector process such as zenping running. These
services are consuming memory, CPU, and may need to be restarted frequently as
you're making code changes. To avoid all of that you can configure some services
to not launch automatically when you start the service.

Run the following command to edit zenping's service definition to make it not
automatically launch.

.. code-block:: bash

    serviced service edit zenping

Search this file for "Launch" with the quotes. You should see a section that
looks like the following. Change *auto* to *manual*. Then save and quit.

.. code-block:: text

    "Launch": "auto",

This won't stop zenping if it was already running, but it will prevent it from
starting up next time you start Zenoss.core or Zenoss.resmgr.

Here's the base list of services you should consider setting to the manual
launch mode.

- zencommand
- zenjmx
- zenmail (defaults to manual)
- zenmodeler
- zenperfsnmp
- zenping
- zenpop3 (defaults to manual)
- zenprocess
- zenpython
- zenstatus
- zensyslog
- zentrap

Here are some additional services you'll find on Zenoss.resmgr only that could
be set to manual.

- zenjserver
- zenpropertymonitor
- zenucsevents
- zenvsphere

You may have more or less services on your system depending on what ZenPacks are
installed. The rule of thumb should be that any services under the *Collection*
tree can be set to manual except for *zenhub*, *MetricShipper*,
*collectorredis*, and *zminion*.
