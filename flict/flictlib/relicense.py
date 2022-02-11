#!/usr/bin/env python3

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
PROGRAM_VERSION = "0.1"

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
  License GPL-3.0-or-later

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
    return args


def read_relicense_file(relicense_file):
    with open(relicense_file) as fp:
        relicense_object = json.load(fp)
        relicense_list = relicense_object["relicense_definitions"]

    relicense_map = {}
    for item in relicense_list:
        #print("item: " + str(item))
        relicense_map[item['spdx']] = item

    return {
        'original': relicense_object,
        'relicense_map': relicense_map
    }


def relicense_license(rel_map, license_expression):
    new_license = []
    for spdx in license_expression.replace("(", " ( ").replace(")", " ) ").split():
        if spdx in rel_map['relicense_map']:
            rel_license = ' OR '.join(rel_map['relicense_map'][spdx]["later"])
            new_license.append(f' ( {rel_license} ) ')
        else:
            new_license.append(spdx)
    return ' '.join(new_license)
