###################################################################
#
# flict - FOSS License Compatibility Tool
#
# SPDX-FileCopyrightText: 2021 Jens Erdmann
# SPDX-FileCopyrightText: 2023 Henrik Sandklef
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
        return self.arbiter.extend_license_db(self._args.license_file, oformat=self._args.output_format, default_no=self._args.default_no)

    def display_compatibility(self):
        compat_list = []
        for lic in self._args.license_expression:
            compat_list.append(self.arbiter.license_compatibility_as(lic))
        inter_compats = self.arbiter.check_compatibilities(compat_list)
        return self._formatter.format_compats(inter_compats)

    def simplify(self):
        simplified = self.arbiter.simplify_license(" ".join(self._args.license_expression))
        return self._formatter.format_simplified(simplified)

    def suggest_outbound_candidate(self):
        license_expression = self._args.license_expression

        if self._args.extended_licenses:
            licenses = self.arbiter.supported_licenses()
        else:
            license_expression = self.arbiter.simplify_license(" ".join(self._args.license_expression))['simplified']
            licenses = self.arbiter.licenses(license_expression)

        allowed_licenses = [x for x in licenses if self.arbiter.license_allowed(x)]

        outbounds = []
        try:
            for outbound in allowed_licenses:
                compats = self.arbiter.inbounds_outbound_check(outbound, [license_expression])
                compat = compats['compatibility'] == 'Yes'
                if compat:
                    outbounds.append(outbound)

            outbounds.sort()
            return self._formatter.format_outbound_license(outbounds)

        except Exception as e:
            raise FlictError(ReturnCodes.RET_INVALID_EXPRESSSION,
                             f'Invalid license expression: {self._args.license_expression}. Original cause: {e}')

    def list_licenses(self):
        licenses = list(self.arbiter.supported_licenses())
        licenses.sort(key=str.lower)
        return self._formatter.format_support_licenses(licenses)

    def _handle_lico_project(self, reader, project_file, formatter):
        project = reader.read_project(project_file)
        verification = self.arbiter.verify(project)
        return verification

    def _read_json_object(self, file_name, object_key, ret):
        if not file_name:
            return ret
        else:
            with open(file_name) as fp:
                return json.load(fp)[object_key]

    def _get_arbiter(self):
        licenses_denied_file = self._args.licenses_denied_file
        licenses_allowed_file = self._args.licenses_allowed_file
        licenses_preference_file = self._args.licenses_preference_file

        if self._args.licenses_info_file:
            licenses_denied_file = self._args.licenses_info_file
            licenses_preference_file = self._args.licenses_info_file

        licenses_denied = self._read_json_object(licenses_denied_file, "licenses_denied", [])
        licenses_allowed = self._read_json_object(licenses_allowed_file, "licenses_allowed", [])
        licenses_preferences = self._read_json_object(licenses_preference_file, "license_preferences", [])
        arbiter = Arbiter(license_db=self._args.license_matrix_file,
                          licenses_preferences=licenses_preferences,
                          denied_licenses=licenses_denied,
                          allowed_licenses=licenses_allowed,
                          update_dual=not self._args.no_relicense)

        return arbiter

    def _compatibility_report_to_return_code(self, compatibility_report):
        """ Given a compatibility report, this functions returns the return code
        """
        if len(compatibility_report['result']['allowed_outbound_licenses']) > 0:
            return 0
        return 1

    def _verification_report_to_return_code(self, verification_report):
        """ Given a verification report, this functions returns the return code
        """
        compatible = True
        for package in verification_report['packages']:
            compatible = compatible and (len(package['allowed_outbound_licenses']) > 0)
        return 0 if compatible else 1

    def verify(self):
        formatter = FormatterFactory.formatter(self._args.output_format)
        strict_check = not self._args.ignore_problems

        if self._args.verify_flict or self._args.verify_sbom:
            if self._args.verify_flict:
                project_reader = ProjectReaderFactory.get_projectreader(self._args.verify_flict, None, "flict")
                verifications = self._handle_lico_project(project_reader, self._args.verify_flict, formatter)
            elif self._args.verify_sbom:
                project_reader = ProjectReaderFactory.get_projectreader(self._args.verify_sbom, self._args.sbom_dirs)
                verifications = self._handle_lico_project(project_reader, self._args.verify_sbom, formatter)

            package_problems = [problem for package in verifications['packages'] for problem in package['problems']]
            deps_problems = [problem for package in verifications['packages'] for problem in package['dependency_problems']]
            problems = package_problems + deps_problems
            if strict_check and problems:
                raise FlictError(ReturnCodes.RET_INVALID_EXPRESSSION,
                                 f'Unknown or undefined licenses identified: {", ".join(problems)}')

            code = self._verification_report_to_return_code(verifications)
            verification_report = formatter.format_verification(verifications)
            return verification_report, code

        elif self._args.out_license and self._args.in_license_expr:
            compatibility_report = self.arbiter.verify_outbound_inbound(self._args.out_license, self._args.in_license_expr)
            problems = compatibility_report['result']['problems']
            if strict_check and problems:
                raise FlictError(ReturnCodes.RET_INVALID_EXPRESSSION,
                                 f'Unknown or undefined licenses identified: {", ".join(problems)}')
            return_code = self. _compatibility_report_to_return_code(compatibility_report)
            formatted = formatter.format_compatibilities(compatibility_report)
            return formatted, return_code
        else:
            raise FlictError(ReturnCodes.RET_MISSING_ARGS, 'Bad verify syntax')
