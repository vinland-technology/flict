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

from flictlib.report import Report
from flictlib.compat_matrix import CompatibilityMatrix
from flictlib.compat_matrix import CompatMatrixStatus
from flictlib.scancode_licenses import ScancodeLicenses
from flictlib.license_groups import LicenseGroups

import sys
from enum import Enum

# Bail out if combinations is greater than...
COMBINATION_THRESHOLD=10000


def error(msg):
    sys.stderr.write(msg + "\n")

class CompatibilityStatus(Enum):
    UNDEFINED=0
    TRUE=1,
    FALSE=2
    DEPENDS=3
    
class Compatibility:

    def __init__(self, matrix_file, scancode_file, group_file, check_all_licenses=False):
        self.compat_matrix = CompatibilityMatrix(matrix_file)
        self.check_all_licenses = check_all_licenses
        if scancode_file != None:
            self.scancode_licenses = ScancodeLicenses(scancode_file)
        else:
            self.scancode_licenses = None
        self.license_groups = LicenseGroups(group_file)

    def supported_licenses(self):
        license_set = set(self.compat_matrix.supported_licenses())
        if self.scancode_licenses != None:
            license_set = license_set.union(self.scancode_licenses.supported_licenses())
        return list(license_set)

    def supported_license_groups(self):
        if self.scancode_licenses != None:
            return list(self.scancode_licenses.supported_license_groups())
        else:
            return []

    def _supported_license(self, lic):
        #print("license: " + str(lic))
        matrix_lic = self.compat_matrix.supported_license(lic)
        #print(" 1 => " + str(matrix_lic))
        if matrix_lic != None:
            return matrix_lic

        if self.scancode_licenses != None:        
            scan_lic = self.scancode_licenses.supported_license(lic)
            #print(" 2 => " + str(scan_lic))
            if scan_lic != None:
                return scan_lic
            
        group_lic = self.license_groups.supported_license(lic)
        #print(" 3 => " + str(group_lic))
        if group_lic != None:
            return group_lic

        #print(" 4 => " + lic)
        return lic

    def _compatibility_status_json(self, status):
        if status == CompatibilityStatus.TRUE:
            return "true"
        elif status == CompatibilityStatus.FALSE:
            return "false"
        elif status == CompatibilityStatus.UNDEFINED:
            return "undefined"
        elif status == CompatibilityStatus.DEPENDS:
            return "depends"
    
    def _a_compatible_with_b(self, a, b):
        """
        wrapper to compat_matrix' method, translates to our enum
        """
        compat = self.compat_matrix.a_compatible_with_b(a, b)
        if compat == CompatMatrixStatus.TRUE:
            return CompatibilityStatus.TRUE
        elif compat == CompatMatrixStatus.FALSE:
            return CompatibilityStatus.FALSE
        elif compat == CompatMatrixStatus.UNDEFINED:
            return CompatibilityStatus.UNDEFINED
        elif compat == CompatMatrixStatus.DEPENDS:
            return CompatibilityStatus.DEPENDS
    
    def check_compatibility(self, license_set, project):
        #print("CC: set: " + str(license_set))
        license_compatibilities=[]
        outbound_suggestions=set()
        if self.check_all_licenses:
            supported = self.supported_licenses()
            if 'Compatibility' in supported:
                supported.remove('Compatibility')
            if 'Copyleft' in supported:
                supported.remove('Copyleft')
            licenses_set = set(list(license_set) + supported)
        else:
            licenses_set = license_set
            
        for license in licenses_set:
            #print("  CC: license: " + str(license))
            license_compatibility={}
            license_compatibility['outbound']=license
            license_compatibility['combinations']=[]
            license_combinations=[]
            if project != None:
                for combination in project.project_combination_list():
                    reason=set()
                    combination_set={}
                    print("  CC: c:" + str((combination)))
                    for p in combination:
                        #print("      CC: p: " + str(p))
                        for lic in p['license']:
                            _license = self._supported_license(license)
                            _lic = self._supported_license(lic)

                            a_b = self._a_compatible_with_b(_license, _lic)

                            if a_b == CompatibilityStatus.TRUE:
                                pass
                            elif a_b == CompatibilityStatus.FALSE:
                                reason.add(license + "\" not compatible with \"" + lic + "\".")       
                            elif a_b == CompatibilityStatus.UNDEFINED:
                                reason.add(license + "\" has undefined compatibility with \"" + lic + "\".")       
                            elif a_b == CompatibilityStatus.DEPENDS:
                                reason.add(license + "\" has dependent compatibility with \"" + lic + "\".")
                                
                    status = len(list(reason))==0
                    print("  CC: c:" + str((combination)) + " ==> "  +str(status) + "    : " + str(reason))
                    if status:
                        outbound_suggestions.add(license)
                        combination_set['combination']=combination
                        combination_set['compatibility_fails']=list(reason)
                        combination_set['compatibility_status']=status
                        #print("CC: z   : " + str(len(reason)) + " ==> " + str(combination_set['compatibility_status']))
                        license_combinations.append(combination_set)
                        license_compatibility['combinations']=license_combinations
            else:
                #print("single....: " + str(license))
                pass
                    
            license_compatibilities.append(license_compatibility)

        license_compatibilities_set={}
        license_compatibilities_set['license_compatibilities']=license_compatibilities
        license_compatibilities_set['outbound_suggestions']=list(outbound_suggestions)
        return license_compatibilities_set

    def check_project_pile(self, project):
        #print("CC: Checking license compat with: " + str(project.name()))
        license_expr = project.license()
        license_set = project.license_set()
        self.compatility_report['license'] = license_expr
        self.compatility_report['license_pile'] = list(license_set)

        print("check_project_pile: " + license_expr)
        print("check_project_pile: " + str(license_set))
        
        # Begin checking compatibility with licenses from all project (incl dps)
        self.compatility_report['compatibilities'] = self.check_compatibility(license_set, project)
        self.valid = True
        
    def check(self, project):

        combinations = project.projects_combinations()

        if combinations < COMBINATION_THRESHOLD:
            return self.check_project_pile(project)
        else:
            error("***ERROR*** maximum amount of combinations reached")
            error("Will use coming method to check compatibility")
            error(" * current number of combinations: " + str(combinations))
            error(" * maximum number of combinations: " + str(COMBINATION_THRESHOLD))
            error(" * coming method has \"complexity\": 2^ " + str(str(project.license_piled_license_check()).count(" OR")+1).strip())
            self.valid = False
            # All licenses in compat object
            # TODO: do we need this?

    def check_compatibilities(self, licenses, check_all=False):
        """
        Check compatbilitiy between all licenses
        """
        #print("check_compatibilities")
        l_fmt = "%-20s"
        compats=[]

        if check_all:
            supported = self.supported_licenses()
            if 'Compatibility' in supported:
                supported.remove('Compatibility')

            # TODO: arrange so we can keep the copylefted licenses
            if 'Copyleft' in supported:
                supported.remove('Copyleft')

            licenses_set = set(licenses + supported)
            outer_licenses = list(licenses_set)
        else:
            outer_licenses = list(licenses)
            #print("outer licenses: " + str(outer_licenses))


        for license_a in outer_licenses:
            #print("check for: " + str(license_a))
            
            result = True
            #lic_str = str(l_fmt) % license_a
            #compatible = True
            inner_licenses=[]
            for license_b in licenses:
                #print(" * : " + str(license_b))
                if license_a == license_b:
                    #print(license_a + " not checked against itself")
                    continue

                # If license not supported by matrix
                # check (and use) if group is available
                lic_a = self._supported_license(license_a)
                lic_b = self._supported_license(license_b)

                comp_left  = self._a_compatible_with_b(lic_a, lic_b)
                comp_right = self._a_compatible_with_b(lic_b, lic_a)

                #print("Compatibility check")
                #print("  compat: " + lic_a + " ? " + lic_b + " => " + str(comp_left))
                #print("  compat: " + lic_b + " ? " + lic_a + " => " + str(comp_right))
                
                inner_compat={}
                inner_compat['license']    = license_b
                inner_compat['compatible_right'] = self._compatibility_status_json(comp_right)
                inner_compat['compatible_left'] = self._compatibility_status_json(comp_left)

                inner_licenses.append(inner_compat)
                


            compat={}
            compat['license']=license_a
            compat['licenses']=inner_licenses
            compats.append(compat)

        compat_object = {}
        compat_object['compatibilities'] = compats
        return compat_object

    def license_group(self, license):
        if self.scancode_licenses != None:
            return self.scancode_licenses.license_group(license)
        return None
        
    def report(self, project):
        self.compatility_report = {}
        self.check(project)
        if not self.valid:
            
            self.compatility_report = None
        return self.compatility_report
    
