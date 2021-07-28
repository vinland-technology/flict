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

class TextFormatter(FormatInterface):

    def format_support_licenses(self, compatibility):
        supported_licenses = compatibility.supported_licenses()
        
        ret_str = ""
        for item in supported_licenses:
            lic_group = compatibility.license_group(item)
            if lic_group is not None:
                ret_str += " " + str(item) + ": (" + lic_group + ")\n"
            else:
                ret_str += " " + str(item) + "\n"
        return ret_str

    def format_license_list(self, license_list):
        return "text implmentation | format_license_list(): " + str(license_list)
        
    def format_report(self, report):
        return "text implmentation | format_report(): " + str(report)

    def format_license_combinations(self, project):
        return str(project.projects_combinations())

    def format_outbound_license(self, suggested_outbounds):
        ret_str = None
        
        for ol in suggested_outbounds:
            if ret_str == None:
                ret_str = ol
            else:
                ret_str += ", " + ol
        return ret_str
    
    def format_supported_license_groups(self, license_groups):
        ret_str = ""
        for lg in license_groups:
            ret_str += " " + str(lg)
            if lg == "Permissive" or lg == "Public Domain":
                pass
            else:
                ret_str += " (under consideration)"
            ret_str += "\n"
        return ret_str
