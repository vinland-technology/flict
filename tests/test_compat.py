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

from flict.flictlib import flict_config
from flict.impl import FlictImpl


class ArgsMock:
    def __init__(self, license_expression):
        self.output_format = 'JSON'
        self.license_group_file = flict_config.DEFAULT_GROUP_FILE 
        self.translations_file = flict_config.DEFAULT_TRANSLATIONS_FILE
        self.relicense_file = flict_config.DEFAULT_RELICENSE_FILE
        self.matrix_file = flict_config.DEFAULT_MATRIX_FILE
        self.scancode_file = None
        self.extended_licenses = False
        self.license_expression = license_expression


class CompatibilityTest(unittest.TestCase):

    def test_compat(self):
        args = ArgsMock(['MIT'])
        ret = FlictImpl(args).display_compatibility()
        self.assertEqual(ret, '{"compatibilities": [{"license": "MIT", "licenses": []}]}')

if __name__ == '__main__':
    unittest.main()
