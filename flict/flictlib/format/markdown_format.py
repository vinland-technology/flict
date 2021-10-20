#!/usr/bin/python3

###################################################################
#
# flict - FOSS License Compatibility Tool
#
# SPDX-FileCopyrightText: 2021 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later
#
###################################################################

from flict.flictlib.format.format import FormatInterface
from flict.flictlib.format.common import compat_interprets


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
        ret_str = None
        for rel in license_handler.relicensing_information()['original']['relicense_definitions']:
            if ret_str is not None:
                ret_str += "\n"
            else:
                ret_str = ""
            lic = rel['spdx']
            later_str = None
            for later in rel['later']:
                if later_str is None:
                    later_str = later
                else:
                    later_str += ", " + later

            ret_str += lic + " --> " + later_str
        return "# Relicense information\n" + ret_str

    def format_translation_information(self, license_handler):
        ret_str = None
        for transl_list in license_handler.translation_information():
            for transl in transl_list:
                if ret_str is None:
                    ret_str = ""
                else:
                    ret_str += "\n"
                ret_str += transl + " <--- " + str(transl_list[transl])
        return "# Translation information\n" + ret_str


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

