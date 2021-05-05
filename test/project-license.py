#!/bin/python3

# SPDX-FileCopyrightText: 2021 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later

import os
import sys
import unittest

TEST_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Add to PYTHON_PATH
sys.path.insert(0, TEST_DIR)


from argparse import RawTextHelpFormatter
import argparse
import json
from flict.flictlib.project import Project
from flict.flictlib.project import ExpandedProject
import flict.flictlib.license
from flict.flictlib.license import LicenseHandler
from flict.flictlib.license import ManagedLicenseExpression
from flict.flictlib.license import interim_license_expression_list_to_string
from flict.flictlib.license import license_expression_set_list_to_string
import flict.flictlib.relicense 
from license_expression import Licensing, LicenseSymbol

project = None
license_handler = None

PROJECT_FILE="example-data/epiphany-pile-flict-fixed.json"
PROJECT_FILE="example-data/europe-small.json"
#PROJECT_FILE="europe.json"
#PROJECT_FILE="cairo-pile-flict-fixed.json"

def setup():
    global project
    global PROJECT_FILE
    global license_handler
    if license_handler == None:
        license_handler = LicenseHandler("var/translation.json", "var/relicense.json", "")
    if project == None:
        project = Project(PROJECT_FILE, license_handler)

class ProjectAndLicense(unittest.TestCase):

    def test_basic(self):
        setup()
        print("project:    " + str(project))
        print("deps:       " + str(project.dependencies_pile()))

        license_set = project.license_set()
        print("set:        " + str(license_set))

        dep_pile = project.dependencies_pile()

        tot_combinations=1
        print("license_set: " + str(license_set))
        for proj in dep_pile:
            proj_license = proj['license']                
            set_list = license_handler.license_expression_list(proj_license, False).set_list
            size = len(set_list)
            tot_combinations = tot_combinations * size
            print(" * project " + str(proj['name']) + " (" + str(size) + ")")
            for license_set in set_list:
                pass
                #print("   * " + str(license_set))
                #for lic in license_set:
                #    print("     * " + str(lic) + ": " )
        #print("dependencies:         " + str(len(dep_pile)))
        #print("expanded:             " + ','.join(map(str, project.expanded_projects())))
        print(str(project.project_combination_list()))
        #print("license combinations: " + str(self.projects_combinations(license_handler, dep_pile, True)))
        #print("license combinations: " + str(self.projects_combinations(license_handler, dep_pile, False)))

        #expanded_project = ProjectExpander(project, license_handler)
        #print("expanded_project: " + str(expanded_project))

        lic = Licensing()
        EXP="MIT or MPL-1.1"
        parsed = lic.parse(EXP)
        simplified = parsed.simplify()
        #print("lic: " + parsed)
        print("lic: " + str(parsed))
        print("lic: " + str(lic.parse(EXP).simplify()))
        print("lic: " + str(parsed.simplify()))
        print("lic: " + str(simplified))
        
if __name__ == '__main__':
    unittest.main()
