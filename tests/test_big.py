# SPDX-FileCopyrightText: 2023 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later

#
# A bug was identified in a "long" license expression. Trying to make
# sure that a really long expression messes things up we're building
# up really long expressions as repetitions of a license expression
# with a known compatibility
#

import json
import pytest

from flict.flictlib.arbiter import Arbiter

arbiter = Arbiter()

def _test_expression(inbound, outbound, result):
    # Check if inbound license is compatible with the outbound license
    # Compare the actual result ("compats") against "result" wich is the expected
    compats = arbiter.inbounds_outbound_check(outbound, [inbound])
    assert result == compats['compatibility']

def test_big_or():
    INBOUND='X11 AND (GPL-2.0-only WITH Classpath-exception-2.0 OR GPL-3.0-only) AND (X11 OR ISC) AND (BSL-1.0 OR BSD-2-Clause) AND (bzip2-1.0.5 OR BSD-1-Clause OR GPL-2.0-only WITH Classpath-exception-2.0 OR X11) AND (GPL-2.0-only WITH Classpath-exception-2.0 AND X11) AND (GPL-2.0-only WITH Classpath-exception-2.0 OR BSD-1-Clause)'
    for i in range(1, 10):
        INBOUND=f'{INBOUND} OR {INBOUND}'
    _test_expression(INBOUND,
                     'GPL-2.0-only',
                     'Yes')

def test_big_and():
    INBOUND='X11 AND (GPL-2.0-only WITH Classpath-exception-2.0 OR GPL-3.0-only) AND (X11 OR ISC) AND (BSL-1.0 OR BSD-2-Clause) AND (bzip2-1.0.5 OR BSD-1-Clause OR GPL-2.0-only WITH Classpath-exception-2.0 OR X11) AND (GPL-2.0-only WITH Classpath-exception-2.0 AND X11) AND (GPL-2.0-only WITH Classpath-exception-2.0 OR BSD-1-Clause)'
    for i in range(1, 10):
        INBOUND=f'{INBOUND} AND {INBOUND}'
    _test_expression(INBOUND,
                     'GPL-2.0-only',
                     'Yes')

def test_big_and_or():
    INBOUND='X11 AND (GPL-2.0-only WITH Classpath-exception-2.0 OR GPL-3.0-only) AND (X11 OR ISC) AND (BSL-1.0 OR BSD-2-Clause) AND (bzip2-1.0.5 OR BSD-1-Clause OR GPL-2.0-only WITH Classpath-exception-2.0 OR X11) AND (GPL-2.0-only WITH Classpath-exception-2.0 AND X11) AND (GPL-2.0-only WITH Classpath-exception-2.0 OR BSD-1-Clause)'
    for i in range(1, 10):
        if i%2 == 0:
            INBOUND=f'{INBOUND} AND {INBOUND}'
        else:
            INBOUND=f'{INBOUND} OR {INBOUND}'
    _test_expression(INBOUND,
                     'GPL-2.0-only',
                     'Yes')

