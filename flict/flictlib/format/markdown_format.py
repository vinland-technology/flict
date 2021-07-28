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

from flict.flictlib.format.format import FormatInterface
from flict.flictlib import logger

class MarkdownFormatter(FormatInterface):


compat_interprets = {
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


def _compat_to_fmt(comp_left, comp_right, fmt):
    left = compat_interprets['left'][comp_left][fmt]
    right = compat_interprets['right'][comp_right][fmt]
    return str(right) + str(left)


def _compat_to_markdown(left, comp_left, right, comp_right):
    return _compat_to_fmt(comp_left, comp_right, "markdown")

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
    
