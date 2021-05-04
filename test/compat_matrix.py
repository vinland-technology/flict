#!/bin/python3

# SPDX-FileCopyrightText: 2021 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later

import os
import sys
import unittest

from argparse import RawTextHelpFormatter
import argparse

TEST_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Add to PYTHON_PATH
sys.path.append(TEST_DIR)

from flictlib.compat_matrix import CompatibilityMatrix

compat_matrix = None

MATRIX_FILE="var/osadl-matrix.csv"

def setup():
    global compat_matrix
    global MATRIX_FILE
    if compat_matrix == None:
        compat_matrix = CompatibilityMatrix(MATRIX_FILE)

class TestOneWay(unittest.TestCase):
    def test_oneway(self):
        setup()
        global compat_matrix
        # Check MIT and BSD-3-Clause noth ways - one at a time
        self.assertTrue(compat_matrix.a_compatible_with_b("MIT", "BSD-3-Clause")==True)
        self.assertTrue(compat_matrix.a_compatible_with_b("BSD-3-Clause", "MIT")==True)
        # BSD is not a license, should give a None
        print("Below test will output (stderr) a message that compatibility could not be checked", file=sys.stderr)
        self.assertTrue(compat_matrix.a_compatible_with_b("MIT", "BSD")==None)
        # GPL-2.0 can use BSD-3-Clause - but not the other way around
        self.assertTrue(compat_matrix.a_compatible_with_b("GPL-2.0-only", "BSD-3-Clause")==True)
        self.assertTrue(compat_matrix.a_compatible_with_b("BSD-3-Clause", "GPL-2.0-only")==False)
        
if __name__ == '__main__':
    unittest.main()
