#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2022 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest

from flict.flictlib.return_codes import FlictError
from flict.flictlib.return_codes import ReturnCodes

from flict.flictlib.license import LicenseParserFactory
from flict.flictlib.license import PrettyLicenseParser


denied = [ "curl" ]

class TestLicenseParser(unittest.TestCase):

    def _parse_and_get_simple_license(self, parser, expr):
        return parser.parse_license([expr])['license']['name']
    
    def test_license_parser_constructor(self):
        parser = LicenseParserFactory.get_parser(denied)
        self.assertTrue(isinstance(parser, PrettyLicenseParser))
        self.assertEqual(parser.denied_licenses(), denied)

    def test_license_parser_parse_license(self):
        parser = LicenseParserFactory.get_parser(denied)
        
        self.assertEqual(self._parse_and_get_simple_license(parser, "MIT"), "MIT")
        self.assertEqual(self._parse_and_get_simple_license(parser, "X11"), "X11")

        self.assertEqual(self._parse_and_get_simple_license(parser, "GPL-2.0-only WITH Classpath-exception-2.0"), "GPL-2.0-only WITH Classpath-exception-2.0")


        mit_and_x11 = parser.parse_license(["MIT AND X11"])
        self.assertEqual(mit_and_x11['license']['type'], "operator")
        self.assertEqual(mit_and_x11['license']['name'], "AND")

        operands = mit_and_x11['license']['operands']

        self.assertTrue(operands[0]['name'] == "MIT" and operands[1]['name'] == "X11" or
                            operands[1]['name'] == "MIT" and operands[0]['name'] == "X11")

        with self.assertRaises(FlictError):
            parser.parse_license("This is not a list")

        with self.assertRaises(FlictError):
            parser.parse_license([])

        with self.assertRaises(FlictError):
            parser.parse_license([""])

    def test_licenses(self):
        parser = LicenseParserFactory.get_parser(denied)
        license_list = parser.licenses("MIT and BSD-3-Clause OR X11 AND MIT OR BSD-3-Clause")
        print("license_list: " + str(license_list))
            


if __name__ == '__main__':
    unittest.main()
        
        
