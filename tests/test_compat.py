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
        # args = ArgsMock(['MIT'])
        # ret = FlictImpl(args).display_compatibility()
        # self.assertEqual(ret, '{"compatibilities": [{"license": "MIT", "licenses": []}]}')
        pass

if __name__ == '__main__':
    unittest.main()


# Namespace(
#     license_group_file='/tmp/venv/lib/python3.9/site-packages/flict-0.1-py3.9.egg/flict/var/license-group.json',
#     matrix_file='/tmp/venv/lib/python3.9/site-packages/osadl_matrix/osadl-matrix.csv',
#     relicense_file='/tmp/venv/lib/python3.9/site-packages/flict-0.1-py3.9.egg/flict/var/relicense.json',
#     scancode_file=None,
#     translations_file='/tmp/venv/lib/python3.9/site-packages/flict-0.1-py3.9.egg/flict/var/translation.json',
#     enable_scancode=False,
#     extended_licenses=False,
#     no_relicense=False,
#     output=<_io.TextIOWrapper name='<stdout>' mode='w' encoding='utf-8'>,
#     output_format='JSON',
#     verbose=False,
#     licenses=None,
#     outbound_licenses=None,
#     version=False,
#     debug_license=False,
#     graph=None,
#     table=None,
#     license_expression=['MIT'],
#     which='display-compatibility',
#     func=<function display_compatibility at 0x7f837ac748b0>
# )
