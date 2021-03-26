#!/bin/python3

import os
import sys
import unittest
from argparse import RawTextHelpFormatter
import argparse
import json

TEST_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Add to PYTHON_PATH
sys.path.append(TEST_DIR)

from flictlib.project import Project
import flictlib.license
from flictlib.license import LicenseHandler
from flictlib.license import ManagedLicenseExpression
from flictlib.license import license_to_string_long


TRANSLATION_FILE   = TEST_DIR + "/var/translation.json"
RELICENSE_FILE     = TEST_DIR + "/var/relicense.json"
LICENSE_GROUP_FILE = TEST_DIR + "/var/license-group.json"

PROJECT_FILE_SMALL = TEST_DIR + "/example-data/europe-small.json"
PROJECT_FILE_BIG   = TEST_DIR + "/example-data/europe.json"

def setup_small():
    license_handler = LicenseHandler(TRANSLATION_FILE, RELICENSE_FILE, "")
    #compatibility = Compatibility(args.matrix_file, args.scancode_file, args.license_group_file)        
        
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

        # Check flattened dep tree (pile) (implicitly tests dependencies_pile)
        exp_map = "[{'name': 'Europe - a flict example', 'license': 'GPL-3.0-only', 'version': '', 'dependencies': [], 'expanded_license': {'expanded': 'GPL-3.0-only', 'grouped': 'GPL-3.0-only', 'simplified': 'GPL-3.0-only', 'set_list': [['GPL-3.0-only']]}}, {'name': 'Sweden', 'license': 'GPL-2.0-or-later or Apache-2.0 or MPL-1.1', 'version': '', 'dependencies': [], 'expanded_license': {'expanded': '( GPL-3.0-only OR GPL-2.0-only )  or Apache-2.0 or MPL-1.1', 'grouped': '( GPL-3.0-only OR GPL-2.0-only )  or Apache-2.0 or MPL-1.1', 'simplified': 'Apache-2.0 OR GPL-2.0-only OR GPL-3.0-only OR MPL-1.1', 'set_list': [['Apache-2.0'], ['GPL-2.0-only'], ['GPL-3.0-only'], ['MPL-1.1']]}}]"
        self.assertTrue(str(self.project.dependencies_pile_map())==exp_map)

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
        exp_list = ['Apache-2.0', 'GPL-2.0-only', 'GPL-3.0-only', 'MPL-1.1']
        self.assertTrue(lic_set_list == exp_list)

        
    def test_big(self):
        self.project = setup_big()
        self.assertTrue(self.project.name()=="Europe - a flict example")
        self.assertTrue(self.project.license()=="GPL-2.0-or-later and MIT")
        self.assertTrue(str(self.project.dependencies())=="[{'name': 'Sweden', 'license': 'GPL-2.0-only or Apache-2.0', 'dependencies': [{'name': 'Gothenburg', 'license': 'BSD-3-Clause', 'dependencies': []}, {'name': 'Stockholm', 'license': 'MIT', 'dependencies': []}]}, {'name': 'Germany', 'license': 'GPL-2.0-or-later or MIT and BSD-3-Clause or Apache-2.0', 'dependencies': [{'name': 'Dusseldorf', 'license': 'GPL-2.0-or-later', 'dependencies': []}, {'name': 'Berlin', 'license': 'MIT or MPL-1.1', 'dependencies': []}]}]")
        #self.assertTrue(str(self.project.dependencies_pile_map())=="")

        # GPL-2.0-or-later and MIT
        # GPL-2.0-only or Apache-2.0
        # BSD-3-Clause
        # MIT
        # GPL-2.0-or-later or MIT and BSD-3-Clause or Apache-2.0
        # GPL-2.0-or-later
        # MIT or MPL-1.1
        #self.assertTrue(str(self.project.license_pile())=="(GPL-2.0-or-later and MIT) and (GPL-2.0-only or Apache-2.0 and (BSD-3-Clause) and (MIT)) and (GPL-2.0-or-later or MIT and BSD-3-Clause or Apache-2.0 and (GPL-2.0-or-later) and (MIT or MPL-1.1))")
    
        
if __name__ == '__main__':
    unittest.main()
