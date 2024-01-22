##############################################################################
#
# Copyright (C) Zenoss, Inc. 2018, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

import os

DIFF_DIR = '/home/zenoss/diff/'


class DiffSaver(object):
    """
    Diff saver - saves ZenPack template diff into a file.
    """

    def __init__(self, log):
        self.zpDiffDir = None
        self.log = log

    def initZPDiffDir(self, zp):
        self.zpDiffDir = '{}{}/'.format(DIFF_DIR, zp.id)
        if os.path.isdir(self.zpDiffDir):
            old_diffs = os.listdir(self.zpDiffDir)
            for f in old_diffs:
                os.remove('{}/{}'.format(self.zpDiffDir, f))
        else:
            os.makedirs(self.zpDiffDir)

    def saveDiff(self, zp, parent, spec, id, diff):
        diffFile = '{}{}.diff'.format(self.zpDiffDir, id)
        self.log.info("Existing object {}/{} differs from "
                 "the newer version included with the {} ZenPack.  "
                 "The existing object will be "
                 "backed up to '{}'. Please review and reconcile any "
                 "local changes before deleting the backup".format(
                 parent.getDmdKey(), spec.name, zp.id, os.path.abspath(diffFile)))
        f = open(diffFile, 'w')
        f.write(diff)
        f.close()

    def remEmptyDir(self):
        if not os.listdir(self.zpDiffDir):
            os.rmdir(self.zpDiffDir)
