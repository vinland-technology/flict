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
        ret_str = ""
        for rel in license_handler.relicensing_information().get('original', {}).get('relicense_definitions', []):
            if ret_str:
                ret_str += "\n"
            later_str = rel.get('later', [])
            ret_str += "{lic} --> {later}".format(lic=rel.get('spdx', 'NOASSERTATION'), later=", ".join(later_str))
        return "# Translation information\n" + ret_str

    def format_translation_information(self, license_handler):
        ret_str = ""
        for transl_list in license_handler.translation_information():
            for transl in transl_list:
                if ret_str:
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

