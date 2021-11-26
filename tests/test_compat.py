#!/bin/python3

# SPDX-FileCopyrightText: 2021 Jens Erdmann
#
# SPDX-License-Identifier: GPL-3.0-or-later

import os
import sys
import unittest

TEST_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Add to PYTHON_PATH
sys.path.insert(0, TEST_DIR)

from flict.impl import FlictImpl
from tests.args_mock import ArgsMock


class CompatibilityTest(unittest.TestCase):

    def test_compat(self):
        args = ArgsMock(license_expression=['MIT'])
        ret = FlictImpl(args).display_compatibility()
        self.assertEqual(ret, '{"compatibilities": [{"license": "MIT", "licenses": []}]}')

if __name__ == '__main__':
    unittest.main()
