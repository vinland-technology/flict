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

from flict.flictlib.project import Project
from flict.flictlib.report import Report
from flict.flictlib.compatibility import Compatibility
from flict.flictlib.license import LicenseHandler
from flict.var import VAR_DIR

TRANSLATION_FILE   = os.path.join(VAR_DIR, "translation.json")
RELICENSE_FILE     = os.path.join(VAR_DIR, "relicense.json")
from osadl_matrix import OSADL_MATRIX

class ReportTest(unittest.TestCase):

    def test_outbound(self):
        license_handler = LicenseHandler(TRANSLATION_FILE, RELICENSE_FILE, "")
        project = Project(TEST_DIR + "/example-data/imp.json", license_handler)
        compatibility = Compatibility(OSADL_MATRIX, False)
        report_object = Report(project, compatibility)
        report = report_object.report()

        outbounds = report['licensing']['outbound_candidates']
        self.assertEqual(len(outbounds),2)

        self.assertTrue("GPL-2.0-only" in outbounds)
        self.assertTrue("GPL-3.0-only" in outbounds)
        
        
if __name__ == '__main__':
    unittest.main()
