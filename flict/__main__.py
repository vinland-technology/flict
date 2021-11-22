#!/bin/python3

# SPDX-FileCopyrightText: 2021 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later

from argparse import RawTextHelpFormatter
import argparse

from flict.flictlib import logger
from flict.flictlib.flict_config import flict_version
from flict.flictlib.return_codes import FlictException
from flict.flictlib.return_codes import ReturnCodes
from flict.flictlib import flict_config
from flict.impl import FlictImpl

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

DATE_FMT = '%Y-%m-%d'


def parse():

    description = "NAME\n  " + PROGRAM_NAME + "\n\n"
    description = description + "DESCRIPTION\n  " + PROGRAM_DESCRIPTION + "\n\n"

    epilog = "Return codes:\n{codes}\n\n".format(codes=ReturnCodes.get_help())
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

    commmon_defaults_group = parser.add_argument_group(title='Options to change default settings')
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
                                        help='File with license compatibility matrix, defaults to osadl-matrix database',
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
                        ". Defaults to " + flict_config.DEFAULT_OUTPUT_FORMAT,
                        default=flict_config.DEFAULT_OUTPUT_FORMAT)

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
    parser_li.add_argument('-r', '--relicensing',
                           dest='list_relicensing',
                           action='store_true',
                           help='List relicensing information')
    parser_li.add_argument('-t', '--translations',
                           dest='list_translation',
                           action='store_true',
                           help='List translation information')

    # display-compatibility
    parser_d = subparsers.add_parser(
        'display-compatibility', help='display license compatibility graphically')
    parser_d.set_defaults(which="display-compatibility",
                          func=display_compatibility)
    parser_d.add_argument('--graph', '-g', type=str,
                          help='create graph representation')
    parser_d.add_argument('--table', '-t', type=str,
                          help='create table representation')
    parser_d.add_argument('license_expression', type=str, nargs='+',
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
                          type=str,
                          dest='policy_file',
                          help='file with license policy',
                          default=None)
    parser_p.add_argument('--compliance-report-file', '-crf',
                          type=str,
                          dest='report_file',
                          help='file with report as produced using "verify"',
                          default=None)

    args = parser.parse_args()

    if args.no_relicense:
        args.relicense_file = ""

    if not args.enable_scancode:
        args.scancode_file = None

    return args


def flict_print(args, msg):
    print(msg, file=args.output)


def flict_exit(ret_code, msg=None):
    if msg is not None:
        logger.main_logger.error(msg)
    if isinstance(ret_code, ReturnCodes):
        ret_code = ret_code.value[0]
    exit(ret_code)


def simplify(args):
    ret = FlictImpl(args).simplify()
    flict_print(args, ret)


def list_licenses(args):
    ret = FlictImpl(args).list_licenses()
    flict_print(args, ret)


def verify(args):
    ret = FlictImpl(args).verify()
    flict_print(args, ret)


def display_compatibility(args):
    ret = FlictImpl(args).display_compatibility()
    flict_print(args, ret)


def suggest_outbound_candidate(args):
    ret = FlictImpl(args).suggest_outbound_candidate()
    flict_print(args, ret)


def policy_report(args):
    ret = FlictImpl(args).policy_report()
    flict_print(args, ret)


def main():
    args = parse()

    logger.setup(args.debug_license, args.verbose)

    if 'which' in args:
        try:
            args.func(args)
        except FlictException as e:
            flict_exit(e.error_code(), e.error_message())

    else:
        flict_exit(ReturnCodes.RET_MISSING_ARGS, "Missing command.")

    flict_exit(ReturnCodes.RET_SUCCESS)


if __name__ == '__main__':
    main()
