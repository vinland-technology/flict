#!/usr/bin/python3

###################################################################
#
# flict - FOSS License Compatibility Tool
#
# SPDX-FileCopyrightText: 2020 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later
#
###################################################################

#
# This file contains functionality to classify licenses not considered
# as misspelling but easily identified as belonging to a group (e.g. Permissive)
#
# The same groups as provided by Scancode (see scancode_licenses.py) will be used
#


import json
from flict.flictlib import logger


class LicenseGroups:
    def __init__(self, group_file):
        self.group_file = group_file
        self.license_groups = ["Permissive",
                               "Public Domain", "Copyleft", "Proprietary"]

        self.group_object = None
        with open(group_file) as fp:
            self.group_object = json.load(fp)
            self._groupify()
            self.license_groups = self.scancode_object['license_groups']

    def license_group(self, license):

        for group in self.license_groups:
            #print("license: " + str(license))
            #print(" * group:   " + str(group))
            #print("spdx:    " + str(self.license_spdx_map[group]))
            #print("key:     " + str(self.license_key_map[group]))
            if license.lower() in group:
                logger.main_logger.debug(" - found")
                for _ in self.license_groups[group]:
                    return group

    def supported_license_groups(self):
        return self.license_groups

    def supported_licenses_per_group(self, group):
        return self.license_groups[group]['licenses']

    def supported_licenses(self):
        supported_list = []
        for group in self.license_groups:
            supported_list = supported_list + \
                self.supported_licenses_per_group(group)
        return supported_list

    def meta_data(self):
        return self.scancode_object['meta_data']
