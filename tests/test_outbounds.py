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

class OutboundTest(unittest.TestCase):

    def test_outbound(self):
        # args = ArgsMock(['MIT'])
        # ret = FlictImpl(args).suggest_outbound_candidate()
        # self.assertEqual(ret, ['MIT'])
        pass
        
        
if __name__ == '__main__':
    unittest.main()


#     local CMD="$1"
#     local EXP="$2"
#     local EXP_RET="$3"
#     local MSG="$4"

# compare_exec     "flict outbound-candidate 'MIT'"          '["MIT"]' 0 "MIT only"

# compare_exec     "flict outbound-candidate  'MIT and MIT'" '["MIT"]' 0 "Simplify MIT and MIT "

# compare_exec     "flict outbound-candidate  'MIT and MIT and BSD-3-Clause'" \
#                  '["BSD-3-Clause", "MIT"]' 0 "MIT and MIT and BSD-3-Clause"

# compare_exec     "flict outbound-candidate  'GPL-2.0-only and (MIT or BSD-3-Clause)'" \
#                  '["GPL-2.0-only"]' 0 "GPL-2-only and (MIT or BSD-3-Clause)"

# compare_exec     "flict outbound-candidate  'GPL-2.0-only or (MIT and BSD-3-Clause)'" \
#                  '["BSD-3-Clause", "GPL-2.0-only", "MIT"]' 0 "GPL-2-only or (MIT and BSD-3-Clause)"

# compare_exec     "flict outbound-candidate  'GPL-2.0-only and (Apache-2.0 or MIT)'" \
#                  '["GPL-2.0-only"]' 0 'GPL-2.0-only and (Apache-2.0 or MIT)'

# compare_exec     "flict outbound-candidate  'GPL-2.0-only or (Apache-2.0 and MIT)'" \
#                  '["Apache-2.0", "GPL-2.0-only", "MIT"]' 0 'GPL-2.0-only or (Apache-2.0 and MIT)'

# compare_exec     "flict outbound-candidate  'GPL-2.0-only and Apache-2.0'" \
#                  '[]' 0 'GPL-2.0-only and Apache-2.0'

# # no relicense
# compare_exec     "flict -nr outbound-candidate  'GPL-2.0-only and MPL-2.0'" \
#                  '["GPL-2.0-only"]' 0 'GPL-2.0-only and MPL-2.0'

# # no relicense
# compare_exec     "flict -rf \"\" outbound-candidate  'GPL-2.0-only and MPL-2.0'" \
#                  '["GPL-2.0-only"]' 0 'GPL-2.0-only and MPL-2.0'

# compare_exec     "flict outbound-candidate  'GPL-2.0-only and Apache-2.0 and MPL-2.0'" \
#                  '[]' 0 'GPL-2.0-only and Apache-2.0 and MPL-2.0'

# compare_exec     "flict outbound-candidate  'GPL-2.0-only and MPL-2.0'" \
#                  '["GPL-2.0-only", "GPL-2.0-or-later"]' 0 'GPL-2.0-only and MPL-2.0'

# compare_exec     "flict outbound-candidate  'GPL-2.0-only and MPL-2.0'" \
#                  '["GPL-2.0-only", "GPL-2.0-or-later"]' 0 'GPL-2.0-only and MPL-2.0'

# compare_exec     "flict outbound-candidate  'GPL-2.0-only and (MPL-2.0 or Apache-2.0) and BSD-3-Clause'" \
#                  '["GPL-2.0-only", "GPL-2.0-or-later"]' 0 'GPL-2.0-only and (MPL-2.0 or Apache-2.0) and BSD-3-Clause'

# compare_exec     "flict outbound-candidate  '(GPL-2.0-only or MPL-2.0) and (Apache-2.0 or BSD-3-Clause)'" \
#                  '["AGPL-3.0-or-later", "GPL-2.0-only", "GPL-2.0-or-later", "GPL-3.0-or-later", "LGPL-2.1-or-later"]' 0 ''