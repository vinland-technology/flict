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

    def format_license_group(self, compatibility, license_handler, license_group, extended_licenses):
        license_list = license_handler.license_expression_list(license_group,
                                                               extended_licenses)
        ret_str = ""
        for lic in license_list.set_list:
            for inner_lic in lic:
                lic_group = compatibility.license_group(inner_lic)
                if lic_group is not None:
                    ret_str += inner_lic + ": " + str(lic_group)
                else:
                    ret_str += inner_lic + ": does not belong to a group. It may still be supported by OSADL's matrix"
        return ret_str
    
    def format_simplified(self, license_expression, simplified):
        return simplified

    def format_verified_license(self, license_expression, suggested_outbounds):
        ret_str = "The licenses in the expression \"" + license_expression + "\" are"
        if len(suggested_outbounds) == 0:
            ret_str += " not"
        ret_str += " compatible.\n"
        if len(suggested_outbounds) == 0:
            ret_str += "No outbound license could be suggested due to license incompatibility."
        else:
            ret_str += "Suggested outbound licenses: "
            lic = None
            for s in suggested_outbounds:
                if lic == None:
                    lic = s
                else:
                    lic += ", " + s
            ret_str += lic + "\n"
            ret_str += "NOTE: the suggested outbounds need to be manually reviewed."
        return ret_str
