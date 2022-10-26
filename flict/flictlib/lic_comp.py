# SPDX-FileCopyrightText: 2022 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later

import logging

from flict.flictlib.compatibility import CompatibilityFactory
from flict.flictlib.compatibility import CompatibilityStatus
from flict.flictlib.compatibility import LICENSE_COMPATIBILITY_AND
from flict.flictlib.compatibility import LICENSE_COMPATIBILITY_OR
from flict.flictlib.compatibility import CompatibilityLicenseChooser
from flict.flictlib.compatibility import CustomLicenseChooser
from flict.flictlib.alias import Alias
from flict.flictlib.license import License
from flict.flictlib.return_codes import FlictError, ReturnCodes

COMPATIBILITY_TAG = "compatibility"


class LicenseCompatibilty:

    def __init__(self, license_db=None, licenses_preferences=None, denied_licenses=None, alias_file=None):
        self.alias = Alias(alias_file)

        self.license = License(denied_licenses, self.alias)

        self.compatibility = CompatibilityFactory.get_compatibility(self.alias, license_db)

        if not licenses_preferences or licenses_preferences == []:
            self.license_chooser = CompatibilityLicenseChooser(self.compatibility.supported_licenses())
        else:
            self.license_chooser = CustomLicenseChooser(licenses_preferences)

    def inbound_outbound_compatibility(self, outbound, inbound):
        return self.compatibility.check_compat(self.alias.replace_aliases(outbound), self.alias.replace_aliases(inbound))

    def inbounds_outbound_compatibility(self, outbound, expr):
        """
        Checks how the outbound license is compatible to the inbound licenses(s).

        Parameters:
            outbound - outbound license (str)
            expr - inbound license expression (list)

        Examples:
        ----------------------------------------------------------------------
        inbounds_outbound_compatibility(X11, ['MIT', 'OR', 'LGPL-2.1-only'])
        inbounds_outbound_compatibility(X11, ['MIT OR LGPL-2.1-only']

        both return the following
            {
                "type": "operator",
                "name": "OR",
                "operands": [
                    {
                        "type": "license",
                        "name": "LGPL-2.1-only",
                        "license_aliased": "LGPL-2.1-only",
                        "check": "inbounds_outbound",
                        "outbound": {
                            "type": "license",
                            "name": "X11"
                        },
                        "outbound_aliased": "X11",
                        "allowed": true,
                        "compatibility": "No"  <--- compatiblity status for outbound X11 and inbound LGPL-2.1-only
                    },
                    {
                        "type": "license",
                        "name": "MIT",
                        "license_aliased": "MIT",
                        "check": "inbounds_outbound",
                        "outbound": {
                            "type": "license",
                            "name": "X11"
                        },
                        "outbound_aliased": "X11",
                        "allowed": true,
                        "compatibility": "Yes"  <--- compatiblity status for outbound X11 and inbound MIT
                    }
                ],
                "outbound": {
                    "type": "license",
                    "name": "X11"
                },
                "compatibility": "Yes",   <--- compatiblity status for outbound X11 and inbound 'MIT OR LGPL-2.1-only'.
                "allowed": true,
                "check": "inbounds_outbound"
            }

        """
        parsed_outbound = self.license.get_license([outbound])

        logging.debug(f"inbounds_outbound_check({outbound}, {expr})")
        parsed = self.license.get_license(expr)
        logging.debug(f"inbounds_outbound_check: parsed:{parsed}")

        return self._inbounds_outbound_check(parsed_outbound, parsed)

    def _inbounds_outbound_check_operator(self, outbound, expr):
        compat_summary = None
        allowed_summary = None
        op = self.license.operator(expr)
        operands = self.license.operands(expr)
        for operand in operands:
            logging.debug(f"Check operand: {operand}")

            # get compatibility_tag between the operand and the outbound
            # and calculate and store the summarized compatibility
            compat = self._inbounds_outbound_check(outbound, operand)
            compat_summary = self._update_compat(op, compat_summary, compat[COMPATIBILITY_TAG] == CompatibilityStatus.LICENSE_COMPATIBILITY_COMPATIBLE.value)

            # are licenses allowed or denied for this expression
            allowed = compat['allowed']
            allowed_summary = self._update_allowed(op, allowed_summary, allowed)
            operand['allowed'] = allowed
            #                operand['compatibility_info'] = compat
            operand[COMPATIBILITY_TAG] = compat[COMPATIBILITY_TAG]

        # store outbound to make for easier reading of result
        expr['outbound'] = outbound
        expr[COMPATIBILITY_TAG] = compat_summary

        expr["allowed"] = allowed_summary
        expr['check'] = 'inbounds_outbound'

        return expr

    def _inbounds_outbound_check_license(self, outbound, expr):
        license_expr = self.license.license_name(expr)

        outbound_aliased = self.license.replace_aliases(self.license.license_name(outbound))
        license_aliased = self.license.replace_aliases(license_expr)

        compat = self.compatibility.check_compat(outbound_aliased, license_aliased)

        expr['license_aliased'] = license_aliased
        expr['check'] = 'inbounds_outbound'
        expr['outbound'] = outbound
        expr['outbound_aliased'] = outbound_aliased
        expr['allowed'] = self.license.license_allowed(license_expr)

        expr[COMPATIBILITY_TAG] = compat[COMPATIBILITY_TAG]
        return expr

    def _inbounds_outbound_check(self, outbound, expr):
        logging.debug(f"_inbounds_outbound_check({outbound}, {expr})")
        if self.license.is_license(expr):
            return self._inbounds_outbound_check_license(outbound, expr)
        elif self.license.is_operator(expr):
            return self._inbounds_outbound_check_operator(outbound, expr)
        else:
            raise FlictError(ReturnCodes.RET_INTERNAL_ERROR,
                             f"Could not parse one of the expression: {outbound}, {expr}")

    def _update_compat(self, op, current, new):

        if current is None:
            updated = new
        elif op == LICENSE_COMPATIBILITY_AND:
            updated = current == CompatibilityStatus.LICENSE_COMPATIBILITY_COMPATIBLE.value and new
        elif op == LICENSE_COMPATIBILITY_OR:
            updated = current == CompatibilityStatus.LICENSE_COMPATIBILITY_COMPATIBLE.value or new

        if updated:
            return CompatibilityStatus.LICENSE_COMPATIBILITY_COMPATIBLE.value
        return CompatibilityStatus.LICENSE_COMPATIBILITY_INCOMPATIBLE.value

    def _update_allowed(self, op, current, new):

        if current is None:
            updated = new
        elif op == LICENSE_COMPATIBILITY_AND:
            updated = current and new
        elif op == LICENSE_COMPATIBILITY_OR:
            updated = current or new

        return updated

    def licenses(self, expr):
        return self.license.licenses(expr)

    def supported_licenses(self):
        return self.compatibility.supported_licenses()

    def replace_aliases(self, expr):
        return self.alias.replace_aliases(expr)

    def check_compatibilities(self, licenses, check_all=False):
        return self.compatibility.check_compatibilities(licenses, check_all)

    def extend_license_db(self, file_name):
        return self.compatibility.extend_license_db(file_name)

    def simplify_license(self, expr):
        return self.license.simplify_license(expr)

    def get_license(self, expr):
        return self.license.get_license(expr)

    def choose_license(self, licenses):
        return self.license_chooser.choose(licenses)


# TODO: add to utils or similar
# easy to use function
def inbound_outbound_compatibility(outbound, inbounds, license_db=None):
    return LicenseCompatibilty(license_db).inbounds_outbound_compatibility(outbound, [inbounds])['compatibility']


if __name__ == '__main__':
    print(inbound_outbound_compatibility("MIT", "X11"))
