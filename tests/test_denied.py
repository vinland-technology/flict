# SPDX-FileCopyrightText: 2024 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later

#
# test passing a list of denied licenses to arbiter. None of these should not be returned
# as allowed outbound licenses after a verification of a project (freetype)
#

import json
import pytest

from flict.flictlib.arbiter import Arbiter
from flict.flictlib.return_codes import FlictError, ReturnCodes
from flict.flictlib.project.reader import ProjectReaderFactory

reader = ProjectReaderFactory.get_projectreader(project_format="spdx", project_dirs=["example-data"])
freetype = reader.read_project("example-data/freetype-2.9.spdx.json")

def test_freetype_verification():
    # normal verification
    arbiter = Arbiter()
    verification = arbiter.verify(freetype)
    allowed_outbounds = verification['packages'][0]['allowed_outbound_licenses_aliased']
    expected_allowed = ['FTL', 'Libpng', 'Zlib', 'GPL-2.0-or-later']
    expected_allowed.sort()
    allowed_outbounds.sort()
    assert allowed_outbounds == expected_allowed

def test_freetype_verification_denied1():
    # verification with denied licenses: 'Zlib' 
    arbiter = Arbiter(denied_licenses=['Zlib'])
    verification = arbiter.verify(freetype)
    allowed_outbounds = verification['packages'][0]['allowed_outbound_licenses_aliased']
    expected_allowed = ['FTL', 'Libpng', 'GPL-2.0-or-later']
    expected_allowed.sort()
    allowed_outbounds.sort()
    assert allowed_outbounds == expected_allowed

def test_freetype_verification_denied2():
    # verification with denied licenses: 'FTL', 'Zlib' 
    arbiter = Arbiter(denied_licenses=['FTL', 'Zlib'])
    verification = arbiter.verify(freetype)
    allowed_outbounds = verification['packages'][0]['allowed_outbound_licenses_aliased']
    expected_allowed = ['Libpng', 'GPL-2.0-or-later']
    expected_allowed.sort()
    allowed_outbounds.sort()
    assert allowed_outbounds == expected_allowed

    
