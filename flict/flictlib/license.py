# SPDX-FileCopyrightText: 2022 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later

from flict.flictlib.alias import Alias
from flict.flictlib.license_parser import LicenseParserFactory
from flict.flictlib.return_codes import FlictError, ReturnCodes


class License():
    """Class managing license expressions, e.g.:
    X11
    MIT OR BSD-3-Clause
    GPL-2.0-or-later or (GPL-3.0-only WITH GCC-exception-3.1 AND curl
    """

    def __init__(self, denied_licenses, alias=None):
        self.alias = alias or Alias()
        self._denied_licenses = denied_licenses
        self.parser = LicenseParserFactory.get_parser()

    def get_license(self, expr):
        return self.parser.parse_license(expr)['license']

    def license_name(self, expr):
        return self.parser.license(expr)

    def operator(self, expr):
        return self.parser.operator(expr)

    def operands(self, expr):
        return self.parser.operands(expr)

    def licenses(self, expr):
        return self.parser.licenses(expr)

    def replace_aliases(self, expr):
        return self.alias.replace_aliases(expr)

    def denied_licenses(self):
        return self._denied_licenses

    def license_denied(self, license):
        if self._denied_licenses:
            return license in self._denied_licenses
        return False

    def license_allowed(self, license):
        return not self.license_denied(license)

    def simplify_license(self, expr):
        try:
            aliased = self.alias.replace_aliases(expr)
            parsed = self.parser.parse_license([aliased])
            simplified = str(parsed['simplified'])
            return {
                "original": expr,
                "simplified": simplified
            }
        except Exception as e:
            raise FlictError(ReturnCodes.RET_INVALID_EXPRESSSION, f"Could not parse or simplify license expression: {expr}. Cause: {str(e)}")

    def is_operator(self, expr):
        return self.parser.is_operator(expr)

    def is_license(self, expr):
        return self.parser.is_license(expr)

    def verified_to_license(self, parsed_expr):
        expr_type = parsed_expr['type']

        if expr_type == 'license':
            return parsed_expr['name']

        if expr_type == 'operator':
            name = parsed_expr['name']

            operands = []
            for op in parsed_expr['operands']:
                if op['compatibility'] != "Yes":
                    pass
                else:
                    parsed_op = self.parsed_to_license(op)
                    operands.append(parsed_op)
            operand_str = f" {name} "
            expr = operand_str.join(operands)
            if name == "OR" and len(operands) > 1:
                expr = f" ( {expr} ) "
            return expr
