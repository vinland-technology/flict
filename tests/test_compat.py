# SPDX-FileCopyrightText: 2021 Jens Erdmann
#
# SPDX-License-Identifier: GPL-3.0-or-later

import pytest

from flict.impl import FlictImpl
from tests.args_mock import ArgsMock

def test_compat():
    args = ArgsMock(license_expression=['MIT'])
    ret = FlictImpl(args).display_compatibility()
    assert '{"compatibilities": [{"license": "MIT", "licenses": []}]}' == ret
