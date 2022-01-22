#!/usr/bin/env python3

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

import json


class JsonFormatter(FormatInterface):

    def format_support_licenses(self, compatibility):
        return json.dumps(compatibility.supported_licenses())

    def format_license_list(self, license_list):
        return json.dumps(license_list)

    def format_report(self, report):
        return report.to_json()

    def format_license_combinations(self, project):
        return json.dumps({
            'license_combinations': project.projects_combinations()
        })

    def format_outbound_license(self, outbound_candidate):
        return json.dumps(outbound_candidate)

    def format_compats(self, compats):
        return json.dumps(compats)

    def format_simplified(self, license_expression, simplified):
        return json.dumps({'original':  license_expression,
                           'simplified': simplified})

    def format_verified_license(self, license_expression, outbound_candidate):
        compat = len(outbound_candidate) != 0
        return json.dumps({"license_expression": license_expression,
                           "compatible": compat,
                           "outbound_candidate": outbound_candidate}
                          )

    def format_relicense_information(self, license_handler):
        return json.dumps(license_handler.relicensing_information()['original']['relicense_definitions'])

    def format_translation_information(self, license_handler):
        return json.dumps(license_handler.translation_information())

    def format_policy_report(self, policy_report):
        return json.dumps(policy_report)
