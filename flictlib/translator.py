#!/usr/bin/python3

###################################################################
#
# flict - FOSS License Compatibility Tool
#
# SPDX-FileCopyrightText: 2020 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later
#
###################################################################

import json
import os
import sys
import re
from argparse import RawTextHelpFormatter
import argparse

#
#
#
PROGRAM_NAME="translator.py"
PROGRAM_DESCRIPTION="Translates license ids from misc spellings to known format (e.g SPDX)"
PROGRAM_VERSION="0.1"
PROGRAM_URL="https://github.com/vinland-technology/compliance-utils" #TODO
PROGRAM_COPYRIGHT="(c) 2020 Henrik Sandklef<hesa@sandklef.com>"
PROGRAM_LICENSE="GPL-3.0-or-larer"
PROGRAM_AUTHOR="Henrik Sandklef"
PROGRAM_SEE_ALSO="yoga (yoda's generic aggregator)\n  yocr (yoga's compliance reporter)\n  flict (FOSS License Compatibility Tool)"

DEFAULT_TRANSLATIONS_FILE="translation.json"

VERBOSE=False

def error(msg):
    sys.stderr.write(msg + "\n")

def verbose(msg):
    if VERBOSE:
        sys.stderr.write(msg)
        sys.stderr.write("\n")
        sys.stderr.flush()

def parse():

    description = "NAME\n  " + PROGRAM_NAME + "\n\n"
    description = description + "DESCRIPTION\n  " + PROGRAM_DESCRIPTION + "\n\n"
    
    epilog = ""
    epilog = epilog + "AUTHOR\n  " + PROGRAM_AUTHOR + "\n\n"
    epilog = epilog + "REPORTING BUGS\n  File a ticket at " + PROGRAM_URL + "\n\n"
    epilog = epilog + "COPYRIGHT\n  Copyright " + PROGRAM_COPYRIGHT + ".\n  License " + PROGRAM_LICENSE + "\n\n"
    epilog = epilog + "SEE ALSO\n  " + PROGRAM_SEE_ALSO + "\n\n"
    
    parser = argparse.ArgumentParser(
        description=description,
        epilog=epilog,
        formatter_class=RawTextHelpFormatter
    )
    parser.add_argument('-tf', '--translation-file',
                        type=str,
                        dest='translation_file',
                        help='files with translations, default is ' + DEFAULT_TRANSLATIONS_FILE,
                        default=DEFAULT_TRANSLATIONS_FILE)
    parser.add_argument('-p', '--package-file',
                        type=str,
                        dest='package_file',                        
                        help='file with package definition')
    parser.add_argument('-v', '--verbose',
                            action='store_true',
                        help='output verbose information to stderr',
                        default=False)
    parser.add_argument('-g', '--graph',
                        action='store_true',
                        help='create graph (dot format) over translations',
                        default=False)
    args = parser.parse_args()

    global VERBOSE
    VERBOSE=args.verbose

    return args


      
#
# TODO: update_license needs a rewrite
#       - overly complicated due to Henrik's lack of Pythonian skills
# 
def update_license(translations, license_expr):
    new_license=""
    for license in license_expr.replace("("," ( ").replace(")"," ) ").split():
        #print(" ---> test??: " + license)
        if license in translations['translations_map']:
            new_single = translations['translations_map'][license]["translation"]
            #print("TRANSLATING " + license + " ---> " + new_single)
            new_license = new_license + " " + new_single
        else:
            #print("TRANSLATING NOT " + license)
            new_license = new_license + " " + license
    #print("TRANSLATING " + license_expr + " ---> " + new_license)
    return new_license

def update_packages(translations, dependencies):
    updates_deps=[]
    for dep in dependencies:
#        print("license: \"" + dep["license"] + "\"")
        license = dep["license"].strip(' ')
        updated_license=update_license(translations, license)
        dep["license"]=updated_license
        dep_deps = dep["dependencies"]
        updates_deps = update_packages(translations, dep_deps)
    return updates_deps

def _read_translations(translations_file):
    with open(translations_file) as fp:
        translations_object = json.load(fp)
        translations=translations_object["translations"]

        translations_map={}
        for item in translations:
            if item['translation'] != None:
                translations_map[item['value']]=item
        translations_data={}
        translations_data['original']=translations_object
        translations_data['translations_map']=translations_map

        return translations_data


def read_translations(translations_file):
    symbols={}
    with open(translations_file) as fp:
        translations_object = json.load(fp)
        translations=translations_object["translations"]
        for item in translations:
            if item['translation'] != None:
                transl = item['translation']
                value = item['value']
                if not transl in symbols:
                    symbols[transl] = []
                symbols[transl].append(value)
    return symbols

    
def read_packages_file(jsonfile, translations):
  with open(jsonfile) as fp:
    packages=json.load(fp)
    # TODO: sync with flict (should be "package")
    package = packages["component"]
    deps = package["dependencies"]
    license=package["license"].strip(' ')
    package["license"]=update_license(translations, license)
    update_packages(translations, deps)
    return packages

def main():
    
    args = parse()
    translations = read_translations(args.translations_file)

    if (args.package_file != None ):
        packages = read_packages_file(args.package_file, translations)
        print(json.dumps(packages))
    elif (args.graph):
        print("digraph graphname {")
        first = True
        for trans in translations:
            t_value = trans["value"]
            t_translated = trans["translation"]
            print("\"" + t_value + "\" -> \"" + t_translated + "\"")
            if first:
                pipe=""
            else:
                pipe="|"
                if ( t_translated != "" ):
                    print(pipe + " sed -e 's," + t_value + "\\([ |&\\\"]\\)," + t_translated + "\\1,g' ", end="")
                first=False
        print("}")
        
        
if __name__ == "__main__":
  main()

