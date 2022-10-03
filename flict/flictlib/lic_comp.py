#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2022 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later

import logging

from flict.flictlib.license import LicenseParserFactory
from flict.flictlib.compatibility import CompatibilityFactory
from flict.flictlib.compatibility import CompatibilityStatus
from flict.flictlib.compatibility import LICENSE_COMPATIBILITY_AND
from flict.flictlib.compatibility import LICENSE_COMPATIBILITY_OR
from flict.flictlib.compatibility import CompatibilityLicenseChoser
from flict.flictlib.compatibility import CustomLicenseChoser
import flict.flictlib.alias

COMPATIBILITY_TAG = "compatibility"


class LicenseCompatibilty:

    def __init__(self, license_db=None, licenses_preferences=None, denied_licenses=None):
        self.license_parser = LicenseParserFactory.get_parser(denied_licenses)

        self.compatibility = CompatibilityFactory.get_compatibility(license_db)

        if licenses_preferences is None or licenses_preferences == []:
            self.license_choser = CompatibilityLicenseChoser(self.compatibility.supported_licenses())
        else:
            self.license_choser = CustomLicenseChoser(licenses_preferences)

    def inbound_outbound_compatibility(self, outbound, inbound):
        return self.compatibility.check_compat(flict.flictlib.alias.replace_aliases(outbound), flict.flictlib.alias.replace_aliases(inbound))

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
        parsed_outbound = self.license_parser.parse_license([outbound])['license']
        #assert(self.license_parser.is_license(parsed_outbound))

        logging.debug(f"inbounds_outbound_check({outbound}, {expr})")
        parsed = self.license_parser.parse_license(expr)['license']
        logging.debug(f"inbounds_outbound_check: parsed:{self.license_parser.parse_license(expr)}")
        logging.debug(f"inbounds_outbound_check: parsed:{parsed}")

        compats = self._inbounds_outbound_check(parsed_outbound, parsed)

        return compats

    def _inbounds_outbound_check(self, outbound, expr):
        logging.debug(f"_inbounds_outbound_check({outbound}, {expr})")
        if self.license_parser.is_license(expr):
            license = self.license_parser.license(expr)

            outbound_aliased = flict.flictlib.alias.replace_aliases(self.license_parser.license(outbound))
            license_aliased = flict.flictlib.alias.replace_aliases(license)

            compat = self.compatibility.check_compat(outbound_aliased, license_aliased)

            expr['license_aliased'] = license_aliased
            expr['check'] = 'inbounds_outbound'
            expr['outbound'] = outbound
            expr['outbound_aliased'] = outbound_aliased
            expr['allowed'] = self.license_parser.license_allowed(license)

            expr[COMPATIBILITY_TAG] = compat[COMPATIBILITY_TAG]
            return expr

        elif self.license_parser.is_operator(expr):

            compat_summary = None
            allowed_summary = None
            op = self.license_parser.operator(expr)
            operands = self.license_parser.operands(expr)
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
                operand['allowed'] = allowed
#                operand['compatibility_info'] = compat
                operand[COMPATIBILITY_TAG] = compat[COMPATIBILITY_TAG]

            # store outbound to make for easier reading of result
            expr['outbound'] = outbound
            #expr['compatibility_info'] = compat
            expr[COMPATIBILITY_TAG] = compat_summary

            expr['outbound'] = outbound
            expr["allowed"] = allowed_summary
            expr['check'] = 'inbounds_outbound'

            return expr
        else:
            # TODO: raise exception
            logging.debug("whats???? ")
            pass

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
        # TODO: raise exception

    def _update_allowed(self, op, current, new):

        if current is None:
            updated = new
        elif op == LICENSE_COMPATIBILITY_AND:
            updated = current and new
        elif op == LICENSE_COMPATIBILITY_OR:
            updated = current or new

        return updated

    def licenses(self, expr):
        return self.license_parser.licenses(expr)

    def supported_licenses(self):
        return self.compatibility.supported_licenses()

    def replace_aliases(self, expr):
        return flict.flictlib.alias.replace_aliases(expr)

    def check_compatibilities(self, licenses, check_all=False):
        return self.compatibility.check_compatibilities(licenses, check_all)

    def extend_license_db(self, file_name):
        return self.compatibility.extend_license_db(file_name)

    def simplify_license(self, expr):
        return self.license_parser.simplify_license(expr)

    def parse_license(self, expr):
        return self.license_parser.parse_license(expr)

    def chose_license(self, licenses):
        return self.license_choser.chose(licenses)


# TODO: add to utils or similar
# easy to use function
def inbound_outbound_compatibility(outbound, inbounds, license_db=None):
    return LicenseCompatibilty(license_db).inbounds_outbound_compatibility(outbound, [inbounds])['compatibility']


if __name__ == '__main__':
    print(inbound_outbound_compatibility("MIT", "X11"))
