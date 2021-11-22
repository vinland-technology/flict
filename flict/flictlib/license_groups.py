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


class LicenseGroups:
    def __init__(self, group_file):
        self.group_file = group_file
        self.supported_groups = ["Permissive",
                                 "Public Domain", "Copyleft", "Proprietary"]

        self.group_object = None
        with open(group_file) as fp:
            self.group_object = json.load(fp)
            self.license_groups = self.group_object['license_groups']

    def license_group(self, license):

        for group in self.supported_groups:
            #print("license: " + str(license))
            #print(" * group:      " + str(group))
            #print(" * licenes:    " + str(self.license_groups[group]))
            #print("key:     " + str(self.license_key_map[group]))
            if license in self.license_groups[group]:
                #print(" - found")
                for _ in self.license_groups[group]:
                    return group

    def supported_license_groups(self):
        return self.license_groups

    def supported_licenses_per_group(self, group):
        #print("group: " + str(group))
        #print("group: " + str(self.license_groups))
        #print("type:  " + str(type(self.license_groups)))
        #print("lice:  " + str(self.license_groups[group]))
        return self.license_groups[group]

    def supported_license(self, license):
        for group in self.supported_groups:
            #print("checking: " + group)
            group_list = self.license_groups[group]
            if license in group_list:
                return group
        return None

    def supported_licenses(self):
        return [self.supported_licenses_per_group(group)
                for group in self.supported_groups]

    def meta_data(self):
        return self.scancode_object['meta_data']
