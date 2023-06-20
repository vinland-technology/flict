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

def test_outbound_1():
    _test_expression(['MIT'], ['MIT'])

def test_outbound_2():
    _test_expression(['MIT and MIT'], ['MIT'])

def test_outbound_3():
    _test_expression(['MIT and GPL-2.0-only'], ['GPL-2.0-only'])

def test_outbound_4():
    _test_expression(['MIT and MIT and BSD-3-Clause'], ['BSD-3-Clause', 'MIT'])

def test_outbound_5():
    _test_expression(['GPL-2.0-only and (MIT or BSD-3-Clause)'], ['GPL-2.0-only'])

def test_outbound_6():
    _test_expression(['GPL-2.0-only or (MIT and BSD-3-Clause)'], ['BSD-3-Clause', 'GPL-2.0-only', 'MIT'])

def test_outbound_7():
    _test_expression(['GPL-2.0-only and (Apache-2.0 or MIT)'], ['GPL-2.0-only'])

def test_outbound_8():
    _test_expression(['GPL-2.0-only or (Apache-2.0 and MIT)'], ['Apache-2.0', 'GPL-2.0-only', 'MIT'])

def test_outbound_9():
    _test_expression(['GPL-2.0-only and Apache-2.0'], [])

def test_outbound_10():
    _test_expression(['GPL-2.0-only and Apache-2.0 and MPL-2.0'], [])

def test_outbound_11():
    _test_expression(['GPL-2.0-only and MPL-2.0'], ['GPL-2.0-only'])

def test_outbound_12():
    _test_expression(['GPL-2.0-only and MPL-2.0'], ['GPL-2.0-only'])

def test_outbound_13():
    _test_expression(['GPL-2.0-only and (MPL-2.0 or Apache-2.0) and BSD-3-Clause'],
                    ['GPL-2.0-only'])

def test_outbound_14():
    _test_expression(['(GPL-2.0-only or MPL-2.0) and (Apache-2.0 or BSD-3-Clause)'],
                    ['GPL-2.0-only', 'MPL-2.0'])

def test_outbound_15():
    _test_expression(['(GPL-2.0-only or MPL-2.0) and (Apache-2.0 or BSD-3-Clause or MIT or X11) and MIT'],
                    ['GPL-2.0-only', 'MPL-2.0'])

def test_outbound_16():
    _test_expression(['(GPL-2.0-only or MPL-2.0) and (Apache-2.0 or BSD-3-Clause or MIT or X11) and GPL-3.0-or-later'],
                    ['GPL-3.0-or-later'])

def test_outbound_17():
    _test_expression(['(GPL-2.0-only or MPL-2.0) and (Apache-2.0 or MPL-2.0) and (X11 or BSD-3-Clause) and LGPL-2.1-only'],
                    ['GPL-2.0-only', 'MPL-2.0', 'Apache-2.0'])

