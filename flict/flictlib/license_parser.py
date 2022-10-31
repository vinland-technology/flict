# SPDX-FileCopyrightText: 2022 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later


import logging
import license_expression

from flict.flictlib.return_codes import FlictError, ReturnCodes

from enum import Enum


class LicenseExpression(Enum):
    LICENSE_EXPRESSION_OR = "OR"
    LICENSE_EXPRESSION_AND = "AND"


class PrettyLicenseSymbol(Enum):
    LICENSE_SYMBOL = "LicenseSymbol"
    LICENSE_WITH_SYMBOL = "LicenseWithExceptionSymbol"


class LicenseParserFactory:

    @staticmethod
    def get_parser():
        # Not much of a choice really :)
        return PrettyLicenseParser()


class LicenseParser:

    def __init__(self):
        self.utils = ParseUtils()

    def parse_license(self, expr):
        return

    def licenses(self, expr):
        return

    def is_operator(self, expr):
        return expr['type'] == "operator"

    def is_license(self, expr):
        return expr['type'] == "license"

    def operator(self, expr):
        return expr['name']

    def is_or(self, expr):
        return self.expr_operator(expr) == LicenseExpression.LICENSE_EXPRESSION_OR.value

    def is_and(self, expr):
        return self.operator(expr) == LicenseExpression.LICENSE_EXPRESSION_AND.value

    def license(self, expr):  # noqa: A003
        return expr['name']

    def operands(self, expr):
        return expr['operands']


class PrettyLicenseParser(LicenseParser):

    def __init__(self):
        super(PrettyLicenseParser, self).__init__()
        self.licensing = license_expression.Licensing()

    def parse_license(self, expr):
        logging.debug(f"parse_license(\"{expr}\")")

        if not isinstance(expr, list):
            raise FlictError(ReturnCodes.RET_INVALID_EXPRESSSION,
                             f"Internal error: Expression to parse must be a list: {expr}")

        if len(expr) == 0:
            raise FlictError(ReturnCodes.RET_INVALID_EXPRESSSION, f"Internal error: Expression list cannot be empty: {expr}")

        if len(expr[0]) == 0:
            raise FlictError(ReturnCodes.RET_INVALID_EXPRESSSION,
                             "Internal error: Expression list's first item cannot be empty")

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
            'license': self._parse_license(trimmed),
            'original': lic_expr,
            'simplified': simplified,
            'pretty': pretty,
            'trimmed': trimmed,
        }

    def _parse_license(self, expr):
        logging.info(f"_parse_license(\"{expr}\")")

        is_operator = self.utils.is_operator(expr)

        if is_operator:

            op = self.utils.next_operator(expr)
            rest = expr[len(op):]

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
                    'name': lic,
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
            elif self.utils.next_token(rest) == PrettyLicenseSymbol.LICENSE_WITH_SYMBOL.value:
                lic, rest = self.utils.get_license(rest)
            else:
                logging.error("*** PANIC IN DETROIT ***")
                logging.error(rest)
                raise FlictError(ReturnCodes.RET_INVALID_EXPRESSSION,
                                 f"Internal error: Remaining expression not valid: {rest}")
        return {
            'type': 'operator',
            'name': op,
            'operands': operands,
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
        except BaseException:
            raise FlictError(ReturnCodes.RET_INVALID_EXPRESSSION, f"Could not parse and list license expression: {expr}")


class ParseUtils:

    def _find_expr_end(self, expr):
        logging.debug(f"_find_expr_end(\"{expr}\")")

        first_found = False
        paren_count = 0
        size = 0
        for tok in expr:
            if tok == "(":
                paren_count += 1
                first_found = True
            elif tok == ")":
                paren_count -= 1

            size += 1
            if paren_count == 0 and first_found:
                index = 0
                return size + index

        raise FlictError(ReturnCodes.RET_INVALID_EXPRESSSION, f"Internal error: Could not find end of expression: {expr}")

    def next_token(self, expr):
        for i in range(len(expr)):
            if i == " " or i == "\n":
                pass
            else:
                if expr.startswith(LicenseExpression.LICENSE_EXPRESSION_OR.value):
                    return LicenseExpression.LICENSE_EXPRESSION_OR.value
                elif expr.startswith(LicenseExpression.LICENSE_EXPRESSION_AND.value):
                    return LicenseExpression.LICENSE_EXPRESSION_AND.value
                elif expr.startswith(PrettyLicenseSymbol.LICENSE_SYMBOL.value):
                    return PrettyLicenseSymbol.LICENSE_SYMBOL.value
                elif expr.startswith(PrettyLicenseSymbol.LICENSE_WITH_SYMBOL.value):
                    return PrettyLicenseSymbol.LICENSE_WITH_SYMBOL.value

                return expr[i]

    def next_operator(self, expr):
        token = self.next_token(expr)
        if token == LicenseExpression.LICENSE_EXPRESSION_OR.value or token == LicenseExpression.LICENSE_EXPRESSION_AND.value:
            return token
        return None

    def is_operator(self, expr):
        return self.next_operator(expr) is not None

    def is_license(self, expr):
        return expr.startswith(PrettyLicenseSymbol.LICENSE_SYMBOL.value) or expr.startswith(PrettyLicenseSymbol.LICENSE_WITH_SYMBOL.value)

    def is_with(self, expr):
        return expr.startswith(PrettyLicenseSymbol.LICENSE_WITH_SYMBOL.value)

    def remove_comma(self, expr):
        stripped = expr.strip()
        return stripped[1:].strip()

    def _get_op_expr(self, expr):
        expr = expr.strip()
        index = self._find_expr_end(expr)
        operation = expr[:index]
        rest = expr[index:]
        return (operation, rest)

    def get_license(self, expr):
        index = expr.index(")")
        if PrettyLicenseSymbol.LICENSE_WITH_SYMBOL.value in expr:
            lic = expr[len(PrettyLicenseSymbol.LICENSE_WITH_SYMBOL.value) + 1:index].replace("'", "")
        elif PrettyLicenseSymbol.LICENSE_SYMBOL.value in expr:
            lic = expr[len(PrettyLicenseSymbol.LICENSE_SYMBOL.value) + 1:index].replace("'", "")

        rest = expr[index + 1:]
        return (lic, rest)

    def index_last_parenthesis(self, expr):
        return expr.rfind(")")
