#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2023 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later

import pytest

from flict.flictlib.arbiter import Arbiter
from flict.flictlib.return_codes import FlictError
from flict.flictlib.compatibility import CompatibilityFactory
from flict.flictlib.compatibility import CompatibilityStatus


#
# Test singe licenses against each other
#

def test_compat_known():
    compatbility = CompatibilityFactory.get_compatibility()
    compat = compatbility.check_compat("MIT", "MIT")
    assert CompatibilityStatus.LICENSE_COMPATIBILITY_COMPATIBLE.value == compat['compatibility']

def test_compat_unknown_inbound():
    compatbility = CompatibilityFactory.get_compatibility()
    compat = compatbility.check_compat("MIT", "NONESUCHNLICENSE")
    assert CompatibilityStatus.LICENSE_COMPATIBILITY_UNKNOWN.value == compat['compatibility']

def test_compat_unknown_outbound():
    compatbility = CompatibilityFactory.get_compatibility()
    compat = compatbility.check_compat("NONESUCHNLICENSE", "MIT")
    assert CompatibilityStatus.LICENSE_COMPATIBILITY_UNDEFINED.value == compat['compatibility']

#
# Test license expressions against outbound
#

def test_verify_i_o_check_known():
    arbiter = Arbiter()
    compats = arbiter.inbounds_outbound_check("MIT", ["MIT"])
    assert CompatibilityStatus.LICENSE_COMPATIBILITY_COMPATIBLE.value == compats['compatibility']

def test_verify_i_o_check_unknown_inbound():
    arbiter = Arbiter()
    compats = arbiter.inbounds_outbound_check("MIT", ["NONESUCHNLICENSE"])
    # unknown license gives unknown compatibility
    assert CompatibilityStatus.LICENSE_COMPATIBILITY_UNKNOWN.value == compats['compatibility']

def test_verify_i_o_check_mix_inbound1or():
    arbiter = Arbiter()
    compats = arbiter.inbounds_outbound_check("MIT", ["NONESUCHNLICENSE OR X11"])
    # MIT is compatible with X11, so the result is compatible even though NONESUCHNLICENSE is not compatible
    assert CompatibilityStatus.LICENSE_COMPATIBILITY_COMPATIBLE.value == compats['compatibility']

def test_verify_i_o_check_mix_inbound1and():
    arbiter = Arbiter()
    compats = arbiter.inbounds_outbound_check("MIT", ["NONESUCHNLICENSE AND X11"])
    # MIT is compatible with X11 but not NONESUCHNLICENSE, so incompatible
    assert CompatibilityStatus.LICENSE_COMPATIBILITY_INCOMPATIBLE.value == compats['compatibility']

def test_verify_i_o_check_mix_inbound2or():
    arbiter = Arbiter()
    compats = arbiter.inbounds_outbound_check("MIT", ["NONESUCHNLICENSE OR NOTTHISEITHER"])
    # Both inbound are unknown, so incompatible
    assert CompatibilityStatus.LICENSE_COMPATIBILITY_INCOMPATIBLE.value == compats['compatibility']

def test_verify_i_o_check_mix_inbound2and():
    arbiter = Arbiter()
    compats = arbiter.inbounds_outbound_check("MIT", ["NONESUCHNLICENSE AND NOTTHISEITHER"])
    # Both inbound are unknown, so incompatible
    assert CompatibilityStatus.LICENSE_COMPATIBILITY_INCOMPATIBLE.value == compats['compatibility']

def test_verify_i_o_check_mix_inbound3or():
    arbiter = Arbiter()
    compats = arbiter.inbounds_outbound_check("MIT", ["NONESUCHNLICENSE OR NOTTHISEITHER OR MIT"])
    # MIT is compatible with X11 so even thouth not the other two are not compatible, the whole thing is compatible
    assert CompatibilityStatus.LICENSE_COMPATIBILITY_COMPATIBLE.value == compats['compatibility']
                    
def test_verify_i_o_check_mix_inbound3and():
    arbiter = Arbiter()
    compats = arbiter.inbounds_outbound_check("MIT", ["NONESUCHNLICENSE AND NOTTHISEITHER AND MIT"])
    # MIT is compatible with X11 but not the other two, so incompatible
    assert CompatibilityStatus.LICENSE_COMPATIBILITY_INCOMPATIBLE.value == compats['compatibility']

def test_verify_i_o_check_unknown_outbound():
    arbiter = Arbiter()
    # an unknown outbound is illegal and will raise a FlictError
    compats = arbiter.inbounds_outbound_check("NONESUCHNLICENSE", ["MIT"])
    assert CompatibilityStatus.LICENSE_COMPATIBILITY_UNDEFINED.value == compats['compatibility']

def test_verify_i_o_check_unknown_all():
    arbiter = Arbiter()
    # an unknown outbound is illegal and will raise a FlictError
    compats = arbiter.inbounds_outbound_check("NONESUCHNLICENSE", ["NOLICENSE"])
    assert CompatibilityStatus.LICENSE_COMPATIBILITY_UNKNOWN.value == compats['compatibility']
