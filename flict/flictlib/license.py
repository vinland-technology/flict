#!/bin/python3

###################################################################
#
# flict - FOSS License Compatibility Tool
#
# SPDX-FileCopyrightText: 2020 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later
#
###################################################################


from flict.flictlib.return_codes import FlictError
from flict.flictlib.return_codes import ReturnCodes
from flict.flictlib.relicense import read_relicense_file
from flict.flictlib.relicense import relicense_license
from flict.flictlib.translator import read_translations
from license_expression import LicenseSymbol
from license_expression import Licensing
from flict.flictlib import logger

OR_STRING = " or "
AND_STRING = " and "


class ManagedLicenseExpression:
    """
    This class contains all the different transforms of a license expression.

    translated - "&" => "and", "GPLv2+" => "GPL-2-or-later"
    expanded   - relicensed, e.g. "LGPL-2.1-or-later" => "GPL-2.0-only")
    grouped    - "keithp-x11" => "Permissive"
    simplified - simplified (boolean algebra) "MIT and MIT" => "MIT"
    interim    - for internal use only
    set_list   - see interim_license_expression_set_list()
    """

    def __init__(self, license_expression):
        self.license_expression = license_expression
        self.expanded = []
        self.grouped = []
        self.translated = []
        self.simplified = []
        self.interim = []
        self.set_list = None

    def _debug_license(self, license_expression):
        logger.license_logger.info(
            "license expression:                    " + str(self.license_expression))
        logger.license_logger.info(
            "translated license expression:         " + str(self.translated))
        logger.license_logger.info(
            "expanded license expression:           " + str(self.expanded))
        logger.license_logger.info(
            "grouped license expression:            " + str(self.grouped))
        logger.license_logger.info(
            "simplified license expression:         " + str(self.simplified))
        _debug_interim_license_expression_list(self.interim)
        _debug_license_expression_set_list(self.set_list)

    def to_json(self):
        return {
            'expanded': self.expanded,
            'grouped': self.grouped,
            'simplified': self.simplified,
            'set_list': self.set_list
        }

    def __str__(self):
        return f"""
                license expression:                    {str(self.license_expression)}
                translated license expression:         {str(self.translated)}
                expanded license expression:           {str(self.expanded)}
                grouped license expression:            {str(self.grouped)}
                simplified license expression:         {str(self.simplified)}
                interim license expression:            {interim_license_expression_list_to_string(self.interim)}
                license expression list:               {license_expression_set_list_to_string(self.set_list)}
                """


class LicenseExpressionList:
    def __init__(self, op, list):
        self.op = op
        self.list = list


class LicenseHandler:

    def __init__(self, translations_files, relicense_file, group_file):
        self.translations_files = translations_files
        self.relicense_file = relicense_file
        self.relicense_map = None
        self.group_file = group_file
        symbols = self.read_symbols(self.translations_files)
        self.licensing = Licensing(symbols)

    def read_symbols(self, translations_files):
        symbols_map = {}
        self.translations = []
        for translations_file in translations_files.split():
            translation_data = read_translations(translations_file)
            self.translations.append(translation_data)
            for lic_key in translation_data:
                if lic_key not in symbols_map:
                    symbols_map[lic_key] = set()
                for val in translation_data[lic_key]:
                    symbols_map[lic_key].add(val)

        return [LicenseSymbol(key=key, aliases=tuple(value))
                for key, value in symbols_map.items()]

    def translate_and_relicense(self, license_expression):
        transl = self.translate(license_expression)
        if not transl:
            transl = license_expression
        rel = self.expand_relicense(transl)

        return rel if rel else transl

    def expand_relicense(self, license_expression):
        if self.relicense_file is not None and self.relicense_file:
            self.relicense_map = read_relicense_file(self.relicense_file)
            expanded = relicense_license(
                self.relicense_map, license_expression)
            return expanded.strip()
        else:
            return license_expression.strip()

    def group(self, license_expression):
        return license_expression.strip()

    def translate(self, license_expression):
        license_expression = license_expression.replace(
            "&", AND_STRING).replace("|", OR_STRING)
        return str(self.simplify(license_expression))

    def simplify(self, license_expression):
        parsed = self.licensing.parse(license_expression)
        return parsed.simplify()

    def license_expression_list_json(self, license_expression, relicense=True):
        license = self.license_expression_list(license_expression, relicense)
        return {
            "license_expression": license_expression,
            "expanded": license.expanded,
            "grouped": license.grouped,
            "translated": license.translated,
            "simplified": license.simplified,
            "interim": license.interim,
            "set_list": license.set_list
        }

    def license_expression_list(self, license_expression, relicense=True):

        license = ManagedLicenseExpression(license_expression)
        license.translated = self.translate(license_expression)

        # We need str to skip verbose output
        license.simplified = str(self.simplify(license.translated))

        if relicense:
            license.expanded = self.expand_relicense(license.simplified)
        else:
            license.expanded = license.simplified

        license.grouped = self.group(license.expanded)

        license.interim = self.interim_license_expression_list(
            license.grouped, self.licensing)

        license.set_list = self.interim_license_expression_set_list(
            license.interim)

        return license

    #
    def _license_expression_list(self, license_expression, relicense=True):

        license = ManagedLicenseExpression(license_expression)
        license.translated = self.translate(license_expression)

        if relicense:
            license.expanded = self.expand_relicense(license.translated)
        else:
            license.expanded = license.translated

        license.grouped = self.group(license.expanded)

        # We need str to skip verbose output
        license.simplified = str(self.simplify(license.grouped))

        license.interim = self.interim_license_expression_list(
            license.simplified, self.licensing)

        license.set_list = self.interim_license_expression_set_list(
            license.interim)

        return license

    def interim_license_expression_list(self, license_expression, licensing):
        """
        Transforms and boolean symbolic expression

        Turns an expression like this:
            G AND (A OR B)
        into:
            AND [G, OR [A, B]]
        The latter is an interim format.
        """
        encoded = encode_license_expression(license_expression)
        tokenizer = licensing.get_advanced_tokenizer()
        tokenized = tokenizer.tokenize(encoded)
        current_license = None
        current_licenses = []
        current_op = None
        paren_expr = None
        paren_count = 0
        for token in tokenized:
            tok = token.string
            if tok == '(':
                if paren_expr is None:
                    paren_expr = ""
                else:
                    paren_expr = paren_expr + " " + tok
                    paren_count = paren_count + 1
            elif tok == ')':
                if paren_count == 0:
                    current_license = self.interim_license_expression_list(
                        paren_expr, licensing)
                    paren_expr = None
                else:
                    paren_count = paren_count - 1
                    paren_expr = paren_expr + " " + tok
            elif tok == 'OR' or tok == 'AND':
                if paren_expr is not None:
                    paren_expr = paren_expr + " " + tok
                else:
                    if current_licenses is None:
                        raise FlictError(ReturnCodes.RET_INTERNAL_ERROR,
                                         "Internal failure. Failed creating interim license expression. current_licenses is None")
                    if current_op is None:
                        # first operator
                        current_op = tok
                        current_licenses.append(current_license)
                    elif current_op == tok:
                        # same operator
                        current_licenses.append(current_license)
                    else:
                        # different operator
                        raise FlictError(ReturnCodes.RET_INTERNAL_ERROR,
                                         "Internal failure. Failed creating interim license expression.")
            else:
                if paren_expr is not None:
                    paren_expr = paren_expr + " " + tok
                else:
                    current_license = tok

        current_licenses.append(current_license)
        if current_op is None:
            current_op = "AND"

        list = LicenseExpressionList(current_op, current_licenses)
        return list

    def _combinations(self, lel):
        if not isinstance(lel, LicenseExpressionList):
            return 1
        if lel.op == "AND":
            prod = 1
            for item in lel.list:
                prod = prod * self._combinations(item)
            return prod
        elif lel.op == "OR":
            sum = 0
            for item in lel.list:
                sum = sum + self._combinations(item)
            return sum
        else:
            FlictError(ReturnCodes.RET_INTERNAL_ERROR,
                       f"Internal failure. Failed identifying operator: {lel}")

    def interim_license_expression_set_list(self, interim_license_expression_list):
        """
        Transforms a boolean symbolic expression

        Turns an expression like this:
            AND [G, OR [A, B]]
        into:
            [
              { G, A },
              { G, B }
            ]
        The latter is an interim format.
        """
        expanded_list = []

        if not isinstance(interim_license_expression_list, LicenseExpressionList):
            # single license
            license_set = {decode_license_expression(interim_license_expression_list)}
            expanded_list.append(list(license_set))
            return expanded_list

        current_op = interim_license_expression_list.op
        for lep in interim_license_expression_list.list:
            if current_op is None:
                raise FlictError(ReturnCodes.RET_INTERNAL_ERROR,
                                 "Internal failure. No operator found")

            lep_list = self.interim_license_expression_set_list(lep)
            if current_op == "OR":
                expanded_list = self._manage_list_item_or(
                    expanded_list, lep_list)

            elif current_op == "AND":
                expanded_list = self._manage_list_item_and(
                    expanded_list, lep_list)
        return expanded_list

    def _manage_list_item_and(self, license_list, lep):
        if isinstance(lep, LicenseExpressionList):
            raise FlictError(ReturnCodes.RET_INTERNAL_ERROR,
                             f"Internal failure. Wrong type {lep} for: {lep}")

        # single license
        if len(license_list) == 0:
            return lep

        new_list = []
        for item in license_list:
            for lep_item in lep:
                new_item = list(set(item + lep_item))
                new_list.append(new_item)

        return new_list

    def _manage_list_item_or(self, license_list, lep):
        if isinstance(lep, LicenseExpressionList):
            raise FlictError(ReturnCodes.RET_INTERNAL_ERROR,
                             f"Internal failure. Wrong type {lep} for: {lep}")

        # single license
        if len(license_list) == 0:
            return lep

        new_list = license_list
        for lep_item in lep:
            new_list.append(lep_item)

        return new_list

    def relicensing_information(self):
        if self.relicense_map is None:
            self.relicense_map = read_relicense_file(self.relicense_file)
        return self.relicense_map

    def translation_information(self):
        return self.translations


def _debug_license_expression_set_list(ilel):
    logger.license_logger.debug("interim license expression set list:  {i}".format(
        i=license_expression_set_list_to_string(ilel)))


def license_to_string_long(license):
    return f"""
            original:   {license.license_expression}
            translated: {license.translated}
            expanded:   {license.expanded}
            grouped:    {license.grouped}
            simplified: {license.simplified}
            set_list:   {str(license.set_list)}
            """


def license_expression_set_list_to_string(set_list):
    _sorted = [",".join(sorted(license_set)) for license_set in set_list.sort()]

    return "[{0}]".format(",".join(_sorted))


def _debug_interim_license_expression_list(lel):
    logger.license_logger.debug("interim license expression list:       {i}".format(
        i=interim_license_expression_list_to_string(lel)))


def interim_license_expression_list_to_string(lel):
    if lel.op is not None:
        op = lel.op
    else:
        op = ""

    _expr = [interim_license_expression_list_to_string(item)
             if isinstance(item, LicenseExpressionList) else item
             for item in lel.list]

    return "{0} [{1}]".format(op, ", ".join(_expr))


def encode_license_expression(license_expression):
    return license_expression.replace(" WITH ", "_WITH_")


def decode_license_expression(license_expression):
    return license_expression.replace("_WITH_", " WITH ")
