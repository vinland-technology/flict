# SPDX-FileCopyrightText: 2022 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later

import pytest
from flict.flictlib.arbiter import Arbiter
from flict.flictlib.project.reader import ProjectReaderFactory
from flict.flictlib.return_codes import FlictError, ReturnCodes

class Zlib:
    """
    class providing a verification of zlib (SBoM)
    """
    def __init__(self, licenses_preferences=None):
        self._arbiter = Arbiter(licenses_preferences=licenses_preferences)
        self._reader = ProjectReaderFactory.get_projectreader(project_format="spdx")
        self._project = self._reader.read_project("example-data/zlib-1.2.11.spdx.json")
        self._verification = self._arbiter.verify(self._project)
        
    def verification(self):
        return self._verification

def _generic_test(verification):
    # just to make sure verfication seems to be OK
    # before we check details
    assert verification['project_name'] 
    assert verification['packages']

    for package in verification['packages']:
        assert package['compatibility']
    

def test_zlib_verification():
    """
    Simple verification of the zlib verification
    """
    zlib = Zlib()
    verification = zlib.verification()

    _generic_test(verification)

    
def test_zlib_pref_list():
    """
    Verify that an incomplete list of preferences raises a flict error, rather than a generic Python oneq
    """
    
    # Create an incomplete license pref list
    lic_prefs = {
        "license_preferences": [
            "curl", "MIT"
        ]
    }

    # Use the incomplete license pref list, when verifying zlib
    # Make sure an error is raised
    with pytest.raises(FlictError) as _error:
        zlib = Zlib(lic_prefs)
        verification = zlib.verification()

    assert _error.value.args[0] == ReturnCodes.RET_INVALID_LICENSE_PREFERENCE
