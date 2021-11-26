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
