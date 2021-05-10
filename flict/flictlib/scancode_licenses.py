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
# This file contains functionality to reuse (no pun intended with the
# tool reuse) the work done by NexB:
# https://scancode-licensedb.aboutcode.org/
#


import json
import os
import sys

VERBOSE=False


def error(msg):
    sys.stderr.write(msg + "\n")

def verbose(msg):
    global VERBOSE
    if VERBOSE:
        sys.stderr.write(msg)
        sys.stderr.write("\n")
        sys.stderr.flush()

def verbosen(msg):
    global VERBOSE
    if VERBOSE:
        sys.stderr.write(msg)
        sys.stderr.flush()

class ScancodeLicenses:
    def __init__(self, scancode_file):
        self.scancode_file = scancode_file
        self.supported_groups = [ "Permissive", "Public Domain", "Copyleft" ]

        self.scancode_object = None
        with open(scancode_file) as fp:
            self.scancode_object = json.load(fp)
            self._groupify()
            self.license_objects = self.scancode_object['scancode_licenses']

    def _groupify(self):
        self.license_key_map = {}
        self.license_spdx_map = {}
        for lic_obj in self.scancode_object['scancode_licenses']:
            #print("obj: " + str(lic_obj))
            group = lic_obj['group']
            lic_key = lic_obj['key']
            lic_spdx = lic_obj['spdx']
            if not group in self.license_key_map:
                self.license_key_map[group]=[]
            if not group in self.license_spdx_map:
                self.license_spdx_map[group]=[]
            self.license_key_map[group].append(lic_key)
            if lic_spdx != None and lic_spdx != "":
                self.license_spdx_map[group].append(lic_spdx)

    def license_group(self, license):
        
        for group in self.supported_groups:
            #print("license: " + str(license))
            #print(" * group:   " + str(group))
            #print("spdx:    " + str(self.license_spdx_map[group]))
            #print("key:     " + str(self.license_key_map[group]))
            if license.lower() in self.license_key_map[group] or license in self.license_spdx_map[group]:
                #print(" - found")
                for lic_obj in self.license_objects:
                    #print("check : " + lic_obj['spdx']) 
                    if lic_obj['spdx'] == license:
                        return lic_obj['group']
                    if lic_obj['key'] == license.lower():
                        return lic_obj['group']
    
    def supported_license_groups(self):
        return self.license_key_map.keys()
    
    def supported_licenses_per_group(self, group):
        return self.license_key_map[group]
    
    def supported_license(self, license):
        for group in self.supported_groups:
            #print("group: " + str(group))
            if license in self.license_spdx_map[group]:
                return group
            if license in self.license_key_map[group]:
                return group
        return None
        
    def supported_licenses(self):
        supported_list = []
        for group in self.supported_groups:
            supported_list = supported_list + self.supported_licenses_per_group(group) 
        return supported_list
    
    def original_data_info(self):
        return self.scancode_object['original_data']

    def meta_data(self):
        return self.scancode_object['meta_data']
    
