# SPDX-FileCopyrightText: 2022 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later

import json
import pytest

from flict.impl import FlictImpl
from tests.args_mock import ArgsMock
from flict.flictlib.return_codes import FlictError, ReturnCodes

matrix_file = "tests/mini-matrix.json"
complete_addition_file = "tests/complete-lic-ext.json"
incomplete_addition_file = "tests/incomplete-lic-ext.json"
tmp_test_file = "tmp-test-data.json"

def _test_expression(orig_matrix, additional_matrix, default_no=False):
    args = ArgsMock(license_matrix_file=orig_matrix, license_file=additional_matrix, default_no=default_no)
    return FlictImpl(args).merge_license_db()

def test_incomplete_additional():
    with pytest.raises(FlictError) as _error:
        _test_expression(matrix_file, incomplete_addition_file)
    
def test_incomplete_additional_fix():
    _test_expression(matrix_file, incomplete_addition_file, default_no=True)
    
def test_complete_additional():
    text =_test_expression(matrix_file, complete_addition_file)
    db = json.loads(text)
    db.pop("timestamp", None)
    db.pop("timeformat", None)
    assert len(db) == 4
    
@pytest.fixture(scope='session')
def test_complete_creation():
    text =_test_expression(matrix_file, complete_addition_file)
    db = json.loads(text)
    with open(tmp_test_file, 'w') as fp:
        json.dump(db, fp, indent=4)

def _check_compat(expr):
    args = ArgsMock(license_matrix_file=tmp_test_file, license_expression=[expr])
    impl = FlictImpl(args)
    candidate = impl.suggest_outbound_candidate()
    return candidate
        
@pytest.mark.usefixtures('test_complete_creation')
def test_compat():
    _check_compat("Dummy and BSD-3-Clause")
    
@pytest.mark.usefixtures('test_complete_creation')
def test_compat2():
    _check_compat("Dummy and BSD-3-Clause")
    
    
    
