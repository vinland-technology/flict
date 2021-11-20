#!/usr/bin/python3

###################################################################
#
# flict - FOSS License Compatibility Tool
#
# SPDX-FileCopyrightText: 2021 Henrik Sandklef, 2021 Konrad Weihmann
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

    def format_outbound_license(self, outbound_candidate):
        return ", ".join(outbound_candidate)

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
                    ret_str += inner_lic + \
                        ": does not belong to a group. It may still be supported by OSADL's matrix"
        return ret_str

    def format_simplified(self, license_expression, simplified):
        return simplified

    def format_verified_license(self, license_expression, outbound_candidate):
        ret_str = "The licenses in the expression \"" + license_expression.strip() + \
            "\" are"
        if len(outbound_candidate) == 0:
            ret_str += " not"
        ret_str += " compatible.\n"
        if len(outbound_candidate) == 0:
            ret_str += "No outbound license candidate could be identified due to license incompatibility."
        else:
            ret_str += "Outbound license candidates: "
            ret_str += ", ".join(outbound_candidate) + "\n"
            ret_str += "NOTE: the suggested outbound candidate licenses need to be manually reviewed."
        return ret_str

    def format_relicense_information(self, license_handler):
        ret = ["{lic} --> {later}".format(lic=rel.get('spdx', 'NOASSERTATION'), later=", ".join(rel.get('later', [])))
               for rel in license_handler.relicensing_information().get('original', {}).get('relicense_definitions', [])]
        return "\n".join(ret)

    def format_translation_information(self, license_handler):
        ret = []
        for transl_list in license_handler.translation_information():
            for transl in transl_list:
                ret.append(f"{transl} <--- {str(transl_list[transl])}")
        return "\n".join(ret)

    def format_policy_report(self, policy_report):
        outbounds = policy_report.get("policy_outbounds")
        ret_str = "Status: "
        policy_result = outbounds.get("policy_result")
        if policy_result == 0:
            ret_str += "OK"
        elif policy_result == 1:
            ret_str += "OK, with licenses to avoid"
        elif policy_result == 2:
            ret_str += "Failed identifying outbound license"
        ret_str += "\n"
        ret_str += "Allowed (suggested) outbound licenses: " + str(outbounds.get("allowed", "")) + "\n"
        ret_str += "Avoided (suggested) outbound licenses: " + str(outbounds.get("avoid", "")) + "\n"
        ret_str += "Denied (suggested) outbound licenses: " + str(outbounds.get("denied", ""))
        return ret_str
