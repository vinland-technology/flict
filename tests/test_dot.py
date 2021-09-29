#!/bin/python3

# SPDX-FileCopyrightText: 2021 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later

import os
import re
import sys
import unittest

TEST_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Add to PYTHON_PATH
sys.path.insert(0, TEST_DIR)

from flict.var import VAR_DIR
from flict.flictlib.compatibility import Compatibility
from flict.flictlib.format.factory import FormatFactory

MATRIX_FILE=os.path.join(VAR_DIR, "osadl-matrix.csv")

TRANSLATION_FILE   = os.path.join(VAR_DIR, "translation.json")
RELICENSE_FILE     = os.path.join(VAR_DIR, "relicense.json")
LICENSE_GROUP_FILE = os.path.join(VAR_DIR, "license-group.json")

class TestDotOutput(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        print('BasicTest.__init__')
        super(TestDotOutput, self).__init__(*args, **kwargs)
        self.compatibility = Compatibility(MATRIX_FILE, None, LICENSE_GROUP_FILE)
        self.formatter = FormatFactory.formatter("dot")

    def license_to_dot(self, licenses):
        """This method returns the dot formatted versions of the list of licenses"""
        compats = self.compatibility.check_compatibilities(licenses, False)
        formatted = self.formatter.format_compats(compats)
        return formatted.replace(" ", "")

    def find_compat(self, formatted_list, left, right, after):
        """This method checks if a line with deps between two licenses are
        present (postpended by after) regardless if which license comes
        first"""
        return left + '->' + right + after in formatted_list or \
            right + '->' + left + after in formatted_list

    def test_bsd_mit(self):
        formatted = self.license_to_dot([ "BSD-3-Clause", "MIT" ])
        formatted_list = formatted.split("\n")

        # line count
        self.assertEqual(len(formatted_list), 6)

        # only one line with "->"
        self.assertEqual(len(re.findall("->", formatted)), 1)

        
        self.assertTrue(self.find_compat(formatted_list, '"BSD-3-Clause"', '"MIT"', '[dir=both][color="darkgreen"]'))

        # only one line with ....
        self.assertEqual(len(re.findall("digraphdepends", formatted)), 1)
        self.assertEqual(len(re.findall('node\[shape=plaintext\]', formatted)), 1)
        self.assertEqual(len(re.findall('}', formatted)), 1)
        
    def test_bsd_mit_apache(self):
        formatted = self.license_to_dot([ "BSD-3-Clause", "MIT", "Apache-2.0" ])
        formatted_list = formatted.split("\n")
        #print(formatted)
        
        # line count
        self.assertEqual(len(formatted_list), 8)

        # only one line with "->"
        self.assertEqual(len(re.findall("->", formatted)), 3)

        # MIT <--> BSD
        self.assertTrue(self.find_compat(formatted_list, '"BSD-3-Clause"', '"MIT"',        '[dir=both][color="darkgreen"]'))
        self.assertTrue(self.find_compat(formatted_list, '"BSD-3-Clause"', '"Apache-2.0"', '[dir=both][color="darkgreen"]'))
        self.assertTrue(self.find_compat(formatted_list, '"MIT"',          '"Apache-2.0"', '[dir=both][color="darkgreen"]'))

        # only one line with ....
        self.assertEqual(len(re.findall("digraphdepends", formatted)), 1)
        self.assertEqual(len(re.findall('node\[shape=plaintext\]', formatted)), 1)
        self.assertEqual(len(re.findall('}', formatted)), 1)

    def test_bsd_gpl2_apache(self):
        formatted = self.license_to_dot([ "BSD-3-Clause", "GPL-2.0-or-later", "Apache-2.0" ])
        formatted_list = formatted.split("\n")
        print(formatted)
        
        # line count
        self.assertEqual(len(formatted_list), 9)

        # only one line with "->"
        self.assertEqual(len(re.findall("->", formatted)), 2)

        # MIT <--> BSD
        self.assertTrue(self.find_compat(formatted_list, '"GPL-2.0-or-later"', '"BSD-3-Clause"', '[color="black"]'))
        self.assertTrue(self.find_compat(formatted_list, '"BSD-3-Clause"', '"Apache-2.0"', '[dir=both][color="darkgreen"]'))
        self.assertTrue('"GPL-2.0-or-later"' in formatted_list)
        self.assertTrue('"Apache-2.0"' in formatted_list)

        # only one line with ....
        self.assertEqual(len(re.findall("digraphdepends", formatted)), 1)
        self.assertEqual(len(re.findall('node\[shape=plaintext\]', formatted)), 1)
        self.assertEqual(len(re.findall('}', formatted)), 1)

if __name__ == '__main__':
    unittest.main()
