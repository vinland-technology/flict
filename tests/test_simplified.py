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
    def __init__(self,
                 debug_licenses=False,
                 enable_scancode=False,
                 extended_licenses=False,
                 license_expression='',
                 license_group_file=flict_config.DEFAULT_GROUP_FILE,
                 licenses=None,
                 matrix_file = flict_config.DEFAULT_MATRIX_FILE,
                 no_relicense=False,
                 outbound_licenses=None,
                 output_format='JSON',
                 relicense_file=flict_config.DEFAULT_RELICENSE_FILE,
                 scancode_file=None,
                 translations_file=flict_config.DEFAULT_TRANSLATIONS_FILE,
                 verbose=False,
                 version=False
                 ):
        self.debug_licenses = debug_licenses
        self.enable_scancode = enable_scancode
        self.extended_licenses = extended_licenses
        self.license_expression = license_expression
        self.license_group_file = license_group_file 
        self.licenses = licenses
        self.matrix_file = matrix_file
        self.no_relicense = no_relicense
        self.outbound_licenses = outbound_licenses
        self.output_format = output_format
        self.relicense_file = relicense_file
        self.scancode_file = scancode_file
        self.translations_file = translations_file
        self.verbose = verbose
        self.version = version


class SimplificationTest(unittest.TestCase):

    def _test_expression(self, expression, result):
        args = ArgsMock(license_expression=expression)
        ret = FlictImpl(args).suggest_outbound_candidate()
        self.assertEqual(ret, result)

    def test_simplify(self):
        # self._test_expression(['MIT'], '{"original": "MIT", "simplified": "MIT"}')
        # self._test_expression(['MIT and MIT'], '{"original": "MIT and MIT", "simplified": "MIT"}')
        # self._test_expression(['MIT and MIT and BSD-3-Clause'], '{"original": "MIT and MIT and BSD-3-Clause", "simplified": "BSD-3-Clause AND MIT"}')
        # self._test_expression(['BSD'], '{"original": "BSD", "simplified": "BSD-3-Clause"}')
        # self._test_expression(['MIT and MIT and BSD'], '{"original": "MIT and MIT and BSD", "simplified": "BSD-3-Clause AND MIT"}')
        # self._test_expression(['MIT and MIT or BSD'], '{"original": "MIT and MIT or BSD", "simplified": "BSD-3-Clause OR MIT"}')
        # self._test_expression(['GPL-2.0-only'], '{"original": "GPL-2.0-only", "simplified": "GPL-2.0-only"}')
        # self._test_expression(['GPL-2.0-or-later'], '{"original": "GPL-2.0-or-later", "simplified": "GPL-2.0-or-later"}')
        # self._test_expression(['GPL-2.0-or-later and MIT'], '{"original": "GPL-2.0-or-later and MIT", "simplified": "GPL-2.0-or-later AND MIT"}')
        pass

if __name__ == '__main__':
    unittest.main()
