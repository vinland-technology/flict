###################################################################
#
# flict - FOSS License Compatibility Tool
#
# SPDX-FileCopyrightText: 2021 Jens Erdmann
# SPDX-FileCopyrightText: 2022 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later
#
###################################################################


from flict.flictlib.return_codes import FlictError, ReturnCodes

from flict.flictlib.arbiter import Arbiter
from flict.flictlib.format.factory import FormatterFactory
from flict.flictlib.project.reader import ProjectReaderFactory

import json


class FlictImpl:

    def __init__(self, args) -> None:
        self._args = args
        self.arbiter = self._get_arbiter()
        self._formatter = FormatterFactory.formatter(args.output_format)

    def merge_license_db(self):
        return self.arbiter.extend_license_db(self._args.license_file)

    def display_compatibility(self):
        inter_compats = self.arbiter.check_compatibilities(self._args.license_expression)
        return self._formatter.format_compats(inter_compats)

    def simplify(self):
        return self.arbiter.simplify_license(" ".join(self._args.license_expression))

    def suggest_outbound_candidate(self):
        licenses = self.arbiter.licenses(" ".join(self._args.license_expression))
        outbounds = []
        try:
            for outbound in licenses:
                compats = self.arbiter.inbounds_outbound_check(outbound, self._args.license_expression)
                compatible = (compats['compatibility'] == "Yes")
                if compatible:
                    outbounds.append(outbound)

            outbounds.sort()
            return self._formatter.format_outbound_license(outbounds)

        except:
            raise FlictError(ReturnCodes.RET_INVALID_EXPRESSSION,
                             f'Invalid license expression: {self._args.license_expression}')

    def list_licenses(self):
        licenses = list(self.arbiter.supported_licenses())
        licenses.sort(key=str.lower)
        return self._formatter.format_support_licenses(licenses)

    def _handle_lico_project(self, reader, project_file, formatter):
        project = reader.read_project(project_file)
        verification = self.arbiter.verify(project)
        verification_report = formatter.format_verification(verification)
        return verification_report

    def _read_json_object(self, file_name, object_key, ret):
        if not file_name:
            return ret
        else:
            with open(file_name) as fp:
                return json.load(fp)[object_key]

    def _get_arbiter(self):
        licenses_denied_file = self._args.licenses_denied_file
        licenses_preference_file = self._args.licenses_preference_file
        alias_file = self._args.alias_file

        if self._args.licenses_info_file:
            licenses_denied_file = self._args.licenses_info_file
            licenses_preference_file = self._args.licenses_info_file

        licenses_denied = self._read_json_object(licenses_denied_file, "licenses_denied", [])
        licenses_preferences = self._read_json_object(licenses_preference_file, "license_preferences", [])
        #parser = LicenseParserFactory.get_parser(licenses_preferences, licenses_denied)
        arbiter = Arbiter(license_db=self._args.license_matrix_file, licenses_preferences=licenses_preferences, denied_licenses=licenses_denied, alias_file=alias_file)

        return arbiter

    def verify(self):
        formatter = FormatterFactory.formatter(self._args.output_format)

        if self._args.out_license and self._args.in_license_expr:
            compats = self.arbiter.inbounds_outbound_check(self._args.out_license, self._args.in_license_expr)
            formatted = formatter.format_compatibilities(compats)
            return formatted

        elif self._args.verify_flict:
            #print("con flict: " + str(self._args.license_matrix_file))
            project_reader = ProjectReaderFactory.get_projectreader(self._args.verify_flict, None, "flict")
            return self._handle_lico_project(project_reader, self._args.verify_flict, formatter)

        elif self._args.verify_sbom:
            project_reader = ProjectReaderFactory.get_projectreader(self._args.verify_sbom, self._args.sbom_dirs)
            return self._handle_lico_project(project_reader, self._args.verify_sbom, formatter)

