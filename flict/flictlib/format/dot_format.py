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

from flict.flictlib import logger
from flict.flictlib.format.format import FormatInterface
from flict.flictlib.format.markdown_format import _compat_to_markdown


class DotFormatter(FormatInterface):

    def format_support_licenses(self, compatibility):
        return None

    def format_license_list(self, license_list):
        return None

    def format_report(self, report):
        return None

    def format_license_project(self, project):
        return None

    def format_outbound_license(self, outbound_candidate):
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

    def format_relicense_information(self, license_handler):
        return None

    def format_translation_information(self, license_handler):
        return None

# help functions


def _licenses_hash(a, b):
    separator = " "
    if a > b:
        return a + separator + b
    else:
        return b + separator + a


def _print_compare_line(left, right, color):
    return f'"{left}" -> "{right}"  {color}'


def _compat_to_dot(left, comp_left, right, comp_right):
    logger.main_logger.debug("_compat_to_dot")

    if comp_left == "true":
        logger.main_logger.debug("left true")
        if comp_right == "true":
            return _print_compare_line(left, right, '[dir=both] [color="darkgreen"]')
        if comp_right == "false":
            logger.main_logger.debug("1 dslkjsljdflskdjfljdf")
            res = _print_compare_line(left, right, '[color="black"]')
            logger.main_logger.debug(left + "    " + right)
            logger.main_logger.debug("dot:      " + res)
            logger.main_logger.debug(
                "markdown: " + _compat_to_markdown(None, comp_left, None, comp_right))
            return res

        if comp_right == "question" or comp_right == "undefined" or comp_right == "depends":
            return f"""
            {_print_compare_line(right, left, '[color="black"]')}
            {_print_compare_line(left, right, '[color="gray", style="dotted"]')}
            """
    elif comp_left == "false":
        logger.main_logger.debug("left false")

        if comp_right == "true":
            logger.main_logger.debug("left false right true")
            return _print_compare_line(right, left, '[color="black"]')
        if comp_right == "false":
            return f'"{left}"\n    "{right}"'
        if comp_right == "question" or comp_right == "undefined" or comp_right == "depends":
            return _print_compare_line(right, left, '[color="gray", style="dotted"]') + " \n "
    elif comp_left == "question" or comp_left == "undefined" or comp_left == "depends":
        logger.main_logger.debug("left QUD")
        # QUD---->
        if comp_right == "true":
            return f"""
            {_print_compare_line(left, right, '[color="black"]')}
            {_print_compare_line(right, left, '[color="gray", style="dotted"]')}
            """
        # QUD----|
        if comp_right == "false":
            return _print_compare_line(left, right, '[color="gray", style="dotted"]') + " \n "
        # QUD----Q|U|D
        if comp_right == "question" or comp_right == "undefined" or comp_right == "depends":
            return f"""
            {_print_compare_line(left, right, '[color="gray", style="dotted"]')}
            {_print_compare_line(right, left, '[color="gray", style="dotted"]')}
            """
