#!/usr/bin/env python3

###################################################################
#
# flict - FOSS License Compatibility Tool
#
# SPDX-FileCopyrightText: 2021 Henrik Sandklef, 2021 Konrad Weihmann
#
# SPDX-License-Identifier: GPL-3.0-or-later
#
###################################################################

from flict.flictlib.format.format import FlictFormatter


class TextFormatter(FlictFormatter):

    def __init__(self):
        self.col_size = 18

    def format_support_licenses(self, supported_licenses):
        ret_str = ""
        for item in supported_licenses:
            ret_str += " " + str(item) + "\n"
        return ret_str

    def format_license_list(self, license_list):
        return "text implmentation | format_license_list(): " + str(license_list)

    def format_license_combinations(self, project):
        return str(project.projects_combinations())

    def format_outbound_license(self, outbound_candidates):
        return ", ".join(outbound_candidates)

    def format_simplified(self, license_expression, simplified):
        return simplified['simplified']

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

    def _format_lic(self, lic):
        str_size = f'{0: <{self.col_size}}'
        return str_size.format(lic)[:self.col_size - 1] + " "

    def _format_line(self):
        return self._format_lic("-" * (self.col_size - 1))

    def _format_compats_licenses(self, compats, license_list):
        ret = []
        for lic in license_list:
            inner = []
            inner.append(self._format_lic(lic + ": "))
            compat = self.find_compat(compats, lic)
            for inner_lic in license_list:
                if inner_lic == lic:
                    lic_compat = "Yes"
                else:
                    lic_compat = self.find_license_compat(compat, inner_lic)
                inner.append(self._format_lic(lic_compat))
            ret.append("".join(inner))
        return ret

    def format_compats(self, compats):
        licenses = set()
        for compat in compats['compatibilities']:
            licenses.add(compat["license"])
        license_list = list(licenses)
        license_list.sort()

        ret = []

        inner = []
        inner.append(self._format_lic(""))
        for lic in license_list:
            inner.append(self._format_lic(lic))
        ret.append("".join(inner))

        ret.append("".join(self._format_line()))

        ret += self._format_compats_licenses(compats, license_list)

        return "\n".join(ret)

    def format_compatibilities(self, compats):
        compatible = compats['compatibility'] == "Yes"
        allowed = compats['allowed']
        return "Yes" if compatible and allowed else "No"

