# SPDX-FileCopyrightText: 2022 Jens Erdmann
#
# SPDX-License-Identifier: GPL-3.0-or-later

import os
import pytest

from flict.flictlib.return_codes import FlictError, ReturnCodes
from flict.impl import FlictImpl
from tests.args_mock import ArgsMock

TEST_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

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

    with pytest.raises(FlictError) as _error:
        prj = os.path.join(TEST_DIR, 'example-data')
        args = ArgsMock(project_file=prj)
        FlictImpl(args).verify()

    assert _error.value.args[0] == ReturnCodes.RET_FILE_NOT_FOUND

    with pytest.raises(FlictError) as _error:
        prj = os.path.join(TEST_DIR, 'setup.py')
        args = ArgsMock(project_file=prj)
        FlictImpl(args).verify()

    assert _error.value.args[0] == ReturnCodes.RET_INVALID_PROJECT

    with pytest.raises(FlictError) as _error:
        prj = os.path.join(TEST_DIR, 'example-data/europe-small-bad.json')
        args = ArgsMock(project_file=prj)
        FlictImpl(args).verify()

    assert _error.value.args[0] == ReturnCodes.RET_INVALID_PROJECT
