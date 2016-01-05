**********
SNMP Tools
**********

To configure Zenoss to monitor a device using SNMP, it is necessary to
understand a bit about SNMP and the specific capabilities of your device. This
section will walk you through using Net-SNMP_, smidump_, and snmpsim_ to learn
about SNMP and your device.

.. _Net-SNMP: http://www.net-snmp.org/
.. _smidump: https://www.ibr.cs.tu-bs.de/projects/libsmi/smidump.html
.. _snmpsim: http://snmpsim.sourceforge.net/


Installing Net-SNMP
===================

In the SNMP world the client is referred to as a *manager* and the server is
referred to as the *agent*. Net-SNMP is software that provides both an *agent*
that's used in all sorts of devices, and many command line tools that act as
*manager*. We're only going to need the command line tools, so we'll be
installing the *net-snmp-utils* package.

You can install Net-SNMP's command line tools by running the following command
as root.

.. code-block:: bash

    yum -y install net-snmp-utils

Installing libsmi
=================

``smidump`` is a useful command line tool for converting MIBs to other formats.
We'll be using it later in this tutorial to research what a MIB provides.

Install *smidump* by installing the *libsmi* package with the following command.

.. code-block:: bash

    yum -y install libsmi

Installing the SNMP Simulator
=============================

When developing a ZenPack to monitor an SNMP-enabled device it can often be
useful to simulate the device's SNMP agent. There are many tools available to do
this. For this guide we will be using the free snmpsim_ because it's easy to
install on our Zenoss host.

1. Run the following commands as root to install *snmpsim*:

   .. code-block:: bash

      yum -y groupinstall "Development Tools"
      yum -y install python-devel
      easy_install snmpsim
      mkdir -p /usr/share/snmpsim/data
      mkdir -p /var/run/snmpsim
      useradd -U snmpsim
      chown snmpsim:snmpsim /var/run/snmpsim

2. Run the following command as root to install a NetBotz recording.

   .. code-block:: bash

      wget https://goo.gl/OJe2vL -O /usr/share/snmpsim/data/public.snmprec

3. Run the following command as root to run snmpsim.

   .. code-block:: bash

      snmpsimd.py \
        --process-user=snmpsim \
        --process-group=snmpsim \
        --agent-udpv4-endpoint=172.17.42.1:161 \
        --daemonize

4. Test the simulator with the following *snmpwalk* command.

   .. code-block:: bash

      snmpwalk -v2c -c public 172.17.42.1 sysDescr

   You should see the following output.

   .. code-block:: text

       SNMPv2-MIB::sysDescr.0 = STRING: Linux Netbotz01 2.4.26 #1 Wed Oct 31 18:09:53 CDT 2007 ppc

.. _SNMPoster: https://github.com/cluther/snmposter#readme

Using snmpwalk
==============

The tool you'll be using most often is called *snmpwalk*. All SNMP values are
arranged on a tree, and snmpwalk allows you to query for all data under a given
branch of that tree. See the following example that walks all values under the
*system* branch.

Run the snmpwalk command.

.. code-block:: bash

    snmpwalk -v2c -c public 172.17.42.1 system

.. code-block:: text

    SNMPv2-MIB::sysDescr.0 = STRING: Linux Netbotz01 2.4.26 #1 Wed Oct 31 18:09:53 CDT 2007 ppc
    SNMPv2-MIB::sysObjectID.0 = OID: SNMPv2-SMI::enterprises.5528.100.20.10.2006
    DISMAN-EVENT-MIB::sysUpTimeInstance = Timeticks: (7275488) 20:12:34.88
    SNMPv2-MIB::sysContact.0 = STRING: unknown
    SNMPv2-MIB::sysName.0 = STRING: Netbotz01
    SNMPv2-MIB::sysLocation.0 = STRING: Z1 Rack02 NetBotz01

We can see that this NetBotz device seems to be based on Linux and that we have
some more-or-less useful information about the device's name, location and
administrative contact.

The second line with the *sysObjectID* has an unusual value. It's a partially
decoded OID. It isn't decoded enough for us to know what it means. SNMP tools
including Net-SNMP use MIB files to decode these OIDs into human readable
values. In fact, we're only able to read most of the output above because Net-
SNMP has a set of standard MIBs enabled by default.

Let's run that command again, but use the ``-On`` flag to tell snmpwalk not to
decode OIDs.

.. code-block:: bash

    snmpwalk -v2c -c public -On 172.17.42.1 system

.. code-block:: text

    .1.3.6.1.2.1.1.1.0 = STRING: Linux Netbotz01 2.4.26 #1 Wed Oct 31 18:09:53 CDT 2007 ppc
    .1.3.6.1.2.1.1.2.0 = OID: .1.3.6.1.4.1.5528.100.20.10.2006
    .1.3.6.1.2.1.1.3.0 = Timeticks: (7275488) 20:12:34.88
    .1.3.6.1.2.1.1.4.0 = STRING: unknown
    .1.3.6.1.2.1.1.5.0 = STRING: Netbotz01
    .1.3.6.1.2.1.1.6.0 = STRING: Z1 Rack02 NetBotz01


While this data is mostly less valuable than the decoded version above, it's
more useful for a single reason. We can take that
``.1.3.6.1.4.1.5528.100.20.10.2006`` value and search the Internet for it. It's
best to remove the leading ``.`` and search for
``1.3.6.1.4.1.5528.100.20.10.2006`` instead. This should lead you to the *NETBOTZV2-MIB* which will contain the decoding
information we need to learn more about this device.

Run the following command to download `NETBOTZV2-MIB.mib` into
`/usr/share/snmp/mibs/`.

.. code-block:: bash

    wget https://goo.gl/0v4Kti -O /usr/share/snmp/mibs/NETBOTZV2-MIB.mib

Now we can run the original snmpwalk command again with the addition of the
``-m all`` option. This option tells Net-SNMP tools to use all MIBs.

.. code-block:: bash

    snmpwalk -v2c -c public -m all 172.17.42.1 system

.. code-block:: text

    SNMPv2-MIB::sysDescr.0 = STRING: Linux Netbotz01 2.4.26 #1 Wed Oct 31 18:09:53 CDT 2007 ppc
    SNMPv2-MIB::sysObjectID.0 = OID: NETBOTZV2-MIB::netBotz420ERack
    DISMAN-EVENT-MIB::sysUpTimeInstance = Timeticks: (7275488) 20:12:34.88
    SNMPv2-MIB::sysContact.0 = STRING: unknown
    SNMPv2-MIB::sysName.0 = STRING: Netbotz01
    SNMPv2-MIB::sysLocation.0 = STRING: Z1 Rack02 NetBotz01

Now we can see that the sysObjectID is NETBOTZV2-MIB::netBotz420ERack. This
gives us a better idea of exactly what kind of device it is. We'll see that as
we look deeper into this device that the NETBOTZV2-MIB will prove more useful.

Default Net-SNMP Options
========================

The snmpwalk usage showed three primary command line options that we tend to use
most of the time. Net-SNMP allows you to specify these in a configuration file
so you don't have to type them every time. I recommend doing this.

Create ``/etc/snmp/snmp.conf`` and add the following lines.

.. code-block:: text

    defVersion v2c
    defCommunity public
    mibs ALL

These lines add the following equivalent command line options respectively:

- `-v2c`
- `-c public`
- `-m all`

So now we can run this command.

.. code-block:: bash

    snmpwalk 172.17.42.1 sysObjectID

And get the same results as if we ran.

.. code-block:: bash

    snmpwalk -v2c -c public -m all 172.17.42.1 sysObjectID

This will save you time while developing this ZenPack, and others in the future.

Decoding and Encoding OIDs
==========================

Often it can be useful to turn numeric OIDs into their human-readable
equivalent, or vice-versa. The *snmptranslate* command can be used for this. See
the following examples.

OID to name:

.. code-block:: bash

    # snmptranslate .1.3.6.1.4.1.5528.100.20.10.2006
    NETBOTZV2-MIB::netBotz420ERack

Name to OID:

.. code-block:: bash

    # snmptranslate -On NETBOTZV2-MIB::netBotz420ERack
    .1.3.6.1.4.1.5528.100.20.10.2006
