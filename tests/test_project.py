#!/bin/python3

# SPDX-FileCopyrightText: 2021 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later

import os
import sys
import unittest
from argparse import RawTextHelpFormatter
import argparse
import json

TEST_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Add to PYTHON_PATH
sys.path.insert(0, TEST_DIR)

from flict.flictlib.project import Project
import flict.flictlib.license
from flict.flictlib.license import LicenseHandler
from flict.flictlib.license import ManagedLicenseExpression
from flict.flictlib.license import license_to_string_long
from flict.var import VAR_DIR


TRANSLATION_FILE   = os.path.join(VAR_DIR, "translation.json")
RELICENSE_FILE     = os.path.join(VAR_DIR, "relicense.json")
LICENSE_GROUP_FILE = os.path.join(VAR_DIR, "license-group.json")

PROJECT_FILE_SMALL = TEST_DIR + "/example-data/europe-small.json"
PROJECT_FILE_BIG   = TEST_DIR + "/example-data/europe.json"

def setup_small():
    license_handler = LicenseHandler(TRANSLATION_FILE, RELICENSE_FILE, "")
    #compatibility = Compatibility(args.matrix_file, args.scancode_file, args.license_group_file)        

    #print("readin: "  + str(PROJECT_FILE_SMALL))
    project = Project(PROJECT_FILE_SMALL, license_handler)
    return project

def setup_big():
    license_handler = LicenseHandler(TRANSLATION_FILE, RELICENSE_FILE, "")
    project = Project(PROJECT_FILE_BIG, license_handler)
    return project


class Basic(unittest.TestCase):

    def test_small(self):
        self.project = setup_small()

        # Check name
        self.assertTrue(self.project.name()=="Europe - a flict example")

        # Check declared license
        self.assertTrue(self.project.license()=="GPL-3.0-only")

        # Check dependencies
        self.assertTrue(len(self.project.dependencies())==1)
        self.assertTrue(str(self.project.dependencies())=="[{'name': 'Sweden', 'license': 'GPL-2.0-or-later or Apache-2.0 or MPL-1.1', 'dependencies': []}]")

        # Check license set (as a alist)
        lic_list = list(self.project.license_set())
        lic_list.sort()
        exp_list = "['Apache-2.0', 'GPL-2.0-only', 'GPL-3.0-only', 'MPL-1.1']"
        self.assertTrue(str(lic_list) == str(exp_list))

        actual_map = self.project.dependencies_pile_map()

        if actual_map[0]['name'] == 'Europe - a flict example':
            europe = actual_map[0]
            sweden = actual_map[1]
        else:
            europe = actual_map[1]
            sweden = actual_map[0]


        self.assertEqual(europe['license'], 'GPL-3.0-only')
        self.assertEqual(len(europe['dependencies']), 0)
        self.assertEqual(europe['expanded_license']['expanded'], "GPL-3.0-only")
        self.assertEqual(europe['expanded_license']['grouped'], "GPL-3.0-only")
        self.assertEqual(europe['expanded_license']['simplified'], "GPL-3.0-only")
        self.assertEqual(europe['expanded_license']['set_list'], [["GPL-3.0-only"]])

        self.assertEqual(sweden['license'], 'GPL-2.0-or-later or Apache-2.0 or MPL-1.1')
        self.assertEqual(len(sweden['dependencies']), 0)
        self.assertEqual(sweden['expanded_license']['expanded'], "Apache-2.0 OR  ( GPL-3.0-only OR GPL-2.0-only )  OR MPL-1.1")
        self.assertEqual(sweden['expanded_license']['grouped'], "Apache-2.0 OR  ( GPL-3.0-only OR GPL-2.0-only )  OR MPL-1.1")
        self.assertEqual(sweden['expanded_license']['simplified'], "Apache-2.0 OR GPL-2.0-or-later OR MPL-1.1")
        sweden['expanded_license']['set_list'].sort()
        self.assertEqual(sweden['expanded_license']['set_list'], [['Apache-2.0'], ['GPL-2.0-only'], ['GPL-3.0-only'], ['MPL-1.1']])
        
        # Check number of license combinations
        exp_combinations = 4 
        combinations = self.project.projects_combinations()
        self.assertTrue(exp_combinations == combinations)
        
        
        # Check license combinations
        # 0: Europe (GPL3), Sweden (Apache)
        # 1: Europe (GPL3), Sweden (GPL2)
        # 2: Europe (GPL3), Sweden (GPL3)
        # 3: Europe (GPL3), Sweden (MPL1)
        combination_list = self.project.project_combination_list()
        exp_combos = [
            [
                {'name': 'Europe - a flict example', 'license': ['GPL-3.0-only']},
                {'name': 'Sweden', 'license': ['Apache-2.0'] }
            ],
            [
                {'name': 'Europe - a flict example', 'license': ['GPL-3.0-only']},
                {'name': 'Sweden', 'license': ['GPL-2.0-only'] }
            ],
            [
                {'name': 'Europe - a flict example', 'license': ['GPL-3.0-only']},
                {'name': 'Sweden', 'license': ['GPL-3.0-only'] }
            ],
            [
                {'name': 'Europe - a flict example', 'license': ['GPL-3.0-only']},
                {'name': 'Sweden', 'license': ['MPL-1.1'] }
            ]
        ]
        for x in range(len(exp_combos)):
            for y in range(2):
                cname = combination_list[x][y]['name']
                ename = exp_combos[x][y]['name']
                clic  = str(combination_list[x][y]['license'])
                elic  = str(exp_combos[x][y]['license'])
                #print(cname + " == " + ename)
                #print(clic + " == " + elic)
                self.assertTrue(cname == ename)
                self.assertTrue(clic == elic)
            
        # Check license set
        lic_set_list = list(self.project.license_set())
        lic_set_list.sort()
        exp_list = ['Apache-2.0', 'GPL-2.0-only', 'GPL-3.0-only', 'MPL-1.1'] # keep sorted
        self.assertTrue(lic_set_list == exp_list)

        
    def test_big(self):
        self.project = setup_big()
        self.assertEqual(self.project.name(),"Europe - a flict example")
        self.assertEqual(self.project.license(), "GPL-2.0-or-later and MIT")
        self.assertEqual(len(self.project.dependencies()), 2)
        self.assertEqual(len(self.project.project_combination_list()), 64)

        deps=[]
        for d in self.project.dependencies():
            deps.append(d['name'])
            if d['name'] == "Sweden":
                sweden = d
            elif d['name'] == "Germany":
                germany = d

        # Check depenencies
        self.assertTrue("Europe - a flict example" not in deps)
        self.assertTrue("Sweden" in deps)
        self.assertTrue("Germany" in deps)

        # Check Sweden
        self.assertEqual(sweden['license'], "GPL-2.0-only or Apache-2.0")
        self.assertEqual(len(sweden['dependencies']), 2)
        deps=[]
        for d in sweden['dependencies']:
            self.assertEqual(len(d['dependencies']), 0)
            deps.append(d['name'])
        self.assertTrue("Gothenburg" in deps)
        self.assertTrue("Stockholm" in deps)
        
        # Check Germany
        self.assertEqual(germany['license'], "GPL-2.0-or-later or MIT and BSD-3-Clause or Apache-2.0")
        self.assertEqual(len(germany['dependencies']), 2)
        deps=[]
        for d in germany['dependencies']:
            self.assertEqual(len(d['dependencies']), 0)
            deps.append(d['name'])
        self.assertTrue("Berlin" in deps)
        self.assertTrue("Dusseldorf" in deps)
        
        # Check license set
        lic_set_list = list(self.project.license_set())
        lic_set_list.sort()
        # due to translation Germany's license is now GPL-2.0-or-later,
        # when retrieving the Project's license set:
        #     'GPL-2.0-only'
        #     'GPL-3.0-only'
        exp_list = ['Apache-2.0', 'BSD-3-Clause', 'GPL-2.0-only', 'GPL-3.0-only', 'MIT', 'MPL-1.1'] # keep sorted
        #print("e: " + str(exp_list))
        #print("l: " + str(lic_set_list))
        self.assertTrue(lic_set_list == exp_list)
        
    
        
if __name__ == '__main__':
    unittest.main()
