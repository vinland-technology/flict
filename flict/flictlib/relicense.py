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

import argparse
import json
from flict.flictlib.translator import read_translations, read_packages_file
from argparse import RawTextHelpFormatter

#
#
#
PROGRAM_NAME = "relicense.py"
PROGRAM_DESCRIPTION = "Add possibe relicensing for licenses "
PROGRAM_VERSION = "0.1"
PROGRAM_URL = "https://github.com/vinland-technology/compliance-utils"  # TODO
PROGRAM_COPYRIGHT = "(c) 2020 Henrik Sandklef<hesa@sandklef.com>"
PROGRAM_LICENSE = "GPL-3.0-or-larer"
PROGRAM_AUTHOR = "Henrik Sandklef"
PROGRAM_SEE_ALSO = "yoga (yoda's generic aggregator)\n  yocr (yoga's compliance reporter)\n  flict (FOSS License Compatibility Tool)"

DEFAULT_RELICENSE_FILE = "relicensing.json"


def parse():

    description = "NAME\n  " + PROGRAM_NAME + "\n\n"
    description = description + "DESCRIPTION\n  " + PROGRAM_DESCRIPTION + "\n\n"

    epilog = ""
    epilog = epilog + "AUTHOR\n  " + PROGRAM_AUTHOR + "\n\n"
    epilog = epilog + "REPORTING BUGS\n  File a ticket at " + PROGRAM_URL + "\n\n"
    epilog = epilog + "COPYRIGHT\n  Copyright " + \
        PROGRAM_COPYRIGHT + ".\n  License " + PROGRAM_LICENSE + "\n\n"
    epilog = epilog + "SEE ALSO\n  " + PROGRAM_SEE_ALSO + "\n\n"

    parser = argparse.ArgumentParser(
        description=description,
        epilog=epilog,
        formatter_class=RawTextHelpFormatter,
    )
    parser.add_argument('-f', '--relicense-file',
                        type=str,
                        dest='relicense_file',
                        help='files with relicense definitions, default is ' + DEFAULT_RELICENSE_FILE,
                        default=DEFAULT_RELICENSE_FILE)
    args = parser.parse_args()

    global VERBOSE
    VERBOSE = args.verbose

    return args


def read_relicense_file(relicense_file):
    with open(relicense_file) as fp:
        relicense_object = json.load(fp)
        relicense_list = relicense_object["relicense_definitions"]

    relicense_map = {}
    for item in relicense_list:
        #print("item: " + str(item))
        relicense_map[item['spdx']] = item

    relicense_data = {}
    relicense_data['original'] = relicense_object
    relicense_data['relicense_map'] = relicense_map

    return relicense_data


def relicense_license(rel_map, license_expression):
    new_license = ""
    for spdx in license_expression.replace("(", " ( ").replace(")", " ) ").split():
        if spdx in rel_map['relicense_map']:
            rel_license = None
            for license in rel_map['relicense_map'][spdx]["later"]:
                if rel_license is None:
                    rel_license = " ( " + license
                else:
                    rel_license = rel_license + " OR " + license + " "
            rel_license = rel_license + ") "

            new_license = new_license + " " + rel_license
        else:
            new_license = new_license + " " + spdx
    return new_license


def main():

    args = parse()
    translations = read_translations(args.translations_file)

    if (args.package_file is not None):
        packages = read_packages_file(args.package_file, translations)
        print(json.dumps(packages))
    elif (args.graph):
        print("digraph graphname {")
        first = True
        for trans in translations:
            t_value = trans["value"]
            t_spdx = trans["spdx"]
            print("\"" + t_value + "\" -> \"" + t_spdx + "\"")
            if first:
                pipe = ""
            else:
                pipe = "|"
                if (t_spdx != ""):
                    print(pipe + " sed -e 's," + t_value +
                          "\\([ |&\\\"]\\)," + t_spdx + "\\1,g' ", end="")
                first = False
        print("}")


if __name__ == "__main__":
    main()
