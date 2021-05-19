#!/bin/python3

# SPDX-FileCopyrightText: 2021 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later

from argparse import RawTextHelpFormatter
import argparse

import flict.flictlib.license
from flict.flictlib.license import LicenseHandler
from flict.flictlib.license import ManagedLicenseExpression
from flict.flictlib.license import license_to_string_long
import flict.flictlib.relicense 
from flict.flictlib.project import Project
from flict.flictlib.report import Report
from flict.flictlib.policy import Policy
from flict.flictlib.compatibility import Compatibility
from flict.flictlib.compat_matrix import CompatibilityMatrix
from flict.flictlib import logger

import json
import os
import subprocess

SCRIPT_DIR=os.path.dirname(os.path.realpath(__file__))

# TODO: replace this with something that makes installation easy
VAR_DIR = SCRIPT_DIR + "/var/"
DEFAULT_TRANSLATIONS_FILE = VAR_DIR + "translation.json"
DEFAULT_GROUP_FILE        = VAR_DIR + "license-group.json"
DEFAULT_RELICENSE_FILE    = VAR_DIR + "relicense.json"
DEFAULT_SCANCODE_FILE     = VAR_DIR + "scancode-licenses.json"
DEFAULT_MATRIX_FILE       = VAR_DIR + "osadl-matrix.csv"

PROGRAM_NAME="flict (FOSS License Compatibility Tool)"
PROGRAM_DESCRIPTION="flict is a Free and Open Source Software tool to verify compatibility between licenses"
COMPLIANCE_UTILS_VERSION="__COMPLIANCE_UTILS_VERSION__"
PROGRAM_URL="https://github.com/vinland-technology/flict"
BUG_URL="https://github.com/vinland-technology/flict/issues"
PROGRAM_COPYRIGHT="(c) 2021 Henrik Sandklef<hesa@sandklef.com>"
PROGRAM_LICENSE="GPL-3.0-or-later"
PROGRAM_AUTHOR="Henrik Sandklef"
PROGRAM_SEE_ALSO=""

DEFAULT_OUTPUT_FORMAT="JSON"

DATE_FMT='%Y-%m-%d'

if COMPLIANCE_UTILS_VERSION == "__COMPLIANCE_UTILS_VERSION__":
    GIT_DIR=os.path.dirname(os.path.realpath(__file__))
    try:
        res = subprocess.check_output(["git", "describe", "--dirty", "--always"], 
                                      cwd=GIT_DIR, stderr=subprocess.DEVNULL,
                                      universal_newlines=True)
        COMPLIANCE_UTILS_VERSION=res.strip()
    except Exception as e:
        print(e)
        COMPLIANCE_UTILS_VERSION="unknown"


def parse():

    description = "NAME\n  " + PROGRAM_NAME + "\n\n"
    description = description + "DESCRIPTION\n  " + PROGRAM_DESCRIPTION + "\n\n"
    
    epilog = ""
    epilog = epilog + "AUTHOR\n  " + PROGRAM_AUTHOR + "\n\n"
    epilog = epilog + "PROJECT SITE\n  " + PROGRAM_URL + "\n\n"
    epilog = epilog + "REPORTING BUGS\n  File a ticket at " + BUG_URL + "\n\n"
    epilog = epilog + "COPYRIGHT\n  Copyright " + PROGRAM_COPYRIGHT + ".\n  License " + PROGRAM_LICENSE + "\n\n"
    epilog = epilog + "SEE ALSO\n  " + PROGRAM_SEE_ALSO + "\n\n"
    
    parser = argparse.ArgumentParser(
        description=description,
        epilog=epilog,
        formatter_class=RawTextHelpFormatter
    )
    parser.add_argument('-v', '--verbose',
                        action='store_true',
                        help='output verbose information to stderr',
                        default=False)
    
    parser.add_argument('-dl', '--debug-license',
                        action='store_true',
                        dest='debug_license',
                        help='output verbose debug information of the intermediate steps when transforming a license expression',
                        default=False)
    
    parser.add_argument('-of', '--output-format',
                        type=str,
                        dest='output_format',
                        help='output format, defaults to ' + DEFAULT_OUTPUT_FORMAT,
                        default=DEFAULT_OUTPUT_FORMAT)
    
    parser.add_argument('-rf', '--relicense-file',
                        type=str,
                        dest='relicense_file',
                        help='' + DEFAULT_RELICENSE_FILE,
                        default=DEFAULT_RELICENSE_FILE)

    parser.add_argument('-sf', '--scancode-file',
                        type=str,
                        dest='scancode_file',
                        help='' + DEFAULT_SCANCODE_FILE,
                        default=DEFAULT_SCANCODE_FILE)

    parser.add_argument('-es', '--enable-scancode',
                        action='store_true',
                        dest='enable_scancode',
                        help='Enable Scancode\'s db - experimental so use with care',
                        default=False)

    parser.add_argument('-nr', '--no-relicense',
                        action='store_true',
                        dest='no_relicense',
                        help='do not use license relicensing, same as -rf ""',
                        default=False)
    
    parser.add_argument('-mf', '--matrix-file',
                        type=str,
                        dest='matrix_file',
                        help='' + DEFAULT_MATRIX_FILE,
                        default=DEFAULT_MATRIX_FILE)

    parser.add_argument('-crf', '--compliance-report-file',
                        type=str,
                        dest='compliance_report_file',
                        help='' )

    parser.add_argument('-pf', '--project-file',
                        type=str,
                        dest='project_file',
                        help='')

    parser.add_argument('-cc', '--check-compatibility',
                        type=str, nargs='+',
                        dest='licenses',
                        help='licenses to check for compatibility')

    parser.add_argument('-ol', '--outbound-license',
                        type=str,
                        dest='outbound_licenses',
                        help='conclude outbound license suggestions from specified license expression. Example: -ol "GPLv2 and MIT BSD-3"')

    parser.add_argument('-el', '--extended-licenses',
                        action='store_true',
                        dest='extended_licenses',
                        help='Check all supported licenes when trying to find an outbound license',
                        default=False)

    parser.add_argument('-tf', '--translations-file',
                        type=str,
                        dest='translations_file',
                        help='' + DEFAULT_TRANSLATIONS_FILE,
                        default=DEFAULT_TRANSLATIONS_FILE)

    parser.add_argument('-gf', '--group-file',
                        type=str,
                        dest='license_group_file',
                        help='' + DEFAULT_GROUP_FILE,
                        default=DEFAULT_GROUP_FILE)

    parser.add_argument('-lpf', '--license-policy-file',
                        type=str,
                        dest='policy_file',
                        help='')

    parser.add_argument('-lpl', '--list-project_licenses',
                        action='store_true',
                        dest='list_project_licenses',
                        help='output the licenses in the specified project')

    parser.add_argument('-lsl', '--list-supported-licenses',
                        action='store_true',
                        dest='list_supported_licenses',
                        help='output the licenses supported by flict')

    parser.add_argument('-lslg', '--list-supported-license-groups',
                        action='store_true',
                        dest='list_supported_license_groups',
                        help='output the license groups supported by flict')

    parser.add_argument('-n', '--new',
                        action='store_true',
                        dest='new',
                        help='try new feature')

    parser.add_argument('-lg', '--license-group',
                        dest='license_group',
                        help='outpur group (if any) for license')

    parser.add_argument('-lcc', '--license-combination-count',
                        action='store_true',
                        dest='license_combination_count',
                        help='output the number of license combinations in the specified project')

    parser.add_argument('-le', '--license-expression',
                        type=str,
                        dest='license_expression',
                        help='')

    parser.add_argument('-les', '--license-expression-states',
                        type=str,
                        dest='license_expression_states',
                        help='')

    parser.add_argument('-V', '--version',
                        action='version',
                        version=COMPLIANCE_UTILS_VERSION,
                        default=False)

    args = parser.parse_args()

    if args.no_relicense:
        args.relicense_file = ""

    if not args.enable_scancode:
        args.scancode_file = None

    return args

def _check_compatibilities(matrix_file, licenses, verbose=True):
        l_fmt = "%-20s"
        compat_matrix = CompatibilityMatrix(matrix_file)
        compats=[]
        for license_a in licenses:
            
            result = True
            lic_str = str(l_fmt) % license_a
            print(lic_str)
            compatible = True
            inner_licenses=[]
            for license_b in licenses:
                lic_str = str(" * " + l_fmt + ": ") % (license_b)
                comp = compat_matrix.a_compatible_with_b(license_a, license_b)
                result = result & comp
                if verbose:
                    print(lic_str + " " + str(comp))
                inner_compat={}
                inner_compat['license']=license_b
                inner_compat['compatible']=result
                compatible = compatible & result
                inner_licenses.append(inner_compat)
                
            if result:
                lic_str = str(l_fmt + "   :  ") % ("Outbound " + license_a)
                print(lic_str, end="")
                print(str(result))
                print("")
            compat={}
            compat['license']=license_a
            compat['licenses']=inner_licenses
            if compatible:
                compat['outbound']=license_a
            else:
                compat['outbound']=None                
            compats.append(compat)
        print("compats:\n"  + json.dumps(compats))
        return compats

def output_license_list(license_list, output_format):
    if output_format.lower() == "json":
        print(json.dumps(license_list))
    elif output_format.lower() == "markdown":
        logger.main_logger.error("MARKDOWN COMING SOON: " + str(license_list))
    else:
        logger.main_logger.error("Error, unsupported format: \"" + output_format + "\"")
        exit(1)
    
def output_compat(compats, output_format, verbose=False):
    if output_format.lower() == "json":
        output_compat_json(compats, verbose)
    elif output_format.lower() == "markdown":
        output_compat_markdown(compats, verbose)
    elif output_format.lower() == "dot":
        output_compat_dot(compats, verbose)
    else:
        logger.main_logger.error("Error, unsupported format: \"" + output_format + "\"")
        exit(1)
        
def output_compat_json(compats, verbose):
    print(json.dumps(compats))

compat_interprets = {
    'left' : {
        'true':       { 'markdown': '--->' }, 
        'false':      { 'markdown': '---|' },
        'undefined':  { 'markdown': '---U' },
        'depends':    { 'markdown': '---D' },
        'question':   { 'markdown': '---Q' }
    },
    'right' : {
        'true':       { 'markdown': '<----'},
        'false':      { 'markdown': '|--' },
        'undefined':  { 'markdown': 'U---' },
        'depends':    { 'markdown': 'D---' },
        'question':   { 'markdown': 'Q---' }
    }
}

def _compat_to_fmt(comp_left, comp_right, fmt):
    left = compat_interprets['left'][comp_left][fmt]
    right = compat_interprets['right'][comp_right][fmt]
    return str(right) + str(left) 


def _compat_to_markdown(left, comp_left, right, comp_right):
    return _compat_to_fmt(comp_left, comp_right, "markdown")

def _compat_to_dot(left, comp_left, right, comp_right):
    logger.main_logger.debug("_compat_to_dot")
    
    if comp_left == "true":
        logger.main_logger.debug("left true")
        if comp_right == "true" :
            return "\"" + left + "\"  -> \"" + right  + "\" [dir=both] [color=\"darkgreen\"]"
        if comp_right == "false" :
            logger.main_logger.debug("1 dslkjsljdflskdjfljdf")
            res = "\"" + left + "\" -> \"" + right + "\"  [color=\"black\"] "
            logger.main_logger.debug(left + "    " + right)
            logger.main_logger.debug("dot:      " + res)
            logger.main_logger.debug("markdown: " + _compat_to_markdown(None, comp_left, None, comp_right))
            return res
            
        if comp_right == "question" or comp_right == "undefined" or comp_right == "depends":
            res = "\"" + right + "\" -> \"" + left + "\"  [color=\"black\"]"
            res += "\n\"" + left + "\" -> \"" + right + "\"  [color=\"gray\", style=\"dotted\"] \n "
            return res
    elif comp_left == "false":
        logger.main_logger.debug("left false")
        
        if comp_right == "true" :
            logger.main_logger.debug("left false right true")
            return "\"" + right + "\"  -> \"" + left  + "\" [color=\"black\"]"
        if comp_right == "false" :
            return "\"" + left + "\"\n    \"" + right + "\""
        if comp_right == "question" or comp_right == "undefined" or comp_right == "depends":
            return "\"" + right + "\" -> \"" + left + "\"  [color=\"gray\", style=\"dotted\"] \n "
    elif comp_left == "question" or comp_left == "undefined" or comp_left == "depends":
        logger.main_logger.debug("left QUD")
        # QUD---->
        if comp_right == "true" :
            res = "\"" + left + "\" -> \"" + right + "\"  [color=\"black\"]"
            res += "\n\"" + right + "\" -> \"" + left + "\"  [color=\"gray\", style=\"dotted\"] \n "
            return res
        # QUD----|
        if comp_right == "false" :
            return "\"" + left + "\" -> \"" + right + "\"  [color=\"gray\", style=\"dotted\"] \n "
        # QUD----Q|U|D
        if comp_right == "question" or comp_right == "undefined" or comp_right == "depends":
            res = "\"" + left + "\" -> \"" + right + "\"  [color=\"gray\", style=\"dotted\"]"
            res += "\n\"" + right + "\" -> \"" + left + "\"  [color=\"gray\", style=\"dotted\"] \n "
            return res
        
def output_compat_markdown(compats, verbose):
    l_fmt = "%-20s"
    # print(str(compats))
    result = "# License compatibilities\n\n"

    result += "# Licenses\n\n"
    for compat in compats['compatibilities']:
        result += " * " + compat['license'] + "\n"

    result += "\n\n# Compatibilities\n\n"
    for compat in compats['compatibilities']:
        main_license = compat['license']
        for lic in compat['licenses']:
            #print(str(compat))
            #print(json.dumps(compat))
            #print(json.dumps(lic))
            inner_license = lic['license']
            comp_left = lic['compatible_left']
            comp_right = lic['compatible_right']
            compat_text = _compat_to_markdown(main_license, comp_left, inner_license, comp_right)
            result += main_license + " " + compat_text + " " + inner_license + "\n\n"

    print(result)


def _licenses_hash(a, b):
    separator = " "
    if a > b:
        return a + separator + b
    else:
        return b + separator + a
        

def output_compat_dot(compats, verbose):
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
            #print(json.dumps(compat))
            #print(json.dumps(lic))
            compat_dot = _compat_to_dot(main_license, comp_left, inner_license, comp_right)
            result += "    " + compat_dot + "\n"
    result += "\n}\n"
    print(result)

def read_compliance_report(report_file):
    with open(report_file) as fp:
        return json.load(fp)

def output_supported_license_groups(compatibility, output_format):
    supported_license_groups = compatibility.supported_license_groups()
    supported_license_groups.sort()
    for lg in supported_license_groups:
        print (" " + str(lg), end="")
        if lg == "Permissive" or lg == "Public Domain":
            pass
        else:
            print(" (under consideration)", end="")
        print("")

def output_license_group_printer():
    pass

def output_license_group(compatibility, license_handler, args):
    
    for lic in license_handler.license_expression_list(args.license_group, args.extended_licenses).set_list:
        for inner_lic in lic:
            #print(" * " + str(inner_lic))
            lic_group = compatibility.license_group(inner_lic)
            if lic_group != None:
                print(inner_lic + ": " + str(lic_group))
            else:
                print(inner_lic + ": does not belong to a group, probably supported via OSADL's matrix")

def output_supported_licenses(compatibility, output_format):
    supported_licenses = compatibility.supported_licenses()
    supported_licenses.sort()
    if output_format.lower() == "json":
        print(json.dumps(supported_licenses))
    elif output_format.lower() == "markdown":
        print("MARKDOWN COMING SOON: " + str(supported_licenses))
    else:
        for l in supported_licenses:
            lic_group = compatibility.license_group(l)
            if lic_group != None:
                print (" " + str(l) + ": (" + lic_group + ")")
            else:
                print (" " + str(l))

def output_outbound_license(compatibility, license_handler, licenses, output_format, extended_licenses):
    project = Project(None, license_handler, licenses)
    license = license_handler.license_expression_list(licenses)
    report_object = Report(project, compatibility)
    report = report_object.report()
    suggested_outbounds = report['compatibility_report']['compatibilities']['outbound_suggestions']
    
    if output_format.lower() == "json":
        print(json.dumps(suggested_outbounds))
    elif output_format.lower() == "markdown":
        print("MARKDOWN COMING SOON: " + str(suggested_outbounds))
    else:
        print("For \"" + str(licenses) + "\"", end=" ")
        if suggested_outbounds != None and len(suggested_outbounds) > 0:
            print("you can chose any of the following outbound suggestions:")
            for lic in suggested_outbounds:
                print(" * " + str(lic))
        else:
            print("we found no possible outbound license")
    
def output_license_combinations(project, output_format):
    combinations = project.license_combinations()
    
    if output_format.lower() == "json":
        comb = {}
        comb['license_combinations']=combinations
        print(json.dumps(comb))
    elif output_format.lower() == "markdown":
        print("MARKDOWN COMING SOON: " + str(combinations))
    else:
        print("Error, unsupported format: \"" + output_format + "\"")
        exit(1)

def main():
    args = parse()
    logger.setup(args)

    license_handler = LicenseHandler(args.translations_file, args.relicense_file, "")
    compatibility = Compatibility(args.matrix_file, args.scancode_file, args.license_group_file, args.extended_licenses)        

    if args.licenses:
        _licenses = []
        for lic in args.licenses:
            new_lic = license_handler.translate_and_relicense(lic).replace("(","").replace(")","").replace(" ","").replace("OR"," ").replace("AND"," ").strip().split(" ")
            _licenses += new_lic
            #print(lic + " ==> " + str(new_lic) + " =====> " + str(licenses))
        #print("Check compat for: " + str(licenses))

        # Diry trick to remove all duplicates
        licenses = list(set(_licenses))

        compats = compatibility.check_compatibilities(licenses, args.extended_licenses)
        output_compat(compats, args.output_format, args.verbose)

    elif args.outbound_licenses:        
        output_outbound_license(compatibility, license_handler, args.outbound_licenses, args.output_format, args.extended_licenses)
        
    elif args.list_supported_licenses:
        output_supported_licenses(compatibility, args.output_format)
        
    elif args.list_supported_license_groups:
        output_supported_license_groups(compatibility, args.output_format)
        
    elif args.license_expression_states:
        managed_license = license_handler.license_expression_list(args.license_expression_states)
        print(license_to_string_long(managed_license))
        
    elif args.license_expression:
        license = license_handler.license_expression_list(args.license_expression)
        if args.verbose:
            license._debug_license(license)
            print(license_to_string_long(license))
        else:
            print(license.simplified)
            
    elif args.compliance_report_file:
        if args.policy_file == None:
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
        combined_license = project.new_license_set(license_handler)
        
    else:
        project = Project(args.project_file, license_handler)
        if project == None:
            logger.main_logger.error("Could not read project file \"" + args.project_file + "\"")
            exit(4)
            
        if args.list_project_licenses:
            output_license_list(list(project.license_set()), args.output_format)
        elif args.license_combination_count:
            output_license_combinations(project, args.output_format)

        #print(str(project.project_combination_list()))


        else:
                
            report = Report(project, compatibility)

            print(json.dumps(report.report()))
            exit(0)

            if report.report() == None:
                exit(20)
            else:
                exit(0)
            
            
            
if __name__ == '__main__':
    main()
    
    
