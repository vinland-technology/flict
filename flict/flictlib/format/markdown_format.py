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
from flict.flictlib.format.common import compat_interprets
from flict.flictlib.format.text_format import TextFormatter


COMPATIBILITY_TAG = "compatibility"

MANIFEST_HEADERS = {
    "projects": "#",
    "packages": "##",
    "package_name": "###",
    "dependencies": "####",
    "problems": "####",
    "dependency": "#####",
    "identified_license": "####"
}


PACKAGE_HEADERS = {
    "projects": "",
    "packages": "#",
    "package_name": "##",
    "dependencies": "###",
    "problems": "###",
    "dependency": "####",
    "identified_license": "###"
}


class MarkdownFlictFormatter(FlictFormatter):

    def format_compats(self, compats):
        return self.output_compat_markdown(compats)

    def format_relicense_information(self, license_handler):
        return "# Translation information\n" + TextFormatter.format_relicense_information(license_handler)

    def format_translation_information(self, license_handler):
        return "# Translation information\n" + TextFormatter.format_translation_information(license_handler)

    def format_compatibilities(self, compats):
        return compats[COMPATIBILITY_TAG]

    def format_licenses(self, licenses):
        return "\n".join(licenses)

    def parsed_to_license(self, parsed_expr):
        expr_type = parsed_expr['type']

        if expr_type == 'license':
            return parsed_expr['name']

        if expr_type == 'operator':
            name = parsed_expr['name']

            operands = []
            for op in parsed_expr['operands']:
                if op['compatibility'] != "Yes":
                    pass
                else:
                    parsed_op = self.parsed_to_license(op)
                    operands.append(parsed_op)
            operand_str = f" {name} "
            expr = operand_str.join(operands)
            if name == "OR" and len(operands) > 1:
                expr = f" ( {expr} ) "
            return expr

    def packages_header(self):
        return f"{self.headers['packages']} Packages\n"

    def package_name_header(self, name):
        return f"{self.headers['package_name']} {name}\n"

    def dependencies_header(self):
        return f"{self.headers['dependencies']} Dependencies\n"

    def problem_header(self):
        return f"{self.headers['problems']} Problems\n"

    def dependency_header(self, name):
        return f"{self.headers['dependency']} {name}\n"

    def identified_license_header(self):
        return f"{self.headers['identified_license']} Identified licenses in the combined work\n"

    def output_compat_markdown(self, compats):
        # print(str(compats))
        result = []

        result.append("# License compatibilities\n\n")

        result.append("# Licenses\n\n")
        for compat in compats['compatibilities']:
            result.append(" * " + compat['license'] + "\n")

        result.append("\n\n# Compatibilities\n\n")
        for compat in compats['compatibilities']:
            main_license = compat['license']
            result.append(self._output_compat_markdown_licenses(main_license, compat))

        return result

    def format_verification(self, verification):
        output = []
        output.append(self.packages_header())
        identified_license = None
        for package in verification['packages']:

            #            identified_license = package.get('identified_license', None)
            #            identified_license_aliased = package.get('identified_license_aliased', identified_license)
            identified_license = package.get('outbound_license', None)
            identified_license_aliased = package.get('outbound_license_aliased', None)

            identified_licenses = package.get('outbound_licenses', None)
            #identified_licenses_aliased = package.get('outbound_licenses_aliased', identified_licenses)

            output.append(self.package_name_header(package['name']))
            description = package.get('description', "")
            if description != "":
                output.append(f"*Description*: {description}\n")

            if identified_licenses == []:
                output.append("Main license: Could not be identified, see problems section below.\n")
                output.append(f"Declared license: {package['license']}\n")
            else:
                # Out of the outbound licenses, present the first and suggest the others
                #identified_license = identified_licenses[0]
                #identified_license_aliased = identified_licenses_aliased[0]
                output.append(f"Main license: {identified_license}\n")

                if identified_license != identified_license_aliased:
                    output.append(f"Main license alias: {identified_license_aliased}\n")
                if identified_licenses and len(identified_licenses) > 1:
                    output.append(f"*Other possible main licenses*: {identified_license}\n".format(identified=", ".join(identified_licenses[1:])))

            output.append(self.dependencies_header())
            for dep in package['dependencies']:

                if not identified_license:
                    dep_identified_license = None
                else:
                    dep_identified_license = super()._get_dep_license(dep, identified_license)

                version = dep.get('version', None)

                output.append(self.dependency_header(dep['name']))
                if version:
                    output.append(f"* version: {version}")
                output.append(f"* declared license:  {dep['license']}")
                if dep_identified_license:
                    output.append(f"* concluded license: {dep_identified_license}")
                output.append("\n")

            output.append(self.identified_license_header())
            license_list = list(verification['all_licenses'])
            license_list.sort(key=str.lower)
            for lic in license_list:
                output.append(f"* {lic}\n")

            # Add problem discussion
            if not dep_identified_license:
                output.append(self.problem_header())
                output.append("Could not conclude an outbound license for the combined work.\n")
        return "\n".join(output)


class ManifestMarkdownFlictFormatter(MarkdownFlictFormatter):

    def __init__(self):
        self.headers = MANIFEST_HEADERS


class PackageMarkdownFlictFormatter(MarkdownFlictFormatter):

    def __init__(self):
        self.headers = PACKAGE_HEADERS


def _compat_to_fmt(comp_left, comp_right, fmt):
    left = compat_interprets['left'][comp_left][fmt]
    right = compat_interprets['right'][comp_right][fmt]
    return str(right) + str(left)


def _compat_to_markdown(left, comp_left, right, comp_right):
    return _compat_to_fmt(comp_left, comp_right, "markdown")


def _output_compat_markdown_licenses(main_license, compat):
    result = []
    for lic in compat['licenses']:
        inner_license = lic['license']
        comp_left = lic['compatible_left']
        comp_right = lic['compatible_right']
        compat_text = _compat_to_markdown(
            main_license, comp_left, inner_license, comp_right)
        result.append(main_license + " " + compat_text + " " + inner_license + "\n\n")
    return "".join(result)

