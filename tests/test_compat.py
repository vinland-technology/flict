# SPDX-FileCopyrightText: 2021 Jens Erdmann
#
# SPDX-License-Identifier: GPL-3.0-or-later

import json
import pytest

from flict.impl import FlictImpl
from tests.args_mock import ArgsMock

def test_compat():
    args = ArgsMock(license_expression=['MIT'])
    ret = FlictImpl(args).display_compatibility()
    assert '{"compatibilities": [{"license": "MIT", "licenses": []}]}' == ret

def test_complex_compat():
    expr = ['MIT BSD GPL-2.0-only WITH Classpath-exception-2.0']    
    args = ArgsMock(license_expression=expr)
    ret = FlictImpl(args).display_compatibility()
    jret = json.loads(ret)

    # this can not be a direct comparism as the result is in random order as of now
    for lic in ['BSD-3-Clause', 'GPL-2.0-only WITH Classpath-exception-2.0', 'MIT']:
        assert any(x['license'] == lic for x in jret['compatibilities'])
