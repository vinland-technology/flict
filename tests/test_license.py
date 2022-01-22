#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2021 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later

import os
import sys
import unittest

from argparse import RawTextHelpFormatter
import argparse

TEST_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Add to PYTHON_PATH
sys.path.insert(0, TEST_DIR)

import flict.flictlib.license
from   flict.flictlib.license import LicenseHandler
from   flict.flictlib.license import ManagedLicenseExpression
from   flict.flictlib.license import interim_license_expression_list_to_string
from   flict.flictlib.license import license_expression_set_list_to_string
import flict.flictlib.relicense 


license_handler = None
def setup():
    global license_handler
    if license_handler == None:
        license_handler = LicenseHandler("", "", "")

def simplified(license, expected):
    setup()
    global license_handler
    actual = license_handler.license_expression_list(license).simplified
    #print(" \"" + str(actual) + "\"  \"" + expected + "\"")
    return (str(actual) == str(expected))
        
def interim(lic, expected):
    setup()
    global license_handler
    _actual = license_handler.license_expression_list(lic).interim
    actual = interim_license_expression_list_to_string(_actual)
    #print("   \"" + str(actual) + "\"  \"" + expected + "\"")
    return (str(actual) == str(expected))
        
def set_list(lic, expected):
    setup()
    global license_handler
    actual = license_handler.license_expression_list(lic).set_list
    ret = ( len(actual) == len(expected) )
    for act in actual:
        act_list = list(act)
        act_list.sort()
        same = False
        for exp in expected:
            exp_list = list(exp)
            exp_list.sort()
            if exp_list == act_list:
                same = True

        ret = ret and same
        
    return ret

def set_list_old(lic, expected):
    setup()
    global license_handler
    _actual = license_handler.license_expression_list(lic).set_list
    actual = license_expression_set_list_to_string(_actual)
    print("  actual: \"" + str(actual) + "\"  expected: \"" + expected + "\"")
    return (str(actual) == str(expected))
    

class TestSimplified(unittest.TestCase):
    def test_simplified(self):
        self.assertTrue(simplified("A", "A"))
        self.assertTrue(simplified("A and A", "A"))
        self.assertTrue(simplified("A or A", "A"))
        self.assertTrue(simplified("A and B", "A AND B"))
        self.assertTrue(simplified("A or B", "A OR B"))
        self.assertTrue(simplified("A or B and C or A", "A OR (B AND C)"))

class TestInterim(unittest.TestCase):
    def test_interim(self):
        self.assertTrue(interim("A", "AND [A]"))
        self.assertTrue(interim("A or B", "OR [A, B]"))
        self.assertTrue(interim("A or B and C or A", "OR [A, AND [B, C]]"))
        self.assertTrue(interim("A or B and (C or D) ", "OR [A, AND [B, OR [C, D]]]"))

        
class TestSetList(unittest.TestCase):
    def test_set_list(self):
        self.assertTrue(set_list("A", [ ['A'] ]))
        self.assertTrue(set_list("A AND B", [ ['A', 'B']]))
        self.assertTrue(set_list("A or B", [ ['A'], ['B']]))
        self.assertTrue(set_list("A or B and C", [ ['A'], ['B', 'C']]))
        self.assertTrue(set_list("A or B and (C or D and E)", [ ['A'], ['B', 'C'], ['B', 'D', 'E']]))
        self.assertTrue(set_list("A WITH Exception", [ ['A WITH Exception']]))
        self.assertTrue(set_list("A WITH BlaBlaException and MIT", [ ['A WITH BlaBlaException', 'MIT']]))
        self.assertTrue(set_list("A WITH BlaBlaException or MIT", [ ['A WITH BlaBlaException'], ['MIT']]))
        self.assertTrue(set_list("A WITH BlaBlaException AND X11 or MIT", [ ['A WITH BlaBlaException','X11'], ['MIT']]))


        
if __name__ == '__main__':
    unittest.main()
