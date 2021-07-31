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

from flict.flictlib.format.format import FormatInterface

import json

class JsonFormatter(FormatInterface):

    def format_support_licenses(self, compatibility):
        supported_licenses = compatibility.supported_licenses()
        return json.dumps(compatibility.supported_licenses())

    def format_license_list(self, license_list):
        return json.dumps(license_list)

    def format_report(self, report):
        return json.dumps(report.report())
 
    def format_license_combinations(self, project):
        combinations = project.projects_combinations()
        comb = {}
        comb['license_combinations'] = combinations
        return json.dumps(comb)
       
    def format_outbound_license(self, outbound_candidate):
        return json.dumps(outbound_candidate)
        
    def format_compats(self, compats):
        return json.dumps(compats)
    
    def format_supported_license_groups(self, license_groups):
        return json.dumps(license_groups)

    def format_license_group(self, compatibility, license_handler, license_group, extended_licenses):
        license_list = license_handler.license_expression_list(license_group,
                                                               extended_licenses)
        lg = []
        for lic in license_list.set_list:
            for inner_lic in lic:
                lic_group = compatibility.license_group(inner_lic)
                if lic_group is not None:
                    item = { inner_lic: lic_group,
                             'status': True }
                    lg.append( item ) 
                else:
                    item = { inner_lic: lic_group,
                             'status': False,
                             'msg': inner_lic + ": does not belong to a group. It may still be supported by OSADL's matrix" } 
                    lg.append(item)
        return json.dumps(lg)

    def format_simplified(self, license_expression, simplified):
        return json.dumps( { 'original':  license_expression,
                             'simplified': simplified } )

    def format_verified_license(self, license_expression, outbound_candidate):
        compat = len(outbound_candidate) != 0
        return json.dumps( { "license_expression": license_expression,
                            "compatible": compat,
                            "outbound_candidate": outbound_candidate }
        )
