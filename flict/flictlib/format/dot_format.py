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
from flict.flictlib.format.format import FlictFormatter
from flict.flictlib.format.markdown_format import _compat_to_markdown
from flict.flictlib.return_codes import FlictError, ReturnCodes


class DotFormatter(FlictFormatter):

    def format_compats(self, compats):
        checked_set = set()
        result = []
        result.append("digraph depends {\n    node [shape=plaintext]\n")
        for compat in compats['compatibilities']:
            #print("checked: " + str(checked_set))
            main_license = compat['license']
            for lic in compat['licenses']:
                inner_license = lic['license']
                #print("main: " + main_license + " <---> " + inner_license)
                if main_license == inner_license:
                    #print("skip same:      " + main_license + " "+ inner_license)
                    continue
                text_hash = _licenses_hash(main_license, inner_license)
                # If already handled, continue
                if text_hash in checked_set:
                    #print("skip text_hash: " + text_hash)
                    continue

                checked_set.add(text_hash)
                comp_left = lic['compatible_left']
                comp_right = lic['compatible_right']
                # print(json.dumps(compat))
                # print(json.dumps(lic))
                compat_dot = _compat_to_dot(
                    main_license, comp_left, inner_license, comp_right)
                if compat_dot != "":
                    result.append(f"    {compat_dot}\n")
        result.append('}\n')
        return " ".join(result)

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
    else:
        FlictError(ReturnCodes.RET_INTERNAL_ERROR,
                   f"Invalid state in dot_format: {left}, {comp_left}, {right}, {comp_right}")
