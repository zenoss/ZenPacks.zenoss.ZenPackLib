##############################################################################
#
# Copyright (C) Zenoss, Inc. 2016, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################
import logging
import sys

def new_log(id):
    '''create and return a new log file'''
    log = logging.getLogger(id)
    # Suppresses "No handlers could be found for logger" errors if logging
    # hasn't been configured.
    if len(log.handlers) == 0:
        log.addHandler(logging.NullHandler())

    if not [x for x in log.handlers if not isinstance(x, logging.NullHandler)]:
        # Logging has not been initialized yet- LOG.error may not be
        # seen.
        logging.basicConfig()
    return log

DEFAULTLOG = new_log('zpl.zenpacklib')


class ZenPackLibLog(object):
    ''''''
    zenpacks = {}
    defaultlog = DEFAULTLOG

    def get_log(self, id):
        if id in self.zenpacks.keys():
            log = self.zenpacks.get(id).get('log')
            return log
        return self.defaultlog

    def add_log(self, id, quiet=True, level=0):
        '''add a new log'''
        id = str(id)
        if id not in self.zenpacks.keys():
            log = new_log(id)
            log.setLevel(level)
            # set to error if quiet is True (default)
            log.setLevel('ERROR' if quiet else level)
            self.zenpacks[id] = {'log': log, 'quiet': quiet, 'level':level}
        else:
            log = self.get_log(id)
        return log

    @classmethod
    def enable_log_stderr(cls, log):
        """
            Enable logging to stderr 
        """
        log.propagate = False
        h = logging.StreamHandler(sys.stderr)
        h.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(name)s: %(message)s'))
        log.addHandler(h)

    @classmethod
    def enable_log_stdout(cls, log):
        """
            Enable logging to stderr 
        """
        log.propagate = False
        h = logging.StreamHandler(sys.stdout)
        h.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(name)s: %(message)s'))
        log.addHandler(h)

ZPLOG = ZenPackLibLog()
