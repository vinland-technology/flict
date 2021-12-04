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


class FormatInterface:

    def format_support_licenses(self, supported_licenses):
        return "default implementation | format_support_licenses(): " + str(supported_licenses)

    def format_license_list(self, license_list):
        return "default implementation | format_license_list(): " + str(license_list)

    def format_report(self, report):
        return "default implementation | format_report(): " + str(report)

    def format_license_project(self, project):
        return "default implementation | format_license_combinations(): " + str(project)

    def format_outbound_license(self, outbounds):
        return "default implementation | format_outbound_license(): " + str(outbounds)

    def format_license_combinations(self, combinations):
        return "default implementation | format_license_combinations(): " + str(combinations)

    def format_compats(self, compats):
        return "default implementation | format_compats(): " + str(compats)

    def format_simplified(self, license_expression, simplified):
        return "default implementation | format_simplified(): " + str(simplified)

    def format_verified_license(self, license_expression, outbound_candidate):
        return "default implementation | format_verified_license(): " + str(license_expression)

    def format_relicense_information(self, license_handler):
        return "default implementation | format_relicense_information(): "

    def format_translation_information(self, license_handler):
        return "default implementation | format_translation_information(): "

    def format_policy_report(self, policy_report):
        return "default implementation | format_policy_report(): "

