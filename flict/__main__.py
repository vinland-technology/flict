# SPDX-FileCopyrightText: 2021 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later

from argparse import RawTextHelpFormatter
import argparse

from flict.flictlib import logger
from flict.flictlib.flict_config import flict_version
from flict.flictlib.return_codes import FlictError
from flict.flictlib.return_codes import ReturnCodes
from flict.flictlib import flict_config
from flict.flictlib.flict_config import FLICT_HOMEPAGE
from flict.flictlib.flict_config import FLICT_BUGS
from flict.impl import FlictImpl

import sys

DESCRIPTION = """
NAME
  flict (FOSS License Compatibility Tool)

DESCRIPTION
  flict is a Free and Open Source Software tool to verify compatibility between licenses

"""

EPILOG = f"""
Return codes:
{ReturnCodes.get_help()}
CONFIGURATION
  All config files can be found in
  {flict_config.VAR_DIR}

AUTHORS
   Jens Erdmann, Krzysztof Królczyk, Henrik Sandklef and Konrad Weihmann 

PROJECT SITE
  {FLICT_HOMEPAGE}

REPORTING BUGS
  File a ticket at {FLICT_BUGS}

COPYRIGHT
  Copyright (c) 2022 belongs to the authors
  License GPL-3.0-or-later

ATTRIBUTION
  flict is using the license compatibility matrix from osadl.org.


"""

OUTPUT_FORMAT_JSON = "JSON"
OUTPUT_FORMAT_TEXT = "text"
OUTPUT_FORMAT_MARKDOWN = "markdown"
OUTPUT_FORMAT_DOT = "dot"

DATE_FMT = '%Y-%m-%d'


def parse():

    parser = argparse.ArgumentParser(
        description=DESCRIPTION,
        epilog=EPILOG,
        formatter_class=RawTextHelpFormatter,
    )

    commmon_defaults_group = parser.add_argument_group(title='Options to change default settings')
    deveveloper_group = parser.add_argument_group(title='Developer options')

    # DEFAULTS
    commmon_defaults_group.add_argument('--license-matrix-file', '-lmf',
                                        type=str,
                                        dest='license_matrix_file',
                                        help='File with license compatibility matrix, defaults to osadl-matrix database',
                                        default=flict_config.DEFAULT_MATRIX_FILE)

    commmon_defaults_group.add_argument('--licenses-denied-file', '-ldf', type=str, dest='licenses_denied_file', help='', default=None)

    commmon_defaults_group.add_argument('--licenses-preference-file', '-lpf', type=str, dest='licenses_preference_file', help='', default=None)

    commmon_defaults_group.add_argument('--alias-file', '-af',
                                        type=str,
                                        dest='alias_file',
                                        help=f'Which file with aliases to use. Default to {flict_config.DEFAULT_FLICT_ALIAS_FILE}',
                                        default=False)

    commmon_defaults_group.add_argument('--license-info-file', '-lif', type=str, dest='licenses_info_file', help='Short for applying -lmf <file> -ldf <file> -lpf <file>', default=None)

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
                        help=f'output format. Avilable formats: {OUTPUT_FORMAT_JSON}, {OUTPUT_FORMAT_TEXT}, {OUTPUT_FORMAT_MARKDOWN}, {OUTPUT_FORMAT_DOT}. Defaults to {flict_config.DEFAULT_OUTPUT_FORMAT}',
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
    parser_v.add_argument('--outbound-license', '-ol', type=str, dest='out_license', help='Outbound license for the licenses to verify compatibibility', default=None)
    parser_v.add_argument('--inbound-license', '-il', type=str, nargs='+', dest='in_license_expr', help='Inbound license(s) for the licenses to verify compatibibility', default=[])
    parser_v.add_argument('--sbom', '-s', type=str, dest='verify_sbom', help='SBoM file to verify')
    parser_v.add_argument('--sbom-dirs', '-sd', type=str, nargs='+', dest='sbom_dirs', help='Directories where SBoM files are searched for.', default='.')
    parser_v.add_argument('--flict', '-f', type=str, dest='verify_flict', help='Flict project file to verify')

    parser_v.add_argument('--manifest-file', '-mf', type=str,
                          help='verify license compatibility for project in manifest file')

    # simplify
    parser_si = subparsers.add_parser(
        'simplify', help='expand and simplify license expression')
    parser_si.set_defaults(which="simplify", func=simplify)
    parser_si.add_argument('license_expression', type=str, nargs='+',
                           help='license expression to simplify')

    # list
    parser_li = subparsers.add_parser(
        'list', help='list supported licenses')
    parser_li.set_defaults(which="list", func=list_licenses)
    parser_li.add_argument('-t', '--translations',
                           dest='list_translation',
                           action='store_true',
                           help='List translation information')

    merge_parser = subparsers.add_parser('merge', help="Merge additional licenses with OSADL's matrix. Will output to store in a file, for use with --license-matrix-file")
    merge_parser.set_defaults(which="merge", func=_merge_licenses)
    merge_parser.add_argument('--license-file', '-lf', type=str, dest='license_file', help='License file (JSON) to merge', default=None)

    # display-compatibility
    parser_d = subparsers.add_parser(
        'display-compatibility', help='display license compatibility graphically')
    parser_d.set_defaults(which="display-compatibility",
                          func=display_compatibility)
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
                          required=True)
    parser_p.add_argument('--compliance-report-file', '-crf',
                          type=str,
                          dest='report_file',
                          help='file with report as produced using "verify"',
                          required=True)

    args = parser.parse_args()

    if args.no_relicense:
        args.relicense_file = ""

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


def _merge_licenses(args):
    file_sanity_check(args.license_file)
    ret = FlictImpl(args).merge_license_db()
    flict_print(args, ret)


def list_licenses(args):
    ret = FlictImpl(args).list_licenses()
    flict_print(args, ret)


def verify(args):
    ret = FlictImpl(args).verify()
    flict_print(args, ret)


def display_compatibility(args):
    on_error = "Expected at least two licenses for checking compatibility"
    on_error_code = ReturnCodes.RET_MISSING_ARGS
    if len(args.license_expression) == 1:
        flict_exit(on_error_code, on_error)
    ret = FlictImpl(args).display_compatibility()
    flict_print(args, ret)


def suggest_outbound_candidate(args):
    ret = FlictImpl(args).suggest_outbound_candidate()
    flict_print(args, ret)


def policy_report(args):
    file_sanity_check(args.report_file)
    file_sanity_check(args.policy_file)
    ret = FlictImpl(args).policy_report()
    flict_print(args, ret)


def file_sanity_check(fname):
    on_error = "Provided file {fname} was not found, or cannot be read."
    on_error_code = ReturnCodes.RET_FILE_NOT_FOUND
    try:
        open(fname).close()
    except (FileNotFoundError, PermissionError):
        flict_exit(on_error_code, on_error.format(fname=fname))


def main():
    args = parse()

    logger.setup(args.debug_license, args.verbose)

    if 'which' in args:
        try:
            args.func(args)
        except FlictError as e:
            flict_exit(e.error_code(), e.error_message())

    else:
        flict_exit(ReturnCodes.RET_MISSING_ARGS, "Missing command.")

    flict_exit(ReturnCodes.RET_SUCCESS)


if __name__ == '__main__':
    main()
