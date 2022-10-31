###################################################################
#
# flict - FOSS License Compatibility Tool
#
# SPDX-FileCopyrightText: 2020, 2022 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later
#
###################################################################

from flict.flictlib.format.format import FlictFormatter

import json


class JsonFormatter(FlictFormatter):

    def format_support_licenses(self, supported_licenses):
        return json.dumps(supported_licenses)

    def format_license_list(self, license_list):
        return json.dumps(license_list)

    def format_license_combinations(self, project):
        return json.dumps({
            'license_combinations': project.projects_combinations(),
        })

    def format_outbound_license(self, outbound_candidate):
        return json.dumps(outbound_candidate)

    def format_compats(self, compats):
        return json.dumps(compats)

    def format_simplified(self, simplified):
        return json.dumps(simplified)

    def format_verified_license(self, license_expression, outbound_candidate):
        compat = len(outbound_candidate) != 0
        return json.dumps({"license_expression": license_expression,
                           "compatible": compat,
                           "outbound_candidate": outbound_candidate},
                          )

    def format_relicense_information(self, license_handler):
        return json.dumps(license_handler.relicensing_information()['original']['relicense_definitions'])

    def format_compatibilities(self, compats):
        return json.dumps(compats)

    def format_licenses(self, licenses):
        return json.dumps(licenses)

    def format_verification(self, verification):
        return json.dumps(verification)
