###################################################################
#
# flict - FOSS License Compatibility Tool
#
# SPDX-FileCopyrightText: 2021 Jens Erdmann
#
# SPDX-License-Identifier: GPL-3.0-or-later
#
###################################################################


from flict.flictlib import logger
from flict.flictlib.compatibility import Compatibility
from flict.flictlib.format.factory import FormatFactory
from flict.flictlib.license import LicenseHandler, decode_license_expression, encode_license_expression
from flict.flictlib.policy import Policy
from flict.flictlib.project import Project
from flict.flictlib.report import Report, outbound_candidates
from flict.flictlib.return_codes import FlictException, ReturnCodes

import json


class FlictSetup:

    _instance = None

    def __init__(self, license_handler, compatibility, output_format):
        self.license_handler = license_handler
        self.compatibility = compatibility
        self.formatter = FormatFactory.formatter(output_format)

    @staticmethod
    def get_setup(args):
        if FlictSetup._instance is None:
            logger.setup(args.debug_license, args.verbose)

            license_handler = LicenseHandler(args.translations_file, args.relicense_file, "")
            compatibility = Compatibility(args.matrix_file,
                                          args.scancode_file,
                                          args.license_group_file,
                                          args.extended_licenses)

            FlictSetup._instance = FlictSetup(license_handler, compatibility, args.output_format)

            logger.main_logger.debug(" flict_setup: " + str(FlictSetup._instance))
        return FlictSetup._instance


class FlictImpl:
    def __init__(self, args) -> None:
        self._args = args
        self._setup = FlictSetup.get_setup(args)

    def _empty_project_report(self, compatibility, license_handler, licenses):
        project = Project(None, license_handler, licenses)
        report_object = Report(project, compatibility)
        return report_object.report()

    def simplify(self):
        lic_str = " ".join(self._args.license_expression)

        try:
            license = self._setup.license_handler.license_expression_list(lic_str)
            return self._setup.formatter.format_simplified(lic_str, license.simplified)
        except:
            raise FlictException(ReturnCodes.RET_INVALID_EXPRESSSION,
                                 "Invalid expression to simplify: " + str(self._args.license_expression))

    def list_licenses(self):
        formatted = ""
        if self._args.license_group:
            formatted = self._setup.formatter.format_license_group(self._setup.compatibility,
                                                                   self._setup.license_handler,
                                                                   self._args.license_group,
                                                                   self._args.extended_licenses)
        elif self._args.list_supported_license_groups:
            supported_license_groups = self._setup.compatibility.supported_license_groups().sort()
            formatted = self._setup.formatter.format_supported_license_groups(supported_license_groups)
        elif self._args.list_relicensing:
            formatted = self._setup.formatter.format_relicense_information(self._setup.license_handler)
        elif self._args.list_translation:
            formatted = self._setup.formatter.format_translation_information(self._setup.license_handler)
        else:
            formatted = self._setup.formatter.format_support_licenses(self._setup.compatibility)
        return formatted

    def _verify_license_expression(self):
        lic_str = " ".join(self._args.license_expression)

        try:
            report = self._empty_project_report(self._setup.compatibility,
                                                self._setup.license_handler,
                                                lic_str)
            candidates = report['compatibility_report']['compatibilities']['outbound_candidates']
            return self._setup.formatter.format_verified_license(lic_str, candidates)
        except:
            raise FlictException(ReturnCodes.RET_INVALID_EXPRESSSION,
                                 f"Could not parse expression \"{str(self._args.license_expression)}\"")

    def _verify_project_file(self):
        try:
            project = Project(self._args.project_file, self._setup.license_handler)
        except FlictException as e:
            raise(e)
        except:
            raise FlictException(ReturnCodes.RET_INVALID_PROJECT)

        formatted = ""
        if self._args.list_project_licenses:
            formatted = self._setup.formatter.format_license_list(list(project.license_set()))
        elif self._args.license_combination_count:
            formatted = self._setup.formatter.format_license_combinations(project)
        else:
            report = Report(project, self._setup.compatibility)
            formatted = self._setup.formatter.format_report(report)

        return formatted

    def _present_and_set(self, args, key):
        return key in args and vars(args)[key] is not None

    def verify(self):
        formatted = ""
        if self._present_and_set(self._args, 'project_file'):
            formatted = self._verify_project_file()
        elif self._present_and_set(self._args, 'license_expression'):
            formatted = self._verify_license_expression()
        else:
            raise FlictException(ReturnCodes.RET_MISSING_ARGS,
                                 "Missing argument to the verify command")
        return formatted

    def _read_compliance_report(self, report_file):
        with open(report_file) as fp:
            return json.load(fp)

    def policy_report(self):
        _compliance_report = self._read_compliance_report(self._args.report_file)
        _policy = Policy(self._args.policy_file)
        _policy_report = _policy.report(_compliance_report)
        return self._setup.formatter.format_policy_report(_policy_report)

    def display_compatibility(self):
        try:
            # build up license string from all expressions
            lic_str = " ".join(self._args.license_expression)

            # encode (flict) all the license expression
            lic_str = encode_license_expression(lic_str)

            # build up license string from the expression string
            _licenses = []
            for lic in lic_str.split():
                lic_list = self._setup.license_handler.translate_and_relicense(lic).replace("(", "").replace(
                    ")", "").replace(" ", "").replace("OR", " ").replace("AND", " ").strip().split(" ")

                for lic in lic_list:
                    _licenses.append(decode_license_expression(lic))

            # Diry trick to remove all duplicates
            licenses = list(set(_licenses))

            compats = self._setup.compatibility.check_compatibilities(licenses, self._args.extended_licenses)
        except:
            raise FlictException(ReturnCodes.RET_INVALID_EXPRESSSION,
                                 "Could not parse license expression: " + str(self._args.license_expression))

        return self._setup.formatter.format_compats(compats)

    def suggest_outbound_candidate(self):
        lic_str = " ".join(self._args.license_expression)

        try:
            _report = self._empty_project_report(lic_str)
            _outbound_candidates = outbound_candidates(_report)
            return self._formatter.format_outbound_license(_outbound_candidates)
        except:
            raise FlictException(ReturnCodes.RET_INVALID_EXPRESSSION,
                                 "Invalid license expression: " + str(self._args.licenses))
