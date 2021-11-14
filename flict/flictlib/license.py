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


from flict.flictlib.relicense import read_relicense_file
from flict.flictlib.relicense import relicense_license
from flict.flictlib.translator import read_translations
from license_expression import LicenseSymbol
from license_expression import Licensing
from flict.flictlib import logger

OR_STRING = " or "
AND_STRING = " and "

# 3

#
# debug and devel variable
#


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
        mle = {}
        mle['expanded'] = self.expanded
        mle['grouped'] = self.grouped
        mle['simplified'] = self.simplified
        #print("set_list: " + str(self.set_list))
        mle['set_list'] = self.set_list
        return mle

    def __str__(self):
        ret_str = ""
        ret_str += "license expression:                    " + str(self.license_expression)
        ret_str += "\n"
        ret_str += "translated license expression:         " + str(self.translated)
        ret_str += "\n"
        ret_str += "expanded license expression:           " + str(self.expanded)
        ret_str += "\n"
        ret_str += "grouped license expression:            " + str(self.grouped)
        ret_str += "\n"
        ret_str += "simplified license expression:         " + str(self.simplified)
        ret_str += "\n"
        ret_str += "interim license expression:            " + interim_license_expression_list_to_string(self.interim)
        ret_str += "\n"
        ret_str += "license expression list:               " + license_expression_set_list_to_string(self.set_list)
        return ret_str


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
        #print("symbols: " + str(symbols))

    def read_symbols(self, translations_files):
        symbols = []
        symbols_map = {}
        self.translations = []
        for translations_file in translations_files.split():
            #print("reading translation file: " + str(translations_file))
            translation_data = read_translations(translations_file)
            self.translations.append(translation_data)
            for lic_key in translation_data:
                #print("lic_key:  \"" + str(lic_key) + "\"")
                #print("  lic_alias:  " + str(translation_data[lic_key] ))
                #print("transl: " + str(len(self.translations)))
                if lic_key not in symbols_map:
                    symbols_map[lic_key] = set()
                for val in translation_data[lic_key]:
                    symbols_map[lic_key].add(val)

                #lic_aliases = tuple(translation_data[lic_key])
                #symbols.append(LicenseSymbol(key=key, aliases=lic_aliases))

        for key, value in symbols_map.items():
            #print("Adding to symbols: " + key)
            #print(" - " + str(value))
            symbols.append(LicenseSymbol(key=key, aliases=tuple(value)))

        # debugging
        # print("Symbols")
        # for sym in symbols:
            #print(" sym: " + (str(sym.key)))
            #print("    aliases :  " + (str(sym.aliases)))
            #l = Licensing([sym])
            #print("    licensing: " + (str(l)))

        #print("symbols: " + str(symbols))
        return symbols

    def translate_and_relicense(self, license_expression):
        license_expression = license_expression.replace(
            "&", AND_STRING).replace("|", OR_STRING)

        transl = self.translate(license_expression)
        if transl is None or not transl:
            transl = license_expression
        #print("translate_and_relicenseself: " + license_expression + " ==> " + transl)
        rel = self.expand_relicense(transl)
        if rel is None:
            rel = transl
        #print("translate_and_relicenseself: " + rel)
        return rel

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
        #parsed = self.licensing._parse_and_simplify(license_expression)
        #print("simplified: " + str(parsed.simplify()))
        # return parsed.simplify()
        return parsed.simplify()

    def license_expression_list_json(self, license_expression, relicense=True):
        license = self.license_expression_list(license_expression, relicense)
        output = {}
        output["license_expression"] = license_expression
        output["expanded"] = license.expanded
        output["grouped"] = license.grouped
        output["translated"] = license.translated
        output["simplified"] = license.simplified
        output["interim"] = license.interim
        output["set_list"] = license.set_list
        return output

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

    def interim_license_expression_list(self, _license_expression, licensing):
        """
        Transforms and boolean symbolic expression

        Turns an expression like this:
            G AND (A OR B)
        into:
            AND [G, OR [A, B]]
        The latter is an interim format.
        """
        license_expression = encode_license_expression(_license_expression)
        tokenizer = licensing.get_advanced_tokenizer()
        tokenized = tokenizer.tokenize(license_expression)
        current_license = None
        current_licenses = []
        current_op = None
        paren_expr = None
        paren_count = 0
        for token in tokenized:
            tok = token.string
            if tok == '(':
                # print("(")
                if paren_expr is None:
                    paren_expr = ""
                else:
                    paren_expr = paren_expr + " " + tok
                    paren_count = paren_count + 1
            elif tok == ')':
                #print("about to parse: \"" + paren_expr + "\"  count: " + str(paren_count))
                if paren_count == 0:
                    current_license = self.interim_license_expression_list(
                        paren_expr, licensing)
                    #print("got:            \"" + str(current_license) + "\"")
                    paren_expr = None
                else:
                    paren_count = paren_count - 1
                    paren_expr = paren_expr + " " + tok
            elif tok == 'OR' or tok == 'AND':
                if paren_expr is not None:
                    #print("TEMP " + tok)
                    paren_expr = paren_expr + " " + tok
                else:
                    #print("OPERATOR " + tok + " (" + str(current_op) + ")")
                    if current_licenses is None:
                        raise Exception(
                            "Internal failure. Failed creating interim license expression. current_licenses is None")
                    if current_op is None:
                        # first operator
                        current_op = tok
                        #print("=cop: " + tok + "   " + current_license)
                        current_licenses.append(current_license)
                    elif current_op == tok:
                        # same operator
                        #print("-cop: " + tok + "   " + current_license)
                        current_licenses.append(current_license)
                    else:
                        # different operator
                        raise Exception(
                            "Internal failure. Failed creating interim license expression.")
            else:
                #print("tok: \"" + tok + "\"")
                if paren_expr is not None:
                    paren_expr = paren_expr + " " + tok
                else:
                    current_license = tok

        current_licenses.append(current_license)
        if current_op is None:
            current_op = "AND"

        list = LicenseExpressionList(current_op, current_licenses)
        #print("DONE: " + str(license_expression) + " => " + str(list))
        return list

    def _combinations(self, lel):
        #print("lel : " + str(lel))
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
            raise Exception(
                "Internal failure. Failed identifying operator: " + str(lel))

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

        #print("Count: " + str(_combinations(interim_license_expression_list)))
        if not isinstance(interim_license_expression_list, LicenseExpressionList):
            # single license
            license_set = {decode_license_expression(interim_license_expression_list)}
            expanded_list.append(list(license_set))
            logger.license_logger.debug(
                "LEAF, returning " + str(expanded_list))
            logger.license_logger.debug(
                "cop: " + interim_license_expression_list)
            #print("managed____ \""  + str(expanded_list) + "\"  <---- MIDDLE")
            return expanded_list

        current_op = interim_license_expression_list.op
        logger.license_logger.debug("cop: " + current_op)
        for lep in interim_license_expression_list.list:
            logger.license_logger.debug(" ------ lep ----- " + str(lep))
            if current_op is None:
                raise Exception("Internal failure. No operator found")

            elif current_op == "OR":
                lep_list = self.interim_license_expression_set_list(lep)
                expanded_list = self._manage_list_item_or(
                    expanded_list, lep_list)

            elif current_op == "AND":
                lep_list = self.interim_license_expression_set_list(lep)
                expanded_list = self._manage_list_item_and(
                    expanded_list, lep_list)
        #print("managed____ \""  + str(expanded_list) + "\"  <---- FINAL")
        return expanded_list

    def _manage_list_item_and(self, license_list, lep):
        logger.license_logger.debug(" * Andy")
        if isinstance(lep, LicenseExpressionList):
            raise Exception("Internal failure. Wrong type " +
                            str(type(lep)) + " for: " + str(lep))
        else:
            # single license
            if len(license_list) == 0:
                logger.license_logger.debug("wooops: " + str(license_list))
                logger.license_logger.debug("wooops: " + str(lep))
                license_list = lep
            else:
                logger.license_logger.debug("daisy: " + str(license_list))
                logger.license_logger.debug("daisy: " + str(lep))
                logger.license_logger.debug(
                    " -------------====== Andy ====----------------- SINGLE: " + str(license_list))
                new_list = []
                for item in license_list:
                    logger.license_logger.debug(
                        "  item: " + str(item) + " <--- " + str(lep))
                    for lep_item in lep:
                        logger.license_logger.debug(
                            "    item: " + str(item) + " <--- " + str(lep_item))
                        new_item = list(set(item + lep_item))
                        logger.license_logger.debug("    item: " + str(item))
                        new_list.append(new_item)
                    logger.license_logger.debug("    list: " + str(new_list))
                license_list = new_list
            return license_list

    def _manage_list_item_or(self, license_list, lep):
        logger.license_logger.debug(" * Orleans: " + (str(lep)))
        if isinstance(lep, LicenseExpressionList):
            raise Exception("Internal failure. Wrong type " +
                            str(type(lep)) + " for: " + str(lep))
        else:
            # single license
            logger.license_logger.debug("HERE I AM .... \"" + str(lep) + "\"")
            if len(license_list) == 0:
                new_list = lep
                logger.license_logger.debug(
                    "topsss: " + str(license_list) + " size: " + str(len(license_list)))
                logger.license_logger.debug(
                    "topsss: " + str(lep) + " size: " + str(len(lep)))
                logger.license_logger.debug(
                    "topsss: " + str(new_list) + " size: " + str(len(new_list)))
            else:
                new_list = license_list
                logger.license_logger.debug("dapsss: " + str(license_list))
                logger.license_logger.debug("dappss: " + str(lep))
                for lep_item in lep:
                    logger.license_logger.debug(
                        "    item: " + str(license_list) + " <--- " + str(lep_item))
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
    res = ""
    res = res + "original:   " + license.license_expression + "\n"
    res = res + "translated: " + license.translated + "\n"
    res = res + "expanded:   " + license.expanded + "\n"
    res = res + "grouped:    " + license.grouped + "\n"
    res = res + "simplified: " + license.simplified + "\n"
    res = res + "set_list:   " + str(license.set_list) + "\n"
    return res


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
    string = op + " ["
    first = True
    for item in lel.list:
        if first:
            first = False
        else:
            string = string + ", "
        if isinstance(item, LicenseExpressionList):
            string = string + interim_license_expression_list_to_string(item)
        else:
            string = string + item

    string = string + "]"
    return string


def encode_license_expression(license_expression):
    return license_expression.replace(" WITH ", "_WITH_")


def decode_license_expression(license_expression):
    return license_expression.replace("_WITH_", " WITH ")
