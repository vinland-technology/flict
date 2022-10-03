#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2022 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest

from flict.flictlib.compatibility import CompatibilityFactory
from flict.flictlib.compatibility import CompatibilityStatus
from flict.flictlib.arbiter import Arbiter
from flict.flictlib.compatibility import CompatibilityLicenseChoser
from flict.flictlib.compatibility import CustomLicenseChoser

class TestCompatibilty(unittest.TestCase):

    def test_check_compat(self):

        compatbility = CompatibilityFactory.get_compatibility()

        compat = compatbility.check_compat("MIT", "MIT")
        #print("compat: " + str(compat))
        self.assertEqual(CompatibilityStatus.LICENSE_COMPATIBILITY_COMPATIBLE.value, compat['compatibility'])

        compat = compatbility.check_compat("MIT", "X11")
        self.assertEqual(CompatibilityStatus.LICENSE_COMPATIBILITY_COMPATIBLE.value, compat['compatibility'])

        compat = compatbility.check_compat("MIT", "GPL-2.0-only")
        self.assertEqual(CompatibilityStatus.LICENSE_COMPATIBILITY_INCOMPATIBLE.value, compat['compatibility'])

        compat = compatbility.check_compat("GPL-2.0-only", "MIT")
        self.assertEqual(CompatibilityStatus.LICENSE_COMPATIBILITY_COMPATIBLE.value, compat['compatibility'])

class TestLicenseChoser(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(TestLicenseChoser, self).__init__(*args, **kwargs)
        self.arbiter = Arbiter()
        self.choser = CompatibilityLicenseChoser(self.arbiter.supported_licenses())

    def test_license_list(self):
        license_list = self.choser.list()
        #print(str(license_list))
        self.assertTrue(len(license_list)>10)

    def test_one_license(self):
        self.assertEqual(self.choser.chose(['curl']), 'curl')

    def test_two_license(self):
        self.assertEqual(self.choser.chose(['curl', 'GPL-2.0-only']), 'curl')
        self.assertEqual(self.choser.chose(['LGPL-2.1-or-later', 'GPL-2.0-only']), 'LGPL-2.1-or-later')
        self.assertEqual(self.choser.chose(['X11', 'MIT']), 'X11')
        #license_list = self.choser.list()
        #print(str(license_list))
        self.assertEqual(self.choser.chose(['BSD-3-Clause', 'BSD-4-Clause']), 'BSD-3-Clause')
        self.assertEqual(self.choser.chose(['GPL-2.0-only', 'LGPL-2.1-only']), 'LGPL-2.1-only')

    def test_multiple_license(self):
        self.assertEqual(self.choser.chose(['curl', 'X11', 'MIT', 'BSD-3-Clause', 'BSD-4-Clause']), 'curl')

class TestCustomLicenseChoser(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(TestCustomLicenseChoser, self).__init__(*args, **kwargs)
        self.choser = CustomLicenseChoser(['MIT', 'curl', 'BSD-3-Clause', 'X11' ])

    def test_license_list(self):
        license_list = self.choser.list()
        print("wello: " + str(license_list))
        self.assertTrue(len(license_list)==4)

    def test_one_license(self):
        self.assertEqual(self.choser.chose(['curl']), 'curl')

    def test_two_license(self):
        license_list = self.choser.list()
        print("wello: " + str(license_list))
        self.assertEqual(self.choser.chose(['curl', 'MIT']), 'MIT')

    def test_multiple_license(self):
        license_list = self.choser.list()
        print("wello: " + str(license_list))
        self.assertEqual(self.choser.chose(['curl', 'MIT', 'BSD-3-Clause']), 'MIT')


if __name__ == '__main__':
    unittest.main()
