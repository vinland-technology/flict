#!/bin/python3

# SPDX-FileCopyrightText: 2021 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later

from argparse import RawTextHelpFormatter
import argparse

from flict.flictlib.license import LicenseHandler
from flict.flictlib.license import license_to_string_long
from flict.flictlib.project import Project
from flict.flictlib.report import Report
from flict.flictlib.policy import Policy
from flict.flictlib.compatibility import Compatibility
from flict.flictlib.compat_matrix import CompatibilityMatrix
from flict.flictlib.flict_config import flict_version
from flict.flictlib import logger

import flict.flictlib.report 

from flict.flictlib.format.factory import FormatFactory
from flict.flictlib.format.format import FormatInterface

import json
import os
import sys

#REMOVE
import logging


SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))

# TODO: replace this with something that makes installation easy
VAR_DIR = SCRIPT_DIR + "/var/"
DEFAULT_TRANSLATIONS_BASE_FILE = "translation.json"
DEFAULT_GROUP_BASE_FILE = "license-group.json"
DEFAULT_RELICENSE_BASE_FILE = "relicense.json"
DEFAULT_SCANCODE_BASE_FILE = "scancode-licenses.json"
DEFAULT_MATRIX_BASE_FILE = "osadl-matrix.csv"

DEFAULT_TRANSLATIONS_FILE = VAR_DIR + DEFAULT_TRANSLATIONS_BASE_FILE
DEFAULT_GROUP_FILE = VAR_DIR + DEFAULT_GROUP_BASE_FILE
DEFAULT_RELICENSE_FILE = VAR_DIR + DEFAULT_RELICENSE_BASE_FILE
DEFAULT_SCANCODE_FILE = VAR_DIR + DEFAULT_SCANCODE_BASE_FILE
DEFAULT_MATRIX_FILE = VAR_DIR + DEFAULT_MATRIX_BASE_FILE

PROGRAM_NAME = "flict (FOSS License Compatibility Tool)"
PROGRAM_DESCRIPTION = "flict is a Free and Open Source Software tool to verify compatibility between licenses"
PROGRAM_URL = "https://github.com/vinland-technology/flict"
BUG_URL = "https://github.com/vinland-technology/flict/issues"
PROGRAM_COPYRIGHT = "(c) 2021 Henrik Sandklef<hesa@sandklef.com>"
PROGRAM_LICENSE = "GPL-3.0-or-later"
PROGRAM_AUTHOR = "Henrik Sandklef"
PROGRAM_SEE_ALSO = ""

DEFAULT_OUTPUT_FORMAT = "JSON"

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
           
            FlictSetup._instance = FlictSetup(license_handler, compatibility, args.output_format, args.output)
            
            logger.main_logger.debug(" flict_setup: " + str(FlictSetup._instance))
        return FlictSetup._instance
    

        
def parse():

    description = "NAME\n  " + PROGRAM_NAME + "\n\n"
    description = description + "DESCRIPTION\n  " + PROGRAM_DESCRIPTION + "\n\n"

    epilog = ""
    epilog = epilog + "CONFIGURATION\n  All config files can be found in\n  " + VAR_DIR + "\n\n"
    epilog = epilog + "AUTHOR\n  " + PROGRAM_AUTHOR + "\n\n"
    epilog = epilog + "PROJECT SITE\n  " + PROGRAM_URL + "\n\n"
    epilog = epilog + "REPORTING BUGS\n  File a ticket at " + BUG_URL + "\n\n"
    epilog = epilog + "COPYRIGHT\n  Copyright " + \
        PROGRAM_COPYRIGHT + ".\n  License " + PROGRAM_LICENSE + "\n\n"
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
                        help='File with group definitions, defaults to' + DEFAULT_GROUP_BASE_FILE + ". EXPERIMENTAL",
                        default=DEFAULT_GROUP_FILE)

    # DEFAULTS
    commmon_defaults_group.add_argument('-mf', '--matrix-file',
                        type=str,
                        dest='matrix_file',
                        help='File with license compatibility matrix, defaults to ' + DEFAULT_MATRIX_BASE_FILE,
                        default=DEFAULT_MATRIX_FILE)

    # DEFAULTS
    commmon_defaults_group.add_argument('-rf', '--relicense-file',
                                        type=str,
                                        dest='relicense_file',
                                        help='File with relicensing information, defaults to ' + DEFAULT_RELICENSE_BASE_FILE,
                                        default=DEFAULT_RELICENSE_FILE)
    # DEFAULTS
    commmon_defaults_group.add_argument('-sf', '--scancode-file',
                        type=str,
                        dest='scancode_file',
                        help='File with scancode licenseses information, defaults to ' + DEFAULT_SCANCODE_BASE_FILE + ". EXPERIMENTAL",
                        default=DEFAULT_SCANCODE_FILE)

    # DEFAULTS
    commmon_defaults_group.add_argument('-tf', '--translations-file',
                        type=str,
                        dest='translations_file',
                        help='File with license translations, defaults to' + DEFAULT_TRANSLATIONS_BASE_FILE,
                        default=DEFAULT_TRANSLATIONS_FILE)

    #parser.add_argument('mode',
    #                    type=str,
    #                    help='list, exportpackage, find, create-config',
    #                    default='list')



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
                        help='output format, defaults to ' + DEFAULT_OUTPUT_FORMAT,
                        default=DEFAULT_OUTPUT_FORMAT)


    parser.add_argument('-v', '--verbose',
                        action='store_true',
                        help='output verbose information to stderr',
                        default=False)


    #parser.add_argument('-crf', '--compliance-report-file',
    #                    type=str,
    #                    dest='File with compliance report',
    #                    help='')

    # DONE
    #parser.add_argument('-pf', '--project-file',
    #                    type=str,
    #                    dest='project_file',
    #                    help='')

    parser.add_argument('-cc', '--check-compatibility',
                        type=str, nargs='+',
                        dest='licenses',
                        help='licenses to check for compatibility')

    
    parser.add_argument('-ol', '--outbound-license',
                        type=str,
                        dest='outbound_licenses',
                        help='conclude outbound license suggestions from specified license expression. Example: -ol "GPLv2 and MIT BSD-3"')


    #DONE
    #parser.add_argument('-lpf', '--license-policy-file',
    #                    type=str,
    #                    dest='policy_file',
    #                    help='')

    #DONE
    #parser.add_argument('-lpl', '--list-project_licenses',
    #                    action='store_true',
    #                    dest='list_project_licenses',
    #                    help='output the licenses in the specified project')

    # DONE
    #parser.add_argument('-lsl', '--list-supported-licenses',
    #                    action='store_true',
    #                    dest='list_supported_licenses',
    #                    help='output the licenses supported by flict')

    # DONE
    #parser.add_argument('-lslg', '--list-supported-license-groups',
    #                    action='store_true',
    #                    dest='list_supported_license_groups',
    #                    help='output the license groups supported by flict')

    
    # DONE
    #parser.add_argument('-lg', '--license-group',
    #                    dest='license_group',
    #                    help='output group (if any) for license')

    #DONE
    #parser.add_argument('-lcc', '--license-combination-count',
    #                    action='store_true',
    #                    dest='license_combination_count',
    #                    help='output the number of license combinations in the specified project')

    # DONE
    #parser.add_argument('-le', '--license-expression',
    #                    type=str,
    #                    dest='license_expression',
    #                    help='')

    # SKIP - ONLY DEVEL
    #parser.add_argument('-les', '--license-expression-states',
    #                    type=str,
    #                    dest='license_expression_states',
    #                    help='')

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
    parser_v = subparsers.add_parser('verify', help='verify license compatibility')
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
    parser_si = subparsers.add_parser('simplify', help='expand and simplify license expression')
    parser_si.set_defaults(which="simplify", func=simplify)
    parser_si.add_argument('license_expression', type=str, nargs='+', 
                          help='license expression to suggest outbound license for')

    # list
    parser_li = subparsers.add_parser('list', help='list supported licenses or groups')
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
    parser_d = subparsers.add_parser('display-compatibility', help='display license compatibility graphically')
    parser_d.set_defaults(which="display-compatibility", func=display_compatibility)
    parser_d.add_argument('--graph', '-g', type=str, help='create graph representation')
    parser_d.add_argument('--table', '-t', type=str, help='create table representation')
    parser_d.add_argument('licenses', type=str, nargs='+', 
                          help='license expression to display compatibility for')

    # suggest-outbound
    parser_s = subparsers.add_parser('suggest-outbound', help='suggest outbound license')
    parser_s.set_defaults(which="suggest-outbound", func=suggest_outbound)
    parser_s.add_argument('license_expression', type=str, nargs='+', 
                          help='license expression to suggest outbound license for')

    # policy-report
    parser_p = subparsers.add_parser('policy-report', help='create report with license policy applied')
    parser_p.set_defaults(which="policy-report", func=policy_report)
    parser_p.add_argument('--license-policy-file', '-lpf',
                          type=argparse.FileType('r'),
                          dest='policy_file',                          
                          help='file with license policy')
    parser_p.add_argument('--compliance-report-file', '-crf',
                          type=argparse.FileType('r'),
                          help='file with report as produced using \'verify\'')

    args = parser.parse_args()

    if args.no_relicense:
        args.relicense_file = ""

    if not args.enable_scancode:
        args.scancode_file = None

    return args


# TODO_REMOVE
def obsoleted__check_compatibilities(matrix_file, licenses, verbose=True):
    l_fmt = "%-20s"
    compat_matrix = CompatibilityMatrix(matrix_file)
    compats = []
    for license_a in licenses:

        result = True
        lic_str = str(l_fmt) % license_a
        print(lic_str)
        compatible = True
        inner_licenses = []
        for license_b in licenses:
            lic_str = str(" * " + l_fmt + ": ") % (license_b)
            comp = compat_matrix.a_compatible_with_b(license_a, license_b)
            result = result & comp
            if verbose:
                print(lic_str + " " + str(comp))
            inner_compat = {}
            inner_compat['license'] = license_b
            inner_compat['compatible'] = result
            compatible = compatible & result
            inner_licenses.append(inner_compat)

        if result:
            lic_str = str(l_fmt + "   :  ") % ("Outbound " + license_a)
            print(lic_str, end="")
            print(str(result))
            print("")
        compat = {}
        compat['license'] = license_a
        compat['licenses'] = inner_licenses
        if compatible:
            compat['outbound'] = license_a
        else:
            compat['outbound'] = None
        compats.append(compat)
    print("compats:\n" + json.dumps(compats))
    return compats




# TODO: REMOVE
def _obsolete_output_compat(compats):
    print (" ===========================")
    if output_format.lower() == "json":
        output_compat_json(compats, verbose)
    elif output_format.lower() == "markdown":
        output_compat_markdown(compats, verbose)
    elif output_format.lower() == "dot":
        output_compat_dot(compats, verbose)
    else:
        logger.main_logger.error(
            "Error, unsupported format: \"" + output_format + "\"")
        exit(1)


# TODO: REMOVE
def _obsolete_output_compat_json(compats, verbose):
    print(json.dumps(compats))


# TODO: REMOVE
_obsolete_compat_interprets = {
    'left': {
        'true':       {'markdown': '--->'},
        'false':      {'markdown': '---|'},
        'undefined':  {'markdown': '---U'},
        'depends':    {'markdown': '---D'},
        'question':   {'markdown': '---Q'},
    },
    'right': {
        'true':       {'markdown': '<----'},
        'false':      {'markdown': '|--'},
        'undefined':  {'markdown': 'U---'},
        'depends':    {'markdown': 'D---'},
        'question':   {'markdown': 'Q---'},
    },
}


# TODO_ REMOVE
def _compat_to_fmt(comp_left, comp_right, fmt):
    left = compat_interprets['left'][comp_left][fmt]
    right = compat_interprets['right'][comp_right][fmt]
    return str(right) + str(left)


# TODO_ REMOVE
def _compat_to_markdown(left, comp_left, right, comp_right):
    return _compat_to_fmt(comp_left, comp_right, "markdown")

# TODO_ REMOVE
def _compat_to_dot(left, comp_left, right, comp_right):
    logger.main_logger.debug("_compat_to_dot")

    if comp_left == "true":
        logger.main_logger.debug("left true")
        if comp_right == "true":
            return "\"" + left + "\"  -> \"" + right + "\" [dir=both] [color=\"darkgreen\"]"
        if comp_right == "false":
            logger.main_logger.debug("1 dslkjsljdflskdjfljdf")
            res = "\"" + left + "\" -> \"" + right + "\"  [color=\"black\"] "
            logger.main_logger.debug(left + "    " + right)
            logger.main_logger.debug("dot:      " + res)
            logger.main_logger.debug(
                "markdown: " + _compat_to_markdown(None, comp_left, None, comp_right))
            return res

        if comp_right == "question" or comp_right == "undefined" or comp_right == "depends":
            res = "\"" + right + "\" -> \"" + left + "\"  [color=\"black\"]"
            res += "\n\"" + left + "\" -> \"" + right + \
                "\"  [color=\"gray\", style=\"dotted\"] \n "
            return res
    elif comp_left == "false":
        logger.main_logger.debug("left false")

        if comp_right == "true":
            logger.main_logger.debug("left false right true")
            return "\"" + right + "\"  -> \"" + left + "\" [color=\"black\"]"
        if comp_right == "false":
            return "\"" + left + "\"\n    \"" + right + "\""
        if comp_right == "question" or comp_right == "undefined" or comp_right == "depends":
            return "\"" + right + "\" -> \"" + left + "\"  [color=\"gray\", style=\"dotted\"] \n "
    elif comp_left == "question" or comp_left == "undefined" or comp_left == "depends":
        logger.main_logger.debug("left QUD")
        # QUD---->
        if comp_right == "true":
            res = "\"" + left + "\" -> \"" + right + "\"  [color=\"black\"]"
            res += "\n\"" + right + "\" -> \"" + left + \
                "\"  [color=\"gray\", style=\"dotted\"] \n "
            return res
        # QUD----|
        if comp_right == "false":
            return "\"" + left + "\" -> \"" + right + "\"  [color=\"gray\", style=\"dotted\"] \n "
        # QUD----Q|U|D
        if comp_right == "question" or comp_right == "undefined" or comp_right == "depends":
            res = "\"" + left + "\" -> \"" + right + \
                "\"  [color=\"gray\", style=\"dotted\"]"
            res += "\n\"" + right + "\" -> \"" + left + \
                "\"  [color=\"gray\", style=\"dotted\"] \n "
            return res


# TODO: REMOVE
def _obsolete_output_compat_markdown(compats, verbose):
    # print(str(compats))
    result = "# License compatibilities\n\n"

    result += "# Licenses\n\n"
    for compat in compats['compatibilities']:
        result += " * " + compat['license'] + "\n"

    result += "\n\n# Compatibilities\n\n"
    for compat in compats['compatibilities']:
        main_license = compat['license']
        for lic in compat['licenses']:
            # print(str(compat))
            # print(json.dumps(compat))
            # print(json.dumps(lic))
            inner_license = lic['license']
            comp_left = lic['compatible_left']
            comp_right = lic['compatible_right']
            compat_text = _compat_to_markdown(
                main_license, comp_left, inner_license, comp_right)
            result += main_license + " " + compat_text + " " + inner_license + "\n\n"

    print(result)


# TODO: REMOVE
def _obsolete__licenses_hash(a, b):
    separator = " "
    if a > b:
        return a + separator + b
    else:
        return b + separator + a


# TODO: REMOVE
def _obsolete__obsolete_output_compat_dot(compats, verbose):
    checked_set = set()
    result = "digraph depends {\n    node [shape=plaintext]\n"
    for compat in compats['compatibilities']:
        #print("checked: " + str(checked_set))
        main_license = compat['license']
        for lic in compat['licenses']:
            inner_license = lic['license']
            text_hash = _licenses_hash(main_license, inner_license)
            # If already handled, continue
            if text_hash in checked_set:
                #print(text_hash + " already handled")
                continue
            checked_set.add(text_hash)
            comp_left = lic['compatible_left']
            comp_right = lic['compatible_right']
            # print(json.dumps(compat))
            # print(json.dumps(lic))
            compat_dot = _compat_to_dot(
                main_license, comp_left, inner_license, comp_right)
            result += "    " + compat_dot + "\n"
    result += "\n}\n"
    print(result)


def read_compliance_report(report_file):
    with open(report_file) as fp:
        return json.load(fp)

def output_supported_license_groups(flict_setup):
    supported_license_groups = flict_setup.compatibility.supported_license_groups()
    supported_license_groups.sort()

    formatted = flict_setup.formatter.format_supported_license_groups(supported_license_groups)
    flict_print(flict_setup, formatted)

    return


def output_license_group(compatibility, license_handler, args):
    flict_setup = FlictSetup.get_setup(args)
    formatted = flict_setup.formatter.format_license_group(flict_setup.compatibility,
                                                           flict_setup.license_handler,
                                                           args.license_group,
                                                           args.extended_licenses)
    flict_print(flict_setup, formatted)


def flict_print(flict_setup,str):
    print(str, file=flict_setup.output)
                
def output_supported_licenses(flict_setup):
    formatted = flict_setup.formatter.format_support_licenses(flict_setup.compatibility)
    flict_print(flict_setup, formatted)

def _empty_project_report(compatibility, license_handler, licenses, output_format, extended_licenses):
    project = Project(None, license_handler, licenses)
    report_object = Report(project, compatibility)
    report = report_object.report()
    return report

def _outbound_license(compatibility, license_handler, licenses, output_format, extended_licenses):
    c_report = _empty_project_report(compatibility, license_handler, licenses, output_format, extended_licenses)
    suggested_outbounds = flict.flictlib.report.suggested_outbounds(c_report)
    #suggested_outbounds = flict.flictlib.report.suggested_outbounds(c_report)
    #suggested_outbounds = report['compatibility_report']['compatibilities']['outbound_suggestions']
    suggested_outbounds.sort()
    return suggested_outbounds

def output_outbound_license(flict_setup, licenses, output_format, extended_licenses):
    suggested_outbounds = _outbound_license(flict_setup.compatibility,
                                            flict_setup.license_handler,
                                            licenses,
                                            output_format,
                                            extended_licenses)
    formatted = flict_setup.formatter.format_outbound_license(suggested_outbounds)
    flict_print(flict_setup, formatted)


# TODO: remove
def _OBSOLETE_output_license_combinations(flict_setup, project):
    combinations = project.projects_combinations()

    if output_format.lower() == "json":
        comb = {}
        comb['license_combinations'] = combinations
        print(json.dumps(comb))
    elif output_format.lower() == "markdown":
        print("MARKDOWN COMING SOON: " + str(combinations))
    else:
        print("Error, unsupported format: \"" + output_format + "\"")
        exit(1)

def present_and_set(args, key):
    return key in args and vars(args)[key] is not None
    
        
def simplify(args):
    flict_setup = FlictSetup.get_setup(args)
    lic_str = ""
    for lic in args.license_expression:
        lic_str += " " + lic
    
    license = flict_setup.license_handler.license_expression_list(
        lic_str)
    if args.verbose:
        license._debug_license(license)
        print(license_to_string_long(license))
    else:
        print(license.simplified)
    

def list_licenses(args):
    flict_setup = FlictSetup.get_setup(args)
    if args.license_group:
        output_license_group(flict_setup.compatibility, flict_setup.license_handler, args)
    elif args.list_supported_license_groups:
        output_supported_license_groups(flict_setup)
    else:
        output_supported_licenses(flict_setup)

def verify(args):
    flict_setup = FlictSetup.get_setup(args)
    
    if present_and_set(args, 'project_file'):
        verify_project_file(args, flict_setup)
    elif present_and_set(args, 'license_expression'):
        print(" * license_expression: " + str(args.license_expression))
        verify_license_expression(args, flict_setup)
    else:
        # TODO: raise exception?
        print(" no....")

    
def verify_license_expression(args, flict_setup):
    lic_str = ""
    for lic in args.license_expression:
        lic_str += " " + lic

    # TODO: fix
    report = _empty_project_report(flict_setup.compatibility, flict_setup.license_handler,
                                   lic_str, args.output_format, args.extended_licenses)

    compats = report['compatibility_report']['compatibilities']['license_compatibilities']
    print(json.dumps(report['compatibility_report']['compatibilities']))
    exit(0)
    all_compatible = True
    for compat in compats:
        compatible = True
        print(" * " + compat['outbound'] + "    combinations: " + str(len(compat['combinations'])))
        for comb in compat['combinations']:
            compatible = compatible and comb['compatibility_status']
            print(str(comb))
            print("   * " + str(comb['combination'][0]['license']) + ": " + str(compatible))
        print(" * " + compat['outbound'] + ": " + str(comb['compatibility_status']))
    all_compatible = all_compatible and compatible 
    print(" ===> " + str(all_compatible))
    output_outbound_license(flict_setup, lic_str, args.output_format, args.extended_licenses)
        
def verify_project_file(args, flict_setup):

    project = Project(args.project_file, flict_setup.license_handler)
    if project is None:
        logger.main_logger.error(
             "Could not read project file \"" + args.project_file + "\"")
        exit(4)

    formatted = ""
    if args.list_project_licenses:
        formatted = flict_setup.formatter.format_license_list(license_list)
    
    elif args.license_combination_count:
        formatted = flict_setup.formatter.format_license_combinations(project)
    else:
        report = Report(project, flict_setup.compatibility)
        formatted = flict_setup.formatter.format_report(report)
        
    flict_print(flict_setup, formatted)

        
def display_compatibility(args):
    flict_setup = FlictSetup.get_setup(args)

    _licenses = []
    for lic in args.licenses:
        new_lic = flict_setup.license_handler.translate_and_relicense(lic).replace("(", "").replace(
                ")", "").replace(" ", "").replace("OR", " ").replace("AND", " ").strip().split(" ")
        _licenses += new_lic
            #print(lic + " ==> " + str(new_lic) + " =====> " + str(licenses))
        #print("Check compat for: " + str(licenses))

        # Diry trick to remove all duplicates
    licenses = list(set(_licenses))

    compats = flict_setup.compatibility.check_compatibilities(licenses, args.extended_licenses)

    formatted = flict_setup.formatter.format_compats(compats)
    flict_print(flict_setup, formatted)
    
def suggest_outbound(args):
    flict_setup = FlictSetup.get_setup(args)
    
    #print("suggest_outbound:    " + str(args))
    #print("verbose:             " + str(args.verbose))
    #print("license expression:: " + str(args.license_expression))
    lic_str = ""
    for lic in args.license_expression:
        lic_str += " " + lic
    
    output_outbound_license(flict_setup, lic_str, args.output_format, args.extended_licenses)

def policy_report(args):
    print("polict_report: " + str(args))
        
def main():
    args = parse()

    
    if 'which' in args:
        vargs = vars(args)
        #print("yes:  " + str(vargs['which']))
        #print("func: " + str(args.func))
        #print("---------------")
        args.func(args)
    else:
        print("no")
        print(str(args))
        
    exit(0)
    

    if args.licenses:
        _licenses = []
        for lic in args.licenses:
            new_lic = license_handler.translate_and_relicense(lic).replace("(", "").replace(
                ")", "").replace(" ", "").replace("OR", " ").replace("AND", " ").strip().split(" ")
            _licenses += new_lic
            #print(lic + " ==> " + str(new_lic) + " =====> " + str(licenses))
        #print("Check compat for: " + str(licenses))

        # Diry trick to remove all duplicates
        licenses = list(set(_licenses))

        compats = compatibility.check_compatibilities(
            licenses, args.extended_licenses)
        output_compat(compats, args.output_format, args.verbose)

    elif args.outbound_licenses:
        output_outbound_license(compatibility, license_handler,
                                args.outbound_licenses, args.output_format, args.extended_licenses)

    elif args.list_supported_licenses:
        output_supported_licenses(flict_setup)

    elif args.list_supported_license_groups:
        output_supported_license_groups(compatibility, args.output_format)

    elif args.license_expression_states:
        managed_license = license_handler.license_expression_list(
            args.license_expression_states)
        print(license_to_string_long(managed_license))

    elif args.license_expression:
        license = license_handler.license_expression_list(
            args.license_expression)
        if args.verbose:
            license._debug_license(license)
            print(license_to_string_long(license))
        else:
            print(license.simplified)

    elif args.compliance_report_file:
        if args.policy_file is None:
            logger.main_logger.error("Missing policy file.... bailing out")
            exit(23)
        policy = Policy(args.policy_file)
        report = read_compliance_report(args.compliance_report_file)
        policy_report = policy.report(report)
        ret = policy_report['policy_outbounds']['policy_result']
        print(json.dumps(policy_report))
        exit(ret)

    elif args.license_group:
        output_license_group(compatibility, license_handler, args)

    elif args.new:
        project = Project(args.project_file, license_handler)

    else:
        project = Project(args.project_file, license_handler)
        if project is None:
            logger.main_logger.error(
                "Could not read project file \"" + args.project_file + "\"")
            exit(4)

        if args.list_project_licenses:
            output_license_list(
                list(project.license_set()), args.output_format)
        elif args.license_combination_count:
            output_license_combinations(project, args.output_format)

        # print(str(project.project_combination_list()))

        else:

            report = Report(project, compatibility)

            print(json.dumps(report.report()))
            exit(0)

            # if report.report() == None:
            #     exit(20)
            # else:
            #     exit(0)


if __name__ == '__main__':
    main()
