# SPDX-FileCopyrightText: 2024 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later

#
# test passing a list of allowed licenses to arbiter. All of these should not be returned
# as allowed outbound licenses after a verification of a project (freetype)
#

import json
import pytest

from flict.flictlib.license import License
from flict.flictlib.arbiter import Arbiter
from flict.flictlib.return_codes import FlictError, ReturnCodes
from flict.flictlib.project.reader import ProjectReaderFactory

reader = ProjectReaderFactory.get_projectreader(project_format="spdx", project_dirs=["example-data"], update_dual=False)
freetype = reader.read_project("example-data/freetype-2.9.spdx.json")

def test_license_clean():
    lic = License(None, None)
    assert lic.license_allowed('MIT')

def test_license_allowed():
    lic = License(None, ['MIT'])
    assert lic.license_allowed('MIT')

def test_license_allowed_false():
    lic = License(None, ['MIT'])
    assert not lic.license_allowed('X11')

def test_license_denined():
    lic = License(['MIT'], None)
    assert lic.license_denied('MIT')

def test_license_denied_false():
    lic = License(['MIT'], None)
    assert not lic.license_denied('X11')

def test_freetype_verification():
    # normal verification
    arbiter = Arbiter(update_dual=False)
    verification = arbiter.verify(freetype)
    allowed_outbounds = verification['packages'][0]['allowed_outbound_licenses']
    expected_allowed = ['FTL', 'Libpng', 'Zlib', 'GPL-2.0-or-later']
    expected_allowed.sort()
    allowed_outbounds.sort()
    assert allowed_outbounds == expected_allowed

def test_freetype_verification_allowed():
    # verification with allowed licenses: 'FTL' 
    arbiter = Arbiter(allowed_licenses=['FTL'], update_dual=False)
    verification = arbiter.verify(freetype)
    allowed_outbounds = verification['packages'][0]['allowed_outbound_licenses']
    expected_allowed = ['FTL']
    expected_allowed.sort()
    allowed_outbounds.sort()
    assert allowed_outbounds == expected_allowed

def test_freetype_verification_allowed():
    # verification with allowed licenses: 'FTL', 'Zlib' 
    arbiter = Arbiter(allowed_licenses=['FTL', 'Zlib'], update_dual=False)
    verification = arbiter.verify(freetype)
    allowed_outbounds = verification['packages'][0]['allowed_outbound_licenses']
    expected_allowed = ['FTL', 'Zlib']
    expected_allowed.sort()
    allowed_outbounds.sort()
    assert allowed_outbounds == expected_allowed

def test_freetype_verification_allowed_denied():
    # verification with allowed and denied licenses: should raise error
    with pytest.raises(FlictError) as _error:
        arbiter = Arbiter(allowed_licenses=['FTL', 'Zlib'], denied_licenses=['FTL', 'Zlib'], update_dual=False)
