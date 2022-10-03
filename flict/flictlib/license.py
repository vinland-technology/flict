#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2022 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later

import license_expression

from flict.flictlib.return_codes import FlictError, ReturnCodes
from flict.flictlib.alias import Alias
import logging

LICENSE_SYMBOL = "LicenseSymbol"
LICENSE_WITH_SYMBOL = "LicenseWithExceptionSymbol"
LICENSE_EXPRESSION_OR = "OR"
LICENSE_EXPRESSION_AND = "AND"


class LicenseParserFactory:

    @staticmethod
    def get_parser(denied_licenses, alias=None):
        # Not much of a choice really :)
        return PrettyLicenseParser(denied_licenses, alias or Alias())


class LicenseParser:

    def __init__(self, denied_licenses, alias):
        self.alias = alias
        self._denied_licenses = denied_licenses
        self.utils = ParseUtils()

    def denied_licenses(self):
        return self._denied_licenses

    def parse_license(self, expr):
        return

    def licenses(self, expr):
        return

    def license_denied(self, license):
        if self._denied_licenses:
            return license in self._denied_licenses
        return False

    def license_allowed(self, license):
        return not self.license_denied(license)

    def is_operator(self, expr):
        return expr['type'] == "operator"

    def is_license(self, expr):
        return expr['type'] == "license"

    def operator(self, expr):
        #assert (self.is_operator(expr))
        return expr['name']

    def is_or(self, expr):
        return self.expr_operator(expr) == LICENSE_EXPRESSION_OR

    def is_and(self, expr):
        return self.operator(expr) == LICENSE_EXPRESSION_AND

    def license(self, expr):
        #assert (self.is_license(expr))
        return expr['name']

    def operands(self, expr):
        #assert (self.is_operator(expr))
        return expr['operands']


class PrettyLicenseParser(LicenseParser):

    def __init__(self, denied_licenses, alias):
        super(PrettyLicenseParser, self).__init__(denied_licenses, alias)
        self.licensing = license_expression.Licensing()

    def parse_license(self, expr):
        logging.debug(f"parse_license(\"{expr}\")")

        if not isinstance(expr, list):
            raise FlictError(ReturnCodes.RET_INVALID_EXPRESSSION, f"Internal error: Expression to parse must be a list: {expr}")

        if len(expr) == 0:
            raise FlictError(ReturnCodes.RET_INVALID_EXPRESSSION, f"Internal error: Expression list cannot be empty: {expr}")

        if len(expr[0]) == 0:
            raise FlictError(ReturnCodes.RET_INVALID_EXPRESSSION, "Internal error: Expression list's first item cannot be empty")

        lic_expr = " ".join(expr).replace(")", " ) ").replace("(", " ( ")
        logging.debug(f"expression:         {lic_expr}")

        parsed = self.licensing.parse(lic_expr)
        logging.debug(f"parsed expression:  {parsed}")

        simplified = parsed.simplify()
        logging.debug(f"parsed expression:  {simplified}")

        pretty = self.licensing.parse(simplified).pretty()
        logging.debug(f"pretty expression:  {pretty}")

        trimmed = pretty.replace("\n", "")
        logging.debug(f"trimmed expression: {trimmed}")

        logging.debug(f"parse_license(\"{expr}\") => {trimmed}")
        return {
            "license": self._parse_license(trimmed),
            'original': lic_expr,
            'trimmed': trimmed
        }

    def _parse_license(self, expr):
        logging.info(f"_parse_license(\"{expr}\")")

        is_operator = self.utils.is_operator(expr)

        if is_operator:

            op = self.utils.next_operator(expr)
            rest = expr[len(op):]

            # assert next token is "("
            #assert ( rest.strip()[:1] == "(" )

            # find last parenthesis and
            rest = rest[1:self.utils.index_last_parenthesis(rest)].strip()

            operands = []

        else:
            rest = expr

        while (rest != ""):
            if self.utils.is_license(rest):
                lic, rest = self.utils.get_license(rest)
                operand = {
                    'type': 'license',
                    'name': lic
                }

                if (is_operator):
                    operands.append(operand)
                else:
                    return operand
            elif self.utils.is_operator(rest):
                operation, rest = self.utils._get_op_expr(rest)
                logging.info(f"  operation: {operation}")
                parsed = self._parse_license(operation)
                operands.append(parsed)
            elif self.utils.next_token(rest) == ",":
                rest = self.utils.remove_comma(rest)
            elif self.utils.next_token(rest) == LICENSE_WITH_SYMBOL:
                lic, rest = self.utils.get_license(rest)
                operand = {
                    'type': 'license',
                    'name': lic
                }
            else:
                logging.error("*** PANIC IN DETROIT ***")
                logging.error(rest)
                # TODO: raise exception
        return {
            'type': 'operator',
            'name': op,
            'operands': operands
        }

    def licenses(self, expr):
        """
        Given a license expression, the licenses in the expression is returned as a list.

        Parameters:
            expr - license expression

        Examples:
          licenses("( FTL OR GPL-2.0-or-later ) AND (  ( Libpng)  AND  ( Zlib)  ) ")

          will return:
            'GPL-2.0-or-later', 'Zlib', 'FTL', 'Libpng'
        """
        try:
            logging.debug(f"licenses(\"{expr}\")")
            parsed = self.licensing.parse(expr.replace(" WITH ", "_WITH_"))
            keys = self.licensing.license_keys(parsed)
            key_set = set()
            for key in keys:
                key_set.add(key.replace("_WITH_", " WITH "))
            return list(key_set)
        except:
            raise FlictError(ReturnCodes.RET_INVALID_EXPRESSSION, f"Could not parse and list license expression: {expr}")

    def simplify_license(self, expr):
        try:
            aliased = self.alias.replace_aliases(expr)
            parsed = self.licensing.parse(aliased)
            simplified = str(parsed.simplify())
            return {
                "original": expr,
                "simplified": simplified
            }
        except:
            raise FlictError(ReturnCodes.RET_INVALID_EXPRESSSION, f"Could not parse or simplify license expression: {expr}")


class ParseUtils:

    def _find_expr_end(self, expr):
        logging.debug(f"_find_expr_end(\"{expr}\")")

        first_found = False
        paren_count = 0
        size = 0
        for tok in expr:
            if tok == "(":
                #logging.debug("-found (  :" + expr[size:])
                paren_count += 1
                first_found = True
            elif tok == ")":
                #logging.debug("-found )  :" + expr[size:])
                paren_count -= 1

            size += 1
            if paren_count == 0 and first_found:
                #logging.debug(" -: " + str(size))
                #logging.debug("1-: " + expr[1:size])
                # may be some space and crap
                index = 0
                #if ")" in expr[size+1:]:
                #    index = expr[size+1:].index(")")

                #logging.debug("2-: " + expr[1:size+index])
                return size + index

        # TODO: raise exception

    def next_token(self, expr):
        for i in range(len(expr)):
            if i == " " or i == "\n":
                pass
            else:
                if expr.startswith(LICENSE_EXPRESSION_OR):
                    return LICENSE_EXPRESSION_OR
                elif expr.startswith(LICENSE_EXPRESSION_AND):
                    return LICENSE_EXPRESSION_AND
                elif expr.startswith(LICENSE_SYMBOL):
                    return LICENSE_SYMBOL
                elif expr.startswith(LICENSE_WITH_SYMBOL):
                    return LICENSE_WITH_SYMBOL

                return expr[i]

    def next_operator(self, expr):
        token = self.next_token(expr)
        if token == LICENSE_EXPRESSION_OR or token == LICENSE_EXPRESSION_AND:
            return token
        return None

    def is_operator(self, expr):
        #assert (expr != None)
        return self.next_operator(expr) is not None

    def is_license(self, expr):
        return expr.startswith(LICENSE_SYMBOL) or expr.startswith(LICENSE_WITH_SYMBOL)

    def is_with(self, expr):
        return expr.startswith(LICENSE_WITH_SYMBOL)

    def remove_comma(self, expr):
        stripped = expr.strip()
        #assert( stripped[0] == "," )
        return stripped[1:].strip()

    def _get_op_expr(self, expr):
        #assert (self.is_operator(expr))
        expr = expr.strip()
        index = self._find_expr_end(expr)
        #assert ( index != None )
        operation = expr[:index]
        rest = expr[index:]
        #logging.debug("_get_op_expr => ")
        #logging.debug("    expression: \"" + expr + "\"")
        #logging.debug("    operation:  \"" + operation + "\"")
        #logging.debug("    rest:       \"" + rest + "\"")
        return (operation, rest)

    def get_license(self, expr):
        #assert( self.is_license(expr) )
        index = expr.index(")")
        if LICENSE_WITH_SYMBOL in expr:
            lic = expr[len(LICENSE_WITH_SYMBOL) + 1:index].replace("'", "")
        elif LICENSE_SYMBOL in expr:
            lic = expr[len(LICENSE_SYMBOL) + 1:index].replace("'", "")

        rest = expr[index + 1:]
        return (lic, rest)

    def index_last_parenthesis(self, expr):
        return expr.rfind(")")


