#!/usr/bin/python3

###################################################################
#
# flict - FOSS License Compatibility Tool
#
# SPDX-FileCopyrightText: 2020 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later
#
###################################################################

from enum import Enum

try:
    from flict.flictlib.compat_matrix import CompatibilityMatrix
    from flict.flictlib.compat_matrix import CompatMatrixStatus
except ImportError:
    # as compat_matrix imports this module as well, we bail out
    # on circular depedencies
    pass
from flict.flictlib import logger

# Bail out if combinations is greater than...
COMBINATION_THRESHOLD = 10000


class CompatibilityStatus(Enum):
    UNDEFINED = 0
    TRUE = 1
    FALSE = 2
    DEPENDS = 3
    QUESTION = 4


class Compatibility:

    def __init__(self, matrix_file, check_all_licenses=False):
        self.compat_matrix = CompatibilityMatrix(matrix_file)
        self.check_all_licenses = check_all_licenses

    def supported_licenses(self):
        license_set = set(self.compat_matrix.supported_licenses())
        return list(license_set)

    def _supported_license(self, lic):
        matrix_lic = self.compat_matrix.supported_license(lic)
        if matrix_lic is not None:
            return matrix_lic

        return lic

    def _compatibility_status_json(self, status):
        if status == CompatibilityStatus.TRUE:
            return "true"
        elif status == CompatibilityStatus.FALSE:
            return "false"
        elif status == CompatibilityStatus.UNDEFINED:
            return "undefined"
        elif status == CompatibilityStatus.DEPENDS:
            return "depends"
        elif status == CompatibilityStatus.QUESTION:
            return "question"

    def _a_compatible_with_b(self, a, b):
        """wrapper to compat_matrix' method, translates to our enum"""
        compat = self.compat_matrix.a_compatible_with_b(a, b)
        logger.main_logger.debug("ncompat: " + str(compat))
        if compat == CompatMatrixStatus.TRUE:
            return CompatibilityStatus.TRUE
        elif compat == CompatMatrixStatus.FALSE:
            return CompatibilityStatus.FALSE
        elif compat == CompatMatrixStatus.UNDEFINED:
            return CompatibilityStatus.UNDEFINED
        elif compat == CompatMatrixStatus.QUESTION:
            logger.main_logger.debug(" " + a + " " + b + " ==> QUESTION")
            return CompatibilityStatus.QUESTION
        elif compat == CompatMatrixStatus.DEPENDS:
            return CompatibilityStatus.DEPENDS

    def check_compatibility(self, license_set, project):
        license_compatibilities = []
        outbound_candidates = set()
        if self.check_all_licenses:
            supported = self.supported_licenses()
            if 'Compatibility' in supported:
                supported.remove('Compatibility')
            if 'Copyleft' in supported:
                supported.remove('Copyleft')
            licenses_set = set(list(license_set) + supported)
        else:
            licenses_set = license_set

        # For every license among all the licenses
        # - check compat against all licenses
        for license in licenses_set:
            license_compatibility = {}
            license_compatibility['outbound'] = license
            license_compatibility['combinations'] = []
            license_combinations = []
            license_compat_status = False
            if project is not None:

                # loop through project license combinations
                # - this is looping over all the top projects combinations (with its deps)
                # - for every or in the license expression we get noe more combination (of the top project)
                for combination in project.project_combination_list():
                    # keep track of whether the combination's status
                    combination_compat_status = True
                    combination_set = {}

                    status = False
                    # loop through the top project and its deps in this project combination
                    for p in combination:

                        reason = set()
                        # and for each such, loop through license(s)
                        for lic in p['license']:
                            # and check if the license is
                            # a) supported
                            # b) compatible with the top level licenses we're looping over (top loop)
                            _license = self._supported_license(license)
                            _lic = self._supported_license(lic)

                            a_b = self._a_compatible_with_b(_license, _lic)

                            if a_b == CompatibilityStatus.TRUE:
                                pass
                            elif a_b == CompatibilityStatus.FALSE:
                                reason.add(f'{license}" not compatible with "{lic}".')
                            elif a_b == CompatibilityStatus.UNDEFINED:
                                reason.add(f'{license}" has undefined compatibility with "{lic}".')
                            elif a_b == CompatibilityStatus.QUESTION:
                                reason.add(f'{license}" has questioned compatibility with "{lic}".')

                        # do we have compatibility? (check if reason=={})
                        status = (reason == set())
                        combination_compat_status = combination_compat_status and status

                    if combination_compat_status:
                        outbound_candidates.add(license)

                    combination_set['combination'] = combination
                    combination_set['compatibility_fails'] = list(reason)
                    combination_set['compatibility_status'] = status

                    license_combinations.append(combination_set)
                    license_compatibility['combinations'] = license_combinations
            else:
                pass

            # The compat status of this license can be calculated by simply
            # checking if the license is in outbound_candidates
            license_compat_status = (license in outbound_candidates)

            license_compatibility['compatibility_status'] = license_compat_status
            license_compatibilities.append(license_compatibility)

        license_compatibilities_set = {}
        license_compatibilities_set['license_compatibilities'] = license_compatibilities
        outs = list(outbound_candidates)
        outs.sort()
        license_compatibilities_set['outbound_candidates'] = outs
        return license_compatibilities_set

    def check_project_pile(self, project):
        license_expr = project.license()
        license_set = project.license_set()
        self.compatility_report['license'] = license_expr
        self.compatility_report['license_pile'] = list(license_set)

        # Begin checking compatibility with licenses from all project (incl dps)
        self.compatility_report['compatibilities'] = self.check_compatibility(
            license_set, project)
        self.valid = True

    def check(self, project):

        combinations = project.projects_combinations()

        if combinations < COMBINATION_THRESHOLD:
            return self.check_project_pile(project)
        else:
            logger.main_logger.error(
                "***ERROR*** maximum amount of combinations reached")
            logger.main_logger.error(
                "Will use coming method to check compatibility")
            logger.main_logger.error(
                " * current number of combinations: " + str(combinations))
            logger.main_logger.error(
                " * maximum number of combinations: " + str(COMBINATION_THRESHOLD))
            logger.main_logger.error(" * coming method has \"complexity\": 2^ " + str(
                str(project.license_piled_license_check()).count(" OR") + 1).strip())
            self.valid = False
            # All licenses in compat object
            # TODO: do we need this?

    def check_compatibilities(self, licenses, check_all=False):
        """Check compatbilitiy between all licenses"""
        compats = []

        if check_all:
            supported = self.supported_licenses()
            if 'Compatibility' in supported:
                supported.remove('Compatibility')

            # TODO: arrange so we can keep the copylefted licenses
            if 'Copyleft' in supported:
                supported.remove('Copyleft')

            licenses_set = set(licenses + supported)
            outer_licenses = list(licenses_set)
        else:
            outer_licenses = list(licenses)

        for lic_a in outer_licenses:
            inner_licenses = []
            for lic_b in licenses:
                if lic_a == lic_b:
                    continue

                comp_left = self._a_compatible_with_b(lic_a, lic_b)
                comp_right = self._a_compatible_with_b(lic_b, lic_a)

                logger.main_logger.debug("Compatibility check")
                logger.main_logger.debug(f'  compat: {lic_a} ? {lic_b} => {comp_left}')
                logger.main_logger.debug(f'  compat: {lic_b} ? {lic_a} => {comp_right}')

                inner_licenses.append({
                    'license': lic_b,
                    'compatible_right': self._compatibility_status_json(comp_right),
                    'compatible_left': self._compatibility_status_json(comp_left)
                })

            compats.append({
                'license': lic_a,
                'licenses': inner_licenses
            })

        return {
            'compatibilities': compats
        }

    def report(self, project):
        self.compatility_report = {}
        self.check(project)
        if not self.valid:

            self.compatility_report = None
        return self.compatility_report
