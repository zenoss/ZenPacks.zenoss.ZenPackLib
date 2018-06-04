#! /usr/bin/python
##############################################################################
#
# Copyright (C) Zenoss, Inc. 2017, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

"""
This script is a YAML splitter for monolithic ZPL configuration files.
It does not use any YAML intelligence, but works on a brute pattern basis.


It will:

  * Separate top-level sections into device.yaml
  * Separate device-class sections into dc_Name.yaml sections
  * Separate event-class sections into ec_Name.yaml sections
  * Places all files in /tmp/zpl

WARNING: Make sure to carefully inspect the resulting files to ensure freshness!
"""

import os
import sys
import re

re_group = re.compile('^  /([\w/]*)')


class Splitter(object):
    global writing

    def __init__(self, filename):

        self.output_dir = '/tmp/zpl'
        if not os.path.isdir(self.output_dir):
            os.makedirs(self.output_dir)

        self.device_classes = False
        self.event_classes = False
        self.zp_top = False
        self.writing = False
        self.filename = filename
        self.tfile = None

    def set_all_false(self):
        self.device_classes = False
        self.event_classes = False
        self.zp_top = False
        self.writing = False

    def switch_file(self, match, cls_type):
        """
        cls_type is one of ('dc', 'ec')
        """
        names = match.group(1).split('/')
        names.insert(0, cls_type) # Prepend the cls_type to filename
        temp_file_name = '_'.join(names) + '.yaml'

        print temp_file_name
        temp = os.path.join(self.output_dir, temp_file_name)
        if not self.writing:
            self.writing = True
            self.tfile = open(temp, 'w')

        elif self.tfile:
            self.tfile.close()
            self.tfile = open(temp, 'w')
        else:
            print "Error: You should either be dormat at BOL or writing"
            sys.exit()

    def split(self):
        zp_top = False
        with open(self.filename) as bigfile:
            for line in bigfile:

                if line.startswith('device_classes:'):
                    self.set_all_false()
                    self.device_classes = True
                    continue

                elif line.startswith('event_classes:'):
                    self.set_all_false()
                    self.event_classes = True
                    continue

                elif line.startswith('name: ZenPacks'):
                    self.set_all_false()
                    zp_top = True
                    zp_name = line
                    continue

                match = re_group.match(line) # Matches dc and ec classes by /Class/Name
                if match and self.device_classes:
                    self.switch_file(match, 'dc')
                    self.tfile.write('device_classes:\n')

                elif match and self.event_classes:
                    self.switch_file(match, 'ec')
                    self.tfile.write('event_classes:\n')

                elif zp_top:
                    temp_file_name = 'device.yaml'
                    print temp_file_name
                    temp = os.path.join(self.output_dir, temp_file_name)
                    self.tfile = open(temp, 'w')
                    self.tfile.write(zp_name) # Write the name: line
                    writing = True
                    zp_top = False

                if writing:
                    self.tfile.write(line)

            self.tfile.close()

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print "Provide Filename"
    else:
        filename = sys.argv[1]
        splitter = Splitter(filename)
        splitter.split()
