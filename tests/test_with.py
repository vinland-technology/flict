# SPDX-FileCopyrightText: 2023 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later

#
# A bug was identified in a "long" license expression with a "WITH"
# statement. These tests checks licenses with WITH to verify things
# seem to be OK.
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

def test_with_0():
    _test_expression('GPL-2.0-only WITH Classpath-exception-2.0',
                     'GPL-2.0-only',
                     'Yes')

def test_with_1():
    _test_expression('X11 AND (GPL-2.0-only WITH Classpath-exception-2.0 OR MIT)',
                     'GPL-2.0-only',
                     'Yes')

def test_with_2():
    _test_expression('X11 AND (GPL-2.0-only WITH Classpath-exception-2.0 OR MIT)',
                     'GPL-3.0-or-later',
                     'Yes')

def test_with_3():
    _test_expression('X11 AND (GPL-2.0-only WITH Classpath-exception-2.0 OR GPL-3.0-only)',
                     'GPL-2.0-only',
                     'Yes')

def test_with_4():
    _test_expression('X11 AND (GPL-2.0-only WITH Classpath-exception-2.0 AND GPL-3.0-only)',
                     'GPL-2.0-only',
                     'No')
    
def test_with_5():
    _test_expression('X11 AND (GPL-2.0-only WITH Classpath-exception-2.0 OR GPL-3.0-only) AND (X11 OR ISC) AND (BSL-1.0 OR BSD-2-Clause)',
                     'GPL-2.0-only',
                     'Yes')
    
def test_with_6():
    _test_expression('X11 AND (GPL-2.0-only WITH Classpath-exception-2.0 AND GPL-3.0-only) AND (X11 OR ISC) AND (BSL-1.0 OR BSD-2-Clause)',
                     'GPL-2.0-only',
                     'No')
    
def test_with_7():
    _test_expression('X11 AND (GPL-2.0-only WITH Classpath-exception-2.0 AND GPL-3.0-only) AND (X11 OR ISC) AND (BSL-1.0 OR BSD-2-Clause) AND (bzip2-1.0.5 OR BSD-1-Clause OR GPL-2.0-only WITH Classpath-exception-2.0 OR X11) AND (GPL-2.0-only WITH Classpath-exception-2.0 AND X11) AND (GPL-2.0-only WITH Classpath-exception-2.0 OR BSD-1-Clause)',
                     'GPL-2.0-only',
                     'No')
    
def test_with_8():
    _test_expression('X11 AND (GPL-2.0-only WITH Classpath-exception-2.0 OR GPL-3.0-only) AND (X11 OR ISC) AND (BSL-1.0 OR BSD-2-Clause) AND (bzip2-1.0.5 OR BSD-1-Clause OR GPL-2.0-only WITH Classpath-exception-2.0 OR X11) AND (GPL-2.0-only WITH Classpath-exception-2.0 AND X11) AND (GPL-2.0-only WITH Classpath-exception-2.0 OR BSD-1-Clause)',
                     'GPL-2.0-only',
                     'Yes')
    
