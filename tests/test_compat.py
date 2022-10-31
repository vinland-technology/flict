#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2022 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest

from flict.flictlib.compatibility import CompatibilityFactory
from flict.flictlib.compatibility import CompatibilityStatus
from flict.flictlib.arbiter import Arbiter
from flict.flictlib.compatibility import CompatibilityLicenseChooser
from flict.flictlib.compatibility import CustomLicenseChooser

class TestCompatibilty(unittest.TestCase):

    def test_check_compat(self):

        compatbility = CompatibilityFactory.get_compatibility()

        compat = compatbility.check_compat("MIT", "MIT")
        self.assertEqual(CompatibilityStatus.LICENSE_COMPATIBILITY_COMPATIBLE.value, compat['compatibility'])

        compat = compatbility.check_compat("MIT", "X11")
        self.assertEqual(CompatibilityStatus.LICENSE_COMPATIBILITY_COMPATIBLE.value, compat['compatibility'])

        compat = compatbility.check_compat("MIT", "GPL-2.0-only")
        self.assertEqual(CompatibilityStatus.LICENSE_COMPATIBILITY_INCOMPATIBLE.value, compat['compatibility'])

        compat = compatbility.check_compat("GPL-2.0-only", "MIT")
        self.assertEqual(CompatibilityStatus.LICENSE_COMPATIBILITY_COMPATIBLE.value, compat['compatibility'])

class TestLicenseChooser(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(TestLicenseChooser, self).__init__(*args, **kwargs)
        self.arbiter = Arbiter()
        self.chooser = CompatibilityLicenseChooser(self.arbiter.supported_licenses())

    def test_license_list(self):
        license_list = self.chooser.list_licenses()
        self.assertTrue(len(license_list)>10)

    def test_one_license(self):
        self.assertEqual(self.chooser.choose(['curl']), 'curl')

    def test_two_license(self):
        self.assertEqual(self.chooser.choose(['curl', 'GPL-2.0-only']), 'curl')
        self.assertEqual(self.chooser.choose(['LGPL-2.1-or-later', 'GPL-2.0-only']), 'LGPL-2.1-or-later')
        self.assertEqual(self.chooser.choose(['X11', 'MIT']), 'X11')
        #license_list = self.choser.list()
        self.assertEqual(self.chooser.choose(['BSD-3-Clause', 'BSD-4-Clause']), 'BSD-3-Clause')
        self.assertEqual(self.chooser.choose(['GPL-2.0-only', 'LGPL-2.1-only']), 'LGPL-2.1-only')

    def test_multiple_license(self):
        self.assertEqual(self.chooser.choose(['curl', 'X11', 'MIT', 'BSD-3-Clause', 'BSD-4-Clause']), 'curl')

class TestCustomLicenseChooser(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(TestCustomLicenseChooser, self).__init__(*args, **kwargs)
        self.chooser = CustomLicenseChooser(['MIT', 'curl', 'BSD-3-Clause', 'X11' ])

    def test_license_list(self):
        license_list = self.chooser.list_licenses()
        self.assertTrue(len(license_list)==4)

    def test_one_license(self):
        self.assertEqual(self.chooser.choose(['curl']), 'curl')

    def test_two_license(self):
        license_list = self.chooser.list_licenses()
        self.assertEqual(self.chooser.choose(['curl', 'MIT']), 'MIT')

    def test_multiple_license(self):
        license_list = self.chooser.list_licenses()
        self.assertEqual(self.chooser.choose(['curl', 'MIT', 'BSD-3-Clause']), 'MIT')


if __name__ == '__main__':
    unittest.main()
