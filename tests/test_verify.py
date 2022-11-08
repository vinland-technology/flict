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
        self.assertEqual(len(compats), 1)

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
        self.assertEqual(len(compats), 4)


    def test_freetype_inner_verification(self):
        reader = ProjectReaderFactory.get_projectreader(project_format="spdx", project_dirs=["example-data"])
        freetype = reader.read_project("example-data/freetype-inner-2.9.spdx.json")

        verification = self.arbiter.verify(freetype)

        # generic check
        self._verify_verification(verification)

        # freetype specific check
        package = verification['packages'][0]
        compats = package['compatibility']
        self.assertEqual(len(compats), 4)


    def test_zlib_no_proper_deps(self):
        """This JSON file has one relationship, but not a valid one
        """
        reader = ProjectReaderFactory.get_projectreader(project_format="spdx", project_dirs=["example-data"])
        zlib = reader.read_project("tests/zlib-no-deps-1.2.11.spdx.json")

        # generic check
        verification = self.arbiter.verify(zlib)
        self._verify_verification(verification)

        # both packages should contain 0 deps
        # - zlib has a relationship that is not "valid"
        # - zlib-doc has no relationships
        for pkg in zlib['packages']:
            self.assertEqual(len(pkg['dependencies']), 0)
            
    def test_zlib_with_deps(self):
        """This JSON file has one valid relationship
        """
        reader = ProjectReaderFactory.get_projectreader(project_format="spdx", project_dirs=["example-data"])
        zlib = reader.read_project("tests/zlib-with-deps-1.2.11.spdx.json")

        verification = self.arbiter.verify(zlib)

        # - zlib has relationships:
        #      one "valid" and one invalid => 1 dep
        # - zlib-libber has no relationships => 0 deps
        for pkg in zlib['packages']:
            if 'defined' in pkg and not pkg['defined']:
                p = pkg['defined']
            if pkg['name'] == 'SPDXRef-Package-zlib-libber':
                self.assertEqual(len(pkg['dependencies']), 0)
            elif pkg['name'] == 'SPDXRef-Package-zlib':
                self.assertEqual(len(pkg['dependencies']), 1)

if __name__ == '__main__':
    unittest.main()
    
