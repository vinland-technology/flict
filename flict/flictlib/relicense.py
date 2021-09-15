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

DESCRIPTION = """
NAME
  relicense.py

DESCRIPTION
  Add possibe relicensing for licenses

"""

EPILOG = """
AUTHOR
  Henrik Sandklef

REPORTING BUGS
  File a ticket at https://github.com/vinland-technology/flict/issues

COPYRIGHT
  Copyright (c) 2020 Henrik Sandklef<hesa@sandklef.com>.
  License GPL-3.0-or-larer

SEE ALSO
  yoga (yoda's generic aggregator)
  yocr (yoga's compliance reporter)
  flict (FOSS License Compatibility Tool)
"""


def parse():
    parser = argparse.ArgumentParser(
        description=DESCRIPTION,
        epilog=EPILOG,
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
