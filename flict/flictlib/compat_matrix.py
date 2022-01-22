#!/usr/bin/env python3

###################################################################
#
# flict - FOSS License Compatibility Tool
#
# SPDX-FileCopyrightText: 2020 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later
#
###################################################################

import csv
from flict.flictlib import logger
from enum import Enum


class CompatMatrixStatus(Enum):
    UNDEFINED = 0
    TRUE = 1
    FALSE = 2
    DEPENDS = 3
    QUESTION = 4


class CompatibilityMatrix:
    def __init__(self, matrix_file):
        self.matrix_file = matrix_file
        self.matrix_map = None
        self.read_matrix_csv()

    def read_matrix_csv(self):
        indices_map = {}
        license_data = []

        with open(self.matrix_file) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            line_count = 0
            for row in csv_reader:
                #print("ROW: " + str(row))
                if line_count == 0:
                    logger.main_logger.debug(f'{row} cols: {len(row)}')
                    col_count = 0
                    for col in row:
                        indices_map[col] = col_count
                        col_count += 1
                    license_data.append(row)
                else:
                    license_row_data = []
                    for col in row:
                        license_row_data.append(col)
                    if row[0] != license_row_data[0]:
                        logger.main_logger.error(f'Could not read matrix file ({self.matrix_file})')
                        return None
                    license_data.append(license_row_data)
                line_count += 1

        self.matrix_map = {
            'matrix_file': self.matrix_file,
            'license_indices': indices_map,
            'license_data': license_data
        }
        #logger.main_logger.debug("indices:  " + str(self.matrix_map['license_indices']))
        #logger.main_logger.debug("MIT:      " + str(self.matrix_map['license_indices']['MIT']))
        #logger.main_logger.debug("data:     " + str(self.matrix_map['license_data']))

    def supported_licenses(self):
        filtered = list(self.matrix_map['license_indices'])
        filtered.pop(0)
        return filtered

    def supported_license(self, license):
        if license in self.matrix_map['license_indices']:
            return license
        return None

    def compatible_both_ways(self, license_a, license_b):
        value_ab = self.a_compatible_with_b(
            license_a, license_b).replace("\"", "").lower()
        value_ba = self.a_compatible_with_b(
            license_b, license_a).replace("\"", "").lower()
        return value_ab == "yes" and value_ba == "yes"

    def a_compatible_with_b(self, license_a, license_b):
        #print("\n\n****Check: " + license_a + " against " + license_b+ "\n\n")
        value_ab = self._a_compatible_with_b(license_a, license_b)
        if value_ab is None:
            logger.main_logger.error(f'Could not check compatibility between "{license_a}" and "{license_b}"')
            return CompatMatrixStatus.UNDEFINED

        # TODO: not yes, does not imply no ... could be depends
        lc_value = value_ab.replace("\"", "").lower().replace(
            " ", "").replace("\t", "")
        if lc_value in ["yes", "same"]:
            return CompatMatrixStatus.TRUE
        elif lc_value == "no":
            return CompatMatrixStatus.FALSE
        elif lc_value == "dep.":
            return CompatMatrixStatus.DEPENDS
        elif lc_value == "?":
            return CompatMatrixStatus.QUESTION
        else:
            logger.main_logger.error(f'compat sign: {lc_value}')
            return CompatMatrixStatus.UNDEFINED

    def _a_compatible_with_b(self, license_a, license_b):
        indices = self.matrix_map['license_indices']

        if license_a not in indices:
            msg = f'{license_a} is not a supported license.'
            logger.main_logger.error(msg)
            raise Exception(msg)
        if license_b not in indices:
            msg = f'{license_b} is not a supported license.'
            logger.main_logger.error(msg)
            raise Exception(msg)

        index_a = indices[license_a]
        index_b = indices[license_b]
        try:
            #print(license_a + "(" + str(index_a) + ") compatible with ", end="")
            #print(license_b + "(" + str(index_b) + "): ", end="")
            #print("\"" + str(self.matrix_map['license_data'][index_a][index_b]) + "\"", end="")
            #print(" | rev : " + str(self.matrix_map['license_data'][index_a][0]), end="")
            #print(" , " + str(self.matrix_map['license_data'][index_b][0]))

            value = self.matrix_map['license_data'][index_a][index_b]
            if value == "":
                value = "Yes"
            return value
        except Exception as e:
            # TODO: no print, rather raise exception?
            logger.main_logger.exception(
                msg="Exception when check compatibility: ", exc_info=e)
            print(f' {license_a} index: {index_a}')
            print(f' {license_b} index: {index_b}')
            return None
