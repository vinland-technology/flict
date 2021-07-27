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
       
    def format_outbound_license(self, suggested_outbounds):
        return json.dumps(suggested_outbounds)
        
    def format_license_combinations(self, combinations):
        return json.dumps(combinations)

    def format_compats(self, compats):
        return json.dumps(compats)
    
