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

from flict.flictlib.format.format import FormatInterface
from flict.flictlib.format.common import compat_interprets
from flict.flictlib.format.text_format import TextFormatter


class MarkdownFormatter(FormatInterface):

    def format_support_licenses(self, compatibility):
        return None

    def format_license_list(self, license_list):
        return None

    def format_report(self, report):
        return None

    def format_license_porject(self, project):
        return None

    def format_outbound_license(self, suggested_outbounds):
        return None

    def format_license_combinations(self, combinations):
        return None

    def format_compats(self, compats):
        return output_compat_markdown(compats)

    def format_relicense_information(self, license_handler):
        return "# Translation information\n" + TextFormatter.format_relicense_information(license_handler)

    def format_translation_information(self, license_handler):
        return "# Translation information\n" + TextFormatter.format_translation_information(license_handler)

    def format_policy_report(self, policy_report):
        outbounds = policy_report.get("policy_outbounds")
        meta = policy_report.get("meta")
        ret_str = "# Policy report\n\n"
        ret_str += "## About\n\n"
        ret_str += "* date: " + meta.get("start") + "\n\n"
        ret_str += "* user: " + meta.get("user") + "\n\n"
        policy_result = outbounds.get("policy_result")
        ret_str += "## Result\n\n"
        ret_str += "Policy result: "
        if policy_result == 0:
            ret_str += "OK"
        elif policy_result == 1:
            ret_str += "OK, with licenses to avoid"
        elif policy_result == 2:
            ret_str += "Failed identifying outbound license"
        ret_str += "\n\n"
        ret_str += "## Suggested outbound licenses \n\n"
        ret_str += "### Allowed\n\n"
        for lic in outbounds.get("allowed"):
            ret_str += " * " + lic + "\n"
        ret_str += "\n\n"
        ret_str += "### Avoided\n\n"
        for lic in outbounds.get("avoided"):
            ret_str += " * " + lic + "\n"
        ret_str += "\n\n"
        ret_str += "### Denied\n\n"
        for lic in outbounds.get("denied"):
            ret_str += " * " + lic + "\n"

        return ret_str


def _compat_to_fmt(comp_left, comp_right, fmt):
    left = compat_interprets['left'][comp_left][fmt]
    right = compat_interprets['right'][comp_right][fmt]
    return str(right) + str(left)


def _compat_to_markdown(left, comp_left, right, comp_right):
    return _compat_to_fmt(comp_left, comp_right, "markdown")


def output_compat_markdown(compats):
    # print(str(compats))
    result = "# License compatibilities\n\n"

    result += "# Licenses\n\n"
    for compat in compats['compatibilities']:
        result += " * " + compat['license'] + "\n"

    result += "\n\n# Compatibilities\n\n"
    for compat in compats['compatibilities']:
        main_license = compat['license']
        for lic in compat['licenses']:
            # print(str(compat))
            # print(json.dumps(compat))
            # print(json.dumps(lic))
            inner_license = lic['license']
            comp_left = lic['compatible_left']
            comp_right = lic['compatible_right']
            compat_text = _compat_to_markdown(
                main_license, comp_left, inner_license, comp_right)
            result += main_license + " " + compat_text + " " + inner_license + "\n\n"

    return result

