# SPDX-FileCopyrightText: 2024 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later
#


import json
from jsonschema import validate
from flict.flictlib.arbiter import Arbiter

#
# The below tests the problems returned by verify
#
#

arbiter = Arbiter()
with open('flict/var/schemas/v1/flict-compatibility-report.json') as fp:
    schema = json.load(fp)

def _get_problems(inbound, outbound):
    result = arbiter.verify_outbound_inbound([outbound], [inbound])
    validate(result, schema)
    return result['result']['problems']

def test_problems_no():
    assert len(_get_problems('MIT', 'GPL-2.0-only')) == 0

def test_problems_uknonwn():
    assert len(_get_problems('HPND', 'GPL-2.0-only')) == 1

def test_problems_undefined():
    assert len(_get_problems('NONESUCH', 'GPL-2.0-only')) == 1

def test_problems_1_1_undefined():
    assert len(_get_problems('NONESUCH', 'NONESUCHEITHER')) == 2

def test_problems_1_2_undefined():
    # 1:2 licenses, this gives us 6 otubound vs inbound combos
    assert len(_get_problems('NONESUCH', 'NONESUCHEITHER OR WHATSISTHIS')) == 6

def test_problems_2_2_undefined():
    # 2:2 licenses, this gives us 8 otubound vs inbound combos
    assert len(_get_problems('NONESUCH OR WHATSUP', 'NONESUCHEITHER OR WHATSISTHIS')) == 8

def test_problems_2_3_undefined():
    # 2:3 licenses, this gives us 15 otubound vs inbound combos
    assert len(_get_problems('NONESUCH OR WHATSUP', 'NONESUCHEITHER OR WHATSISTHIS OR OHNO')) == 15

def test_problems_2_5_undefined():
    # 2:5 licenses, this gives us 35 (5 * (5+2)) otubound vs inbound combos
    assert len(_get_problems('NONESUCH OR WHATSUP', 'NONESUCHEITHER OR WHATSISTHIS OR OHNO OR DRNO OR DRHOOK')) == 35

