# SPDX-FileCopyrightText: 2022 Jens Erdmann
#
# SPDX-License-Identifier: GPL-3.0-or-later

import os
import pytest

from flict.impl import FlictImpl
from tests.args_mock import ArgsMock

TEST_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def test_verify_file():
    prj_file = os.path.join(TEST_DIR, 'example-data/europe-small.json')

    args = ArgsMock(project_file=prj_file)
    ret = FlictImpl(args).verify()
    assert ret != None

    args = ArgsMock(project_file=prj_file, license_combination_count=True)
    ret = FlictImpl(args).verify()
    assert ret != None

    args = ArgsMock(project_file=prj_file, list_project_licenses=True)
    ret = FlictImpl(args).verify()
    assert ret != None

def test_verify_expression():
    args = ArgsMock(license_expression=['MIT'])
    ret = FlictImpl(args).verify()
    assert ret != None
