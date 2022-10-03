# SPDX-FileCopyrightText: 2021 Jens Erdmann
#
# SPDX-License-Identifier: GPL-3.0-or-later

import json
import pytest

from flict.impl import FlictImpl
from tests.args_mock import ArgsMock

def _test_expression(expression, result):
    args = ArgsMock(license_expression=expression)
    ret = FlictImpl(args).suggest_outbound_candidate()
    assert result == json.loads(ret)

def test_outbound():
    _test_expression(['MIT'], ['MIT'])
    _test_expression(['MIT and MIT'], ['MIT'])
    _test_expression(['MIT and GPL-2.0-only'], ['GPL-2.0-only'])
    _test_expression(['MIT and MIT and BSD-3-Clause'], ['BSD-3-Clause', 'MIT'])
    _test_expression(['GPL-2.0-only and (MIT or BSD-3-Clause)'], ['GPL-2.0-only'])
    _test_expression(['GPL-2.0-only or (MIT and BSD-3-Clause)'], ['BSD-3-Clause', 'GPL-2.0-only', 'MIT'])
    _test_expression(['GPL-2.0-only and (Apache-2.0 or MIT)'], ['GPL-2.0-only'])
    _test_expression(['GPL-2.0-only or (Apache-2.0 and MIT)'], ['Apache-2.0', 'GPL-2.0-only', 'MIT'])
    _test_expression(['GPL-2.0-only and Apache-2.0'], [])
    _test_expression(['GPL-2.0-only and Apache-2.0 and MPL-2.0'], [])
    _test_expression(['GPL-2.0-only and MPL-2.0'], ['GPL-2.0-only'])
    _test_expression(['GPL-2.0-only and MPL-2.0'], ['GPL-2.0-only'])
    _test_expression(['GPL-2.0-only and (MPL-2.0 or Apache-2.0) and BSD-3-Clause'],
                    ['GPL-2.0-only'])
    _test_expression(['(GPL-2.0-only or MPL-2.0) and (Apache-2.0 or BSD-3-Clause)'],
                    ['GPL-2.0-only', 'MPL-2.0'])

