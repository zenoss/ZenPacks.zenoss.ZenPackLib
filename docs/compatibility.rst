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

==================  ==============
zenpacklib Version  Zenoss Version
==================  ==============
1.0                 4.1
                    4.2
                    5.0
==================  ==============

Compatibility only considers <major>.<minor> versions of both zenpacklib and
Zenoss. Maintenance or patch releases of each are always considered compatible.

