#!/bin/python3

# SPDX-FileCopyrightText: 2021 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later

from argparse import RawTextHelpFormatter
import argparse

from flict.flictlib import logger
from flict.flictlib.license import LicenseHandler
from flict.flictlib.license import encode_license_expression
from flict.flictlib.license import decode_license_expression
from flict.flictlib.compatibility import Compatibility
from flict.flictlib.flict_config import flict_version
from flict.flictlib.format.factory import FormatFactory
from flict.flictlib.project import Project
from flict.flictlib.report import Report
from flict.flictlib.return_codes import FLictException
from flict.flictlib.return_codes import ReturnCodes

import flict.flictlib.report
from flict.flictlib import flict_config

import json
import os
import sys


SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))

PROGRAM_NAME = "flict (FOSS License Compatibility Tool)"
PROGRAM_DESCRIPTION = "flict is a Free and Open Source Software tool to verify compatibility between licenses"
PROGRAM_URL = "https://github.com/vinland-technology/flict"
BUG_URL = "https://github.com/vinland-technology/flict/issues"
PROGRAM_COPYRIGHT = "(c) 2021 Henrik Sandklef<hesa@sandklef.com>"
PROGRAM_LICENSE = "GPL-3.0-or-later"
PROGRAM_AUTHOR = "Henrik Sandklef"
PROGRAM_ATTRIBUTION = "flict is using the license compatibility matrix from osadl.org,\n  which can be found at https://www.osadl.org/fileadmin/checklists/matrix.html"
PROGRAM_SEE_ALSO = ""

OUTPUT_FORMAT_JSON = "JSON"
OUTPUT_FORMAT_TEXT = "text"
OUTPUT_FORMAT_MARKDOWN = "markdown"
OUTPUT_FORMAT_DOT = "dot"
DEFAULT_OUTPUT_FORMAT = OUTPUT_FORMAT_JSON

DATE_FMT = '%Y-%m-%d'


class FlictSetup:

    _instance = None

    def __init__(self, license_handler, compatibility, output_format, output):
        self.license_handler = license_handler
        self.compatibility = compatibility
        self.formatter = FormatFactory.formatter(output_format)
        self.output = output

    @staticmethod
    def get_setup(args):
        if FlictSetup._instance is None:
            logger.setup(args.debug_license, args.verbose)

            license_handler = LicenseHandler(
                args.translations_file, args.relicense_file, "")
            compatibility = Compatibility(
                args.matrix_file, args.scancode_file, args.license_group_file, args.extended_licenses)

            FlictSetup._instance = FlictSetup(
                license_handler, compatibility, args.output_format, args.output)

            logger.main_logger.debug(
                " flict_setup: " + str(FlictSetup._instance))
        return FlictSetup._instance


def parse():

    description = "NAME\n  " + PROGRAM_NAME + "\n\n"
    description = description + "DESCRIPTION\n  " + PROGRAM_DESCRIPTION + "\n\n"

    epilog = ""
    epilog = epilog + "CONFIGURATION\n  All config files can be found in\n  " + flict_config.VAR_DIR + "\n\n"
    epilog = epilog + "AUTHOR\n  " + PROGRAM_AUTHOR + "\n\n"
    epilog = epilog + "PROJECT SITE\n  " + PROGRAM_URL + "\n\n"
    epilog = epilog + "REPORTING BUGS\n  Create an issue at " + BUG_URL + "\n\n"
    epilog = epilog + "COPYRIGHT\n  Copyright " + \
        PROGRAM_COPYRIGHT + ".\n  License " + PROGRAM_LICENSE + "\n\n"
    epilog = epilog + "ATTRIBUTION\n  " + PROGRAM_ATTRIBUTION + "\n\n"
    epilog = epilog + "SEE ALSO\n  " + PROGRAM_SEE_ALSO + "\n\n"

    parser = argparse.ArgumentParser(
        description=description,
        epilog=epilog,
        formatter_class=RawTextHelpFormatter,
    )

    commmon_defaults_group = parser.add_argument_group(
        title='Options to change default settings')
    deveveloper_group = parser.add_argument_group(title='Developer options')

    # DEFAULTS
    commmon_defaults_group.add_argument('-gf', '--group-file',
                                        type=str,
                                        dest='license_group_file',
                                        help='File with group definitions, defaults to' +
                                        flict_config.DEFAULT_GROUP_BASE_FILE + ". EXPERIMENTAL",
                                        default=flict_config.DEFAULT_GROUP_FILE)

    # DEFAULTS
    commmon_defaults_group.add_argument('-mf', '--matrix-file',
                                        type=str,
                                        dest='matrix_file',
                                        help='File with license compatibility matrix, defaults to ' + flict_config.DEFAULT_MATRIX_BASE_FILE,
                                        default=flict_config.DEFAULT_MATRIX_FILE)

    # DEFAULTS
    commmon_defaults_group.add_argument('-rf', '--relicense-file',
                                        type=str,
                                        dest='relicense_file',
                                        help='File with relicensing information, defaults to ' + flict_config.DEFAULT_RELICENSE_BASE_FILE,
                                        default=flict_config.DEFAULT_RELICENSE_FILE)
    # DEFAULTS
    commmon_defaults_group.add_argument('-sf', '--scancode-file',
                                        type=str,
                                        dest='scancode_file',
                                        help='File with scancode licenseses information, defaults to ' +
                                        flict_config.DEFAULT_SCANCODE_BASE_FILE + ". EXPERIMENTAL",
                                        default=flict_config.DEFAULT_SCANCODE_FILE)

    # DEFAULTS
    commmon_defaults_group.add_argument('-tf', '--translations-file',
                                        type=str,
                                        dest='translations_file',
                                        help='File with license translations, defaults to' + flict_config.DEFAULT_TRANSLATIONS_BASE_FILE,
                                        default=flict_config.DEFAULT_TRANSLATIONS_FILE)

    # COMMON
    parser.add_argument('-es', '--enable-scancode',
                        action='store_true',
                        dest='enable_scancode',
                        help="Use Scancode's license database - experimental so use with care",
                        default=False)

    # COMMON
    parser.add_argument('-el', '--extended-licenses',
                        action='store_true',
                        dest='extended_licenses',
                        help='Check all supported licenes when trying to find an outbound license',
                        default=False)

    # COMMON
    parser.add_argument('-nr', '--no-relicense',
                        action='store_true',
                        dest='no_relicense',
                        help='do not use license relicensing, same as -rf ""',
                        default=False)

    # COMMON
    parser.add_argument('-o', '--output',
                        type=argparse.FileType('w'),
                        dest='output',
                        help='output, defaults to stdout',
                        default=sys.stdout)
    # COMMON
    parser.add_argument('-of', '--output-format',
                        type=str,
                        dest='output_format',
                        help="output format. Avilable formats: " + OUTPUT_FORMAT_JSON + ", " + OUTPUT_FORMAT_TEXT + ", " +
                        OUTPUT_FORMAT_MARKDOWN + ", " + OUTPUT_FORMAT_DOT +
                        ". Defaults to " + DEFAULT_OUTPUT_FORMAT,
                        default=DEFAULT_OUTPUT_FORMAT)

    parser.add_argument('-v', '--verbose',
                        action='store_true',
                        help='output verbose information to stderr',
                        default=False)

    parser.add_argument('-cc', '--check-compatibility',
                        type=str, nargs='+',
                        dest='licenses',
                        help='licenses to check for compatibility')

    parser.add_argument('-ol', '--outbound-license',
                        type=str,
                        dest='outbound_licenses',
                        help='conclude outbound license suggestions from specified license expression. Example: -ol "GPLv2 and MIT BSD-3"')

    # KEEP
    parser.add_argument('-V', '--version',
                        action='version',
                        version=flict_version,
                        default=False)

    deveveloper_group.add_argument('-dl', '--debug-license',
                                   action='store_true',
                                   dest='debug_license',
                                   help='output verbose debug information of the intermediate steps when transforming a license expression',
                                   default=False)

    subparsers = parser.add_subparsers(help='Sub commands')

    # verify
    parser_v = subparsers.add_parser(
        'verify', help='verify license compatibility')
    parser_v.set_defaults(which="verify", func=verify)
#    parser_v.add_argument('--project-file', '-pf', type=argparse.FileType('r'), help='verify license compatibility for project in project file')
    parser_v.add_argument('--project-file', '-pf', type=str,
                          help='verify license compatibility for project in project file')
    parser_v.add_argument('--license-expression', '-le', type=str, nargs='+',
                          help='verify license compatibility for license expression')
    parser_v.add_argument('--manifest-file', '-mf', type=str,
                          help='verify license compatibility for project in manifest file')
    parser_v.add_argument('--license-combination-count', '-lcc', action='store_true', dest='license_combination_count',
                          help='output the number of license combinations in the specified project')
    parser_v.add_argument('--list-project_licenses', '-lpl', action='store_true',
                          dest='list_project_licenses',
                          help='output the licenses in the specified project')

    # simplify
    parser_si = subparsers.add_parser(
        'simplify', help='expand and simplify license expression')
    parser_si.set_defaults(which="simplify", func=simplify)
    parser_si.add_argument('license_expression', type=str, nargs='+',
                           help='license expression to simplify')

    # list
    parser_li = subparsers.add_parser(
        'list', help='list supported licenses or groups')
    parser_li.set_defaults(which="list", func=list_licenses)
    parser_li.add_argument('--groups', '-g',
                           action='store_true',
                           dest='list_supported_license_groups',
                           help='output the license groups supported by flict')
    parser_li.add_argument('-lg', '--license-group',
                           dest='license_group',
                           type=str,
                           help='output group (if any) for license')

    # display-compatibility
    parser_d = subparsers.add_parser(
        'display-compatibility', help='display license compatibility graphically')
    parser_d.set_defaults(which="display-compatibility",
                          func=display_compatibility)
    parser_d.add_argument('--graph', '-g', type=str,
                          help='create graph representation')
    parser_d.add_argument('--table', '-t', type=str,
                          help='create table representation')
    parser_d.add_argument('licenses', type=str, nargs='+',
                          help='license expression to display compatibility for')

    # outbound-candidates
    parser_s = subparsers.add_parser(
        'outbound-candidate', help='suggest outbound license candidates')
    parser_s.set_defaults(which="outbound-candidate",
                          func=suggest_outbound_candidate)
    parser_s.add_argument('license_expression', type=str, nargs='+',
                          help='license expression to suggest candidate outbound license for')

    # policy-report
    parser_p = subparsers.add_parser(
        'policy-report', help='create report with license policy applied')
    parser_p.set_defaults(which="policy-report", func=policy_report)
    parser_p.add_argument('--license-policy-file', '-lpf',
                          type=argparse.FileType('r'),
                          dest='policy_file',
                          help='file with license policy')
    parser_p.add_argument('--compliance-report-file', '-crf',
                          type=argparse.FileType('r'),
                          help='file with report as produced using "verify"')

    args = parser.parse_args()

    if args.no_relicense:
        args.relicense_file = ""

    if not args.enable_scancode:
        args.scancode_file = None

    return args


def read_compliance_report(report_file):
    with open(report_file) as fp:
        return json.load(fp)


def output_supported_license_groups(flict_setup):
    supported_license_groups = flict_setup.compatibility.supported_license_groups()
    supported_license_groups.sort()

    formatted = flict_setup.formatter.format_supported_license_groups(
        supported_license_groups)
    flict_print(flict_setup, formatted)

    return


def output_license_group(compatibility, license_handler, args):
    flict_setup = FlictSetup.get_setup(args)
    formatted = flict_setup.formatter.format_license_group(flict_setup.compatibility,
                                                           flict_setup.license_handler,
                                                           args.license_group,
                                                           args.extended_licenses)
    flict_print(flict_setup, formatted)


def flict_print(flict_setup, msg):
    print(msg, file=flict_setup.output)


def flict_exit(ret_code, msg):
    if msg is not None:
        logger.main_logger.error(msg)
    exit(ret_code)


def output_supported_licenses(flict_setup):
    formatted = flict_setup.formatter.format_support_licenses(
        flict_setup.compatibility)
    flict_print(flict_setup, formatted)


def _empty_project_report(compatibility, license_handler, licenses, output_format, extended_licenses):
    project = Project(None, license_handler, licenses)
    report_object = Report(project, compatibility)
    report = report_object.report()
    return report


def _outbound_license(compatibility, license_handler, licenses, output_format, extended_licenses):
    c_report = _empty_project_report(
        compatibility, license_handler, licenses, output_format, extended_licenses)
    outbound_candidates = flict.flictlib.report.outbound_candidates(c_report)
    #outbound_candidates = flict.flictlib.report.outbound_candidates(c_report)
    #outbound_candidates = report['compatibility_report']['compatibilities']['outbound_candidates']
    outbound_candidates.sort()
    # print(json.dumps(c_report))
    return outbound_candidates


def output_outbound_license(flict_setup, licenses, output_format, extended_licenses):
    outbound_candidates = _outbound_license(flict_setup.compatibility,
                                            flict_setup.license_handler,
                                            licenses,
                                            output_format,
                                            extended_licenses)
    formatted = flict_setup.formatter.format_outbound_license(
        outbound_candidates)
    flict_print(flict_setup, formatted)


def present_and_set(args, key):
    return key in args and vars(args)[key] is not None


def simplify(args):
    flict_setup = FlictSetup.get_setup(args)
    lic_str = None
    for lic in args.license_expression:
        if lic_str is None:
            lic_str = lic
        else:
            lic_str += " " + lic
    try:
        license = flict_setup.license_handler.license_expression_list(lic_str)
    except:
        raise FLictException(ReturnCodes.RET_INVALID_EXPRESSSION,
                             "Invalid expression to simplify: " + str(args.license_expression))

    formatted = flict_setup.formatter.format_simplified(
        lic_str, license.simplified)
    flict_print(flict_setup, formatted)


def list_licenses(args):
    flict_setup = FlictSetup.get_setup(args)
    if args.license_group:
        output_license_group(flict_setup.compatibility,
                             flict_setup.license_handler, args)
    elif args.list_supported_license_groups:
        output_supported_license_groups(flict_setup)
    else:
        output_supported_licenses(flict_setup)


def verify(args):
    flict_setup = FlictSetup.get_setup(args)

    if present_and_set(args, 'project_file'):
        verify_project_file(args, flict_setup)
    elif present_and_set(args, 'license_expression'):
        verify_license_expression(args, flict_setup)
    else:
        raise FLictException(ReturnCodes.RET_MISSING_ARGS,
                             "Missing argument to the verify command")


def verify_license_expression(args, flict_setup):
    lic_str = ""
    for lic in args.license_expression:
        lic_str += " " + lic

    try:
        report = _empty_project_report(flict_setup.compatibility, flict_setup.license_handler,
                                       lic_str, args.output_format, args.extended_licenses)

        candidates = report['compatibility_report']['compatibilities']['outbound_candidates']

        formatted = flict_setup.formatter.format_verified_license(
            lic_str, candidates)

        flict_print(flict_setup, formatted)
    except:
        raise FLictException(ReturnCodes.RET_INVALID_EXPRESSSION,
                             "Could not parse expression \"" + str(args.license_expression) + "\"")


def verify_project_file(args, flict_setup):

    try:
        project = Project(args.project_file, flict_setup.license_handler)
    except:
        raise FLictException(ReturnCodes.RET_INVALID_PROJECT,
                             "Missing or invalid project file.")

    formatted = ""
    if args.list_project_licenses:
        formatted = flict_setup.formatter.format_license_list(
            list(project.license_set()))

    elif args.license_combination_count:
        formatted = flict_setup.formatter.format_license_combinations(project)
    else:
        report = Report(project, flict_setup.compatibility)
        formatted = flict_setup.formatter.format_report(report)

    flict_print(flict_setup, formatted)


def display_compatibility(args):
    flict_setup = FlictSetup.get_setup(args)

    try:
        # build up license string from all expressions
        lic_str = ""
        for lic in args.licenses:
            lic_str += " " + lic

        # encode (flict) all the license expression
        lic_str = encode_license_expression(lic_str)

        # build up license string from the expression string
        _licenses = []
        for lic in lic_str.split():
            #print("   lic: " + str(lic))
            lic_list = flict_setup.license_handler.translate_and_relicense(lic).replace("(", "").replace(
                ")", "").replace(" ", "").replace("OR", " ").replace("AND", " ").strip().split(" ")

            for lic in lic_list:
                _licenses.append(decode_license_expression(lic))
            #print(lic + " ==> " + str(lic_list) + " =====> " + str(_licenses))
            #print("Check compat for: " + str(licenses))

            # Diry trick to remove all duplicates
        licenses = list(set(_licenses))

        compats = flict_setup.compatibility.check_compatibilities(
            licenses, args.extended_licenses)
    except:
        raise FLictException(ReturnCodes.RET_INVALID_EXPRESSSION,
                             "Could not parse license expression: " + str(args.licenses))

    formatted = flict_setup.formatter.format_compats(compats)
    flict_print(flict_setup, formatted)


def suggest_outbound_candidate(args):
    flict_setup = FlictSetup.get_setup(args)

    #print("suggest_outbound:    " + str(args))
    #print("verbose:             " + str(args.verbose))
    #print("license expression:: " + str(args.license_expression))
    lic_str = ""
    for lic in args.license_expression:
        lic_str += " " + lic

    try:
        output_outbound_license(flict_setup, lic_str,
                                args.output_format, args.extended_licenses)
    except:
        raise FLictException(ReturnCodes.RET_INVALID_EXPRESSSION,
                             "Invalid license expression: " + str(args.licenses))


def policy_report(args):
    print("polict_report: " + str(args))


def main():
    args = parse()

    if 'which' in args:
        try:
            args.func(args)
        except FLictException as e:
            flict_exit(e.error_code(), e.error_message())

    else:
        flict_exit(ReturnCodes.RET_MISSING_ARGS, "Missing command.")

    #flict_exit(ReturnCodes.RET_SUCESS, None)


if __name__ == '__main__':
    main()
