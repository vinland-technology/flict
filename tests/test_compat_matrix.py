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
sys.path.insert(0, TEST_DIR)

from flict.flictlib.compat_matrix import CompatibilityMatrix, CompatMatrixStatus
from flict.var import VAR_DIR

MATRIX_FILE=os.path.join(VAR_DIR, "osadl-matrix.csv")

class TestOneWay(unittest.TestCase):
    def test_oneway(self):
        _compat_matrix = CompatibilityMatrix(MATRIX_FILE)
        # Check MIT and BSD-3-Clause noth ways - one at a time
        self.assertEqual(_compat_matrix.a_compatible_with_b("MIT", "BSD-3-Clause"), CompatMatrixStatus.TRUE)
        self.assertEqual(_compat_matrix.a_compatible_with_b("BSD-3-Clause", "MIT"), CompatMatrixStatus.TRUE)
        # BSD is not a license, should give a None
        print("Below test will output (stderr) a message that compatibility could not be checked", file=sys.stderr)
        self.assertRaises(Exception, _compat_matrix.a_compatible_with_b, "MIT", "BSD")
        # GPL-2.0 can use BSD-3-Clause - but not the other way around
        self.assertEqual(_compat_matrix.a_compatible_with_b("GPL-2.0-only", "BSD-3-Clause"), CompatMatrixStatus.TRUE)
        self.assertEqual(_compat_matrix.a_compatible_with_b("BSD-3-Clause", "GPL-2.0-only"), CompatMatrixStatus.FALSE)
        
if __name__ == '__main__':
    unittest.main()
