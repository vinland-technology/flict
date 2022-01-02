# SPDX-FileCopyrightText: 2022 Jens Erdmann
#
# SPDX-License-Identifier: GPL-3.0-or-later

import pytest

from flict.flictlib.return_codes import FlictError, ReturnCodes
from flict.impl import FlictImpl
from tests.args_mock import ArgsMock

def test_exceptions():
    with pytest.raises(FlictError) as _error:
        args = ArgsMock(license_expression=['MIT and BSD ,,,'])
        FlictImpl(args).simplify()

    assert _error.value.args[0] == ReturnCodes.RET_INVALID_EXPRESSSION

    with pytest.raises(FlictError) as _error:
        args = ArgsMock(license_expression=['MIT ,,,'])
        FlictImpl(args).suggest_outbound_candidate()

    assert _error.value.args[0] == ReturnCodes.RET_INVALID_EXPRESSSION

    with pytest.raises(FlictError) as _error:
        args = ArgsMock(license_expression=['MIT ...'])
        FlictImpl(args).display_compatibility()

    assert _error.value.args[0] == ReturnCodes.RET_INVALID_EXPRESSSION
