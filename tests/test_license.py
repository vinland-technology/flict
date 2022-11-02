# SPDX-FileCopyrightText: 2022 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later

import pytest

from flict.flictlib.return_codes import FlictError

from flict.flictlib.license_parser import LicenseParserFactory
from flict.flictlib.license_parser import PrettyLicenseParser


@pytest.fixture(autouse=True)
def parser():
    one_and_only_blessed_parser = LicenseParserFactory.get_parser()
    assert (one_and_only_blessed_parser.utils)
    yield one_and_only_blessed_parser


@pytest.fixture
def parse_single_license(parser):
    yield parser.parse_license


@pytest.fixture
def parse_simple(parse_single_license, lic_expr):
    yield parse_single_license([lic_expr])['license']


@pytest.mark.parametrize('lic_expr', ['MIT', "GPL-2.0-only WITH Classpath-exception-2.0"])
def test_simple_license_result_contain_expected_keys_single_license(parse_simple, lic_expr):
    assert isinstance(parse_simple, dict)
    keys, vals = parse_simple.items()
    assert all((set(keys) == {"license", "type"}, set(vals) == {lic_expr, "name"}))
    assert parse_simple["name"] == lic_expr


@pytest.mark.parametrize('lic_expr', ['MIT AND X11', ])
def test_simple_license_contain_expected_keys_two_licenses(parse_simple, lic_expr):
    assert (isinstance(parse_simple, dict))
    p = parse_simple
    assert p["name"] == "AND"
    assert len(p["operands"]) == 2
    assert p["type"] == "operator"
    assert all((lic["type"] == "license" for lic in p["operands"]))
    assert all((lic["name"] in ("MIT", "X11") for lic in p["operands"]))


def test_licenses_without_duplicates(parser):
    license_list = parser.licenses("MIT and BSD-3-Clause OR X11 AND MIT OR BSD-3-Clause")
    assert {'X11', 'BSD-3-Clause', 'MIT'} == set(license_list)


def test_licenses_with_duplicates(parser):
    license_list = parser.licenses("MIT and BSD-3-Clause AND MIT OR X11 AND MIT OR BSD-3-Clause")
    assert {'X11', 'BSD-3-Clause', 'MIT'} == set(license_list)
