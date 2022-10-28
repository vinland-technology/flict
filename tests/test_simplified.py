# SPDX-FileCopyrightText: 2021 Jens Erdmann
#
# SPDX-License-Identifier: GPL-3.0-or-later

import json
import pytest

from flict.impl import FlictImpl
from tests.args_mock import ArgsMock

def _test_expression(expression, result):
    args = ArgsMock(license_expression=expression, output_format="JSON")
    ret = FlictImpl(args).simplify()
    assert json.loads(result) == json.loads(ret)

def test_simplify():
    _test_expression(['MIT'], '{"original": "MIT", "simplified": "MIT"}')
    _test_expression(['MIT and MIT'], '{"original": "MIT and MIT", "simplified": "MIT"}')
    _test_expression(['MIT and MIT and BSD-3-Clause'], '{"original": "MIT and MIT and BSD-3-Clause", "simplified": "BSD-3-Clause AND MIT"}')
    _test_expression(['BSD'], '{"original": "BSD", "simplified": "BSD-3-Clause"}')
    _test_expression(['MIT and MIT and BSD'], '{"original": "MIT and MIT and BSD", "simplified": "BSD-3-Clause AND MIT"}')
    _test_expression(['MIT and MIT or BSD'], '{"original": "MIT and MIT or BSD", "simplified": "BSD-3-Clause OR MIT"}')
    _test_expression(['GPL-2.0-only'], '{"original": "GPL-2.0-only", "simplified": "GPL-2.0-only"}')
    _test_expression(['GPL-2.0-or-later'], '{"original": "GPL-2.0-or-later", "simplified": "GPL-2.0-or-later"}')
    _test_expression(['GPL-2.0-or-later and MIT'], '{"original": "GPL-2.0-or-later and MIT", "simplified": "GPL-2.0-or-later AND MIT"}')
    _test_expression(['MIT and GPL-2.0-only WITH Classpath-exception-2.0 and MIT'], '{"original": "MIT and GPL-2.0-only WITH Classpath-exception-2.0 and MIT", "simplified": "GPL-2.0-only WITH Classpath-exception-2.0 AND MIT"}')
