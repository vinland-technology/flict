# SPDX-FileCopyrightText: 2024 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later
#


import json
from jsonschema import validate
from flict.flictlib.arbiter import Arbiter

#
# The below validates returned data follows schema
#
#

arbiter = Arbiter()
with open('flict/var/schemas/v1/flict-compatibility-report.json') as fp:
    schema = json.load(fp)

def _get_problems(inbound, outbound):
    result = arbiter.verify_outbound_inbound([outbound], [inbound])
    validate(result, schema)

def test_verify_simplae():
    _get_problems('MIT', 'GPL-2.0-only')

def test_verify_uknonwn():
    _get_problems('HPND', 'GPL-2.0-only')

def test_verify_undefined():
    _get_problems('NONESUCH', 'GPL-2.0-only')

def test_verify_2_2_undefined():
    _get_problems('NONESUCH OR WHATSUP', 'NONESUCHEITHER OR WHATSISTHIS')
