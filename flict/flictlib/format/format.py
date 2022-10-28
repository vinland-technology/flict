###################################################################
#
# flict - FOSS License Compatibility Tool
#
# SPDX-FileCopyrightText: 2020 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later
#
###################################################################


class FlictFormatter:

    def format_support_licenses(self, supported_licenses):
        return "default implementation | format_support_licenses(): " + str(supported_licenses)

    def format_license_list(self, license_list):
        return "default implementation | format_license_list(): " + str(license_list)

    def format_outbound_license(self, outbounds):
        return "default implementation | format_outbound_license(): " + str(outbounds)

    def format_license_combinations(self, combinations):
        return "default implementation | format_license_combinations(): " + str(combinations)

    def format_compats(self, compats):
        return "default implementation | format_compats(): " + str(compats)

    def format_simplified(self, simplified):
        return "default implementation | format_simplified(): " + str(simplified)

    def format_verified_license(self, license_expression, outbound_candidate):
        return "default implementation | format_verified_license(): " + str(license_expression)

    def format_compatibilities(self, compats):
        return

    def format_licenses(self, licenses):
        return

    def format_verification(self, verification):
        return

    def get_dep_license(self, dep, outbound):
        for lic_compat in dep.get('compatibility'):
            outbound_lic = lic_compat['outbound']['name']

            if outbound_lic == outbound:
                name = self.license.verified_to_license(lic_compat)
                return name
        return None

    def find_compat(self, compats, license_name):
        for compat in compats['compatibilities']:
            if compat["license"] == license_name:
                return compat

    def find_license_compat(self, compat, license_name):
        for lic in compat['licenses']:
            if lic['license'] == license_name:
                return lic['compatible_left'].replace("true", "Yes").replace("false", "No")
