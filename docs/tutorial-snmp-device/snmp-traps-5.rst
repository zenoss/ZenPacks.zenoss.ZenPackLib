**********
SNMP Traps
**********

This section covers how to handle SNMP traps.

Zenoss will accept SNMP traps from your devices as soon as you configure those
devices to send traps to your Zenoss server. The `zentrap` daemon will listen to
the standard SNMP trap port of `162/udp` and create an event for every trap that
it receives.

However, without you giving Zenoss more information about the contents of those
traps, the events will contain numeric OIDs and be nearly impossible for a human
to decipher.

Importing MIBs
==============

Let's import the `NETBOTZV2-MIB` that we've been working with through these
examples.

1. Copy the MIB to */z* so containers can read it.

   .. code-block:: bash

       cp /usr/share/snmp/mibs/NETBOTZV2-MIB.mib /z

2. Import the MIB file.

   .. code-block:: bash

       zenmib run --keepMiddleZeros NETBOTZV2-MIB.mib

   From which we should get the following output::

       Found 1 MIBs to import.
       Unable to find a file that defines SNMPv2-SMI
       Unable to find a file that defines SNMPv2-TC
       Parsed 214 nodes and 256 notifications from NETBOTZV2-MIB
       Loaded MIB NETBOTZV2-MIB into the DMD
       Loaded 1 MIB file(s)

3. Add the imported MIB to the NetBotz ZenPack.

   1. Navigate to *Advanced* -> *MIBs* in the web interface.
   2. Select `NETBOTZV2-MIB`.
   3. Choose *Add to ZenPack* from the gear menu at the bottom of the list.
   4. Choose the *ZenPacks.training.NetBotz* then click *SUBMIT*.


Simulating SNMP Traps
=====================

To more easily configure and test Zenoss' trap handling, it's useful to know
how to simulate SNMP traps. The alternative is breaking your real devices in
various ways and hoping to be able to get the device to send all of the traps
you need. This isn't always possible.

Let's start by picking an SNMP trap to simulate.

1. Navigate to *Advanced* -> *MIBs* in the web interface.

2. Choose *NETBOTZV2-MIB* from the list of MIBs.

3. Choose *Traps* from the drop-down box in the middle of the right panel.

4. Choose *netBotzTempTooHigh* in the list of traps.

We'll now see information about this trap in the bottom-right panel. The first
thing to note is the OID. This is all we need to get started.

Send a Simple Trap
------------------

Use the following steps to get your feet wet sending a basic trap.

1. Make sure the `zentrap` service is running.

   If you have stopped the zentrap service, or if you have it configured to
   manual launch mode, you will need to start it.

   .. code-block:: bash

      serviced service start zentrap

2. Identify the IP address to which traps should be sent to get to zentrap.

   serviced does performs port forwarding on the serviced host to route
   received SNMP traps to the zentrap container. We're going to be sending
   simulated SNMP traps from the serviced host, and will need to know what
   address to send traps to so they're received by zentrap.

   Run the following command to find the address.

   .. code-block:: bash

      sudo iptables -L FORWARD -n | grep 162

   This will output something very close to the following:

   .. code-block:: plain

      ACCEPT     udp  --  0.0.0.0/0            172.17.0.29          udp dpt:162

   We'll be sending traps to that 172.17.0.29 address. It may be different on
   your system.

3. Send an SNMP trap.

   Run the following `snmptrap` command on the serviced host.

   .. code-block:: bash

      sudo snmptrap 172.17.0.29 0 NETBOTZV2-MIB::netBotzTempTooHigh

4. Find this netBotzTempTooHigh event in web interface's event console.

   Double-click the "snmp trap netBotzTempTooHigh" event in the event console to
   see its details. Look for the following details.

   * eventClassKey: This should be netBotzTempTooHigh as decoded using the MIB.
   * oid: This is the original undecoded OID.

Send a Full Trap
----------------

Now that we've proved out a simple trap, we should add variable bindings or
*varbinds* to the trap. If you look at the *netBotzTempTooHigh* trap in the
Zenoss web interface's MIB explorer again, you'll see that there's an extensive
list of *Objects* associated with the trap definition. These are variable
bindings.

A variable binding allows the device sending the SNMP trap to attach additional
information to the trap. In this example, one of the variable bindings for the
*netBotzTempTooHigh* trap is *netBotzV2TrapSensorID*. This will give us a way to
know which one of the sensors has exceeded it's high temperature threshold.

1. Run the following `snmptrap` command.

   .. code-block:: bash

      sudo snmptrap 172.17.0.29 0 NETBOTZV2-MIB::netBotzTempTooHigh \
          NETBOTZV2-MIB::netBotzV2TrapSensorID s 'nbHawkEnc_1_TEMP1'

   As you can see, this `zentrap` command starts exactly the same as in the
   example. We then add the following three fields.

   1. ``NETBOTZV2-MIB::netBotzV2TrapSensorID`` (OID)
   2. ``s`` (type)
   3. ``'nbHawkEnc_1_TEMP1'`` (value)

   We can continue to add sets of these three parameters to add as many other
   variable bindings to the trap as we want.

   Note that the only difference between this event and the simple event is the
   addition of the `netBotzV2TrapSensorID` field. So now you see how Zenoss take
   the name/value pairs that are the SNMP trap's variable bindings and turn them
   into name/value pairs within the resulting event.

Mapping SNMP Trap Events
========================

Now that we're able to create SNMP traps anytime we want, it's time to use
Zenoss' event mapping system to make them more useful. The most important field
on an incoming event when it comes to mapping is the `eventClassKey` field.
Fortunately for us, SNMP traps get that great `eventClassKey` set that gives us
a big head start.

1. Map the event.

   1. Navigate to *Events* in the web interface.

   2. Select the *netBotzTempTooHigh* event you just created.

   3. Click the toolbar button that looks like a hierarchy. If you hover over it,
      the tooltip will say *Reclassify an event*.

   4. Choose the */Environ* event class then click *SUBMIT*

      Now the next time a *netBotzTempTooHigh* trap is received it will be put
      into the */Environ* event class instead of */Unknown*.

2. Enrich the event.

   1. Click the *Go to new mapping* link to navigate to the new mapping.

   2. Click *Edit* in the left navigation pane.

   3. Set *Transform* to the following:

      .. code-block:: python

         evt.component = getattr(evt, 'netBotzV2TrapSensorID', '')

      This will use the name of the sensor as described by the
      `netBotzV2TrapSensorID` variable binding as the event's `component`
      field.

There are endless possibilities of what you could do within the transform for
this event and others. This is just one practical example.
