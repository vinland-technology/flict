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

class DotFormatter(FormatInterface):

    def format_support_licenses(self, compatibility):
        return None
    
    def format_license_list(self, license_list):
        return None

    def format_report(self, report):
        return None
 
    def format_license_combinations(self, project):
        return None
       
    def format_outbound_license(self, suggested_outbounds):
        return None
        
    def format_license_combinations(self, combinations):
        return None

    def format_compats(self, compats):
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
        return result
    
# help functions

def _licenses_hash(a, b):
    separator = " "
    if a > b:
        return a + separator + b
    else:
        return b + separator + a

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

    
