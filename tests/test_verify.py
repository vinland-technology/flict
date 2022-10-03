#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2022 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest
from flict.flictlib.arbiter import Arbiter
from flict.flictlib.project.reader import ProjectReaderFactory

class TestVerification(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(TestVerification, self).__init__(*args, **kwargs)
        self.arbiter = Arbiter()

    def _verify_verification(self, verification):
        self.assertIsNotNone(verification['project_name'])
        self.assertIsNotNone(verification['packages'])

        for package in verification['packages']:
            self.assertIsNotNone(package['compatibility'])

    def test_zlib_verification(self):
        reader = ProjectReaderFactory.get_projectreader(project_format="spdx")
        zlib = reader.read_project("example-data/zlib-1.2.11.spdx.json")

        verification = self.arbiter.verify(zlib)

        # generic check
        self._verify_verification(verification)

        # zlib specific check
        package = verification['packages'][0]
        compat = package['compatibility'][0]

        compats = package['compatibility']
        self.assertTrue(len(compats)==1)

        self.assertIsNotNone(compat['allowed'])
        allowed = compat['allowed']
        self.assertTrue(allowed)

    def test_freetype_verification(self):
        reader = ProjectReaderFactory.get_projectreader(project_format="spdx", project_dirs=["example-data"])
        freetype = reader.read_project("example-data/freetype-2.9.spdx.json")

        verification = self.arbiter.verify(freetype)

        # generic check
        self._verify_verification(verification)

        # freetype specific check
        package = verification['packages'][0]
        compats = package['compatibility']
        self.assertTrue(len(compats)>1)


if __name__ == '__main__':
    unittest.main()
    
