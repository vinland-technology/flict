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

import json
import os
import sys
import csv
import re
from argparse import RawTextHelpFormatter
import argparse
import flictlib.compatibility
from enum import Enum

VERBOSE=False

class CompatMatrixStatus(Enum):
    UNDEFINED=0
    TRUE=1,
    FALSE=2
    DEPENDS=3

def error(msg):
    sys.stderr.write(msg + "\n")

def verbose(msg):
    global VERBOSE
    if VERBOSE:
        sys.stderr.write(msg)
        sys.stderr.write("\n")
        sys.stderr.flush()

def verbosen(msg):
    global VERBOSE
    if VERBOSE:
        sys.stderr.write(msg)
        sys.stderr.flush()

class CompatibilityMatrix:
    def __init__(self, matrix_file):
        self.matrix_file = matrix_file
        self.matrix_map = None
        self.read_matrix_csv()
    
    def read_matrix_csv(self):
        self.matrix_map={}
        self.matrix_map['matrix_file']=self.matrix_file
        indices_map={}
        license_data=[]
    
        with open(self.matrix_file) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            line_count = 0
            for row in csv_reader:
                #print("ROW: " + str(row))
                if line_count == 0:
                    verbose(str(row) + " cols: " + str(len(row)))
                    col_count = 0
                    for col in row:
                        indices_map[col]=col_count
                        col_count += 1
                    license_data.append(row)
                else:
                    license_row_data=[]
                    for col in row:
                        license_row_data.append(col)
                    if row[0] != license_row_data[0]:
                        error("Could not read matrix file (" + matrix_file + ")")
                        return None
                    license_data.append(license_row_data)
                line_count += 1
        self.matrix_map['license_indices']=indices_map
        self.matrix_map['license_data']=license_data
        #verbose("indices:  " + str(self.matrix_map['license_indices']))
        #verbose("MIT:      " + str(self.matrix_map['license_indices']['MIT']))
        #verbose("data:     " + str(self.matrix_map['license_data']))

    def supported_licenses(self):
        filtered = list(self.matrix_map['license_indices'])
        filtered.pop(0)
        return filtered
        
    def supported_license(self, license):
        if license in self.matrix_map['license_indices']:
            return license
        return None
        
    def compatible_both_ways(self, license_a, license_b):
        value_ab = self.a_compatible_with_b(license_a, license_b).replace("\"","").lower()
        value_ba = self.a_compatible_with_b(license_b, license_a).replace("\"","").lower()
        return value_ab == "yes" and value_ba == "yes"

    def a_compatible_with_b(self, license_a, license_b):
        #print("\n\n****Check: " + license_a + " against " + license_b+ "\n\n")
        value_ab = self._a_compatible_with_b(license_a, license_b)
        if value_ab == None:
            error("Could not check compatibility between \"" + str(license_a) + "\" and \"" + str(license_b) + "\"")
            return CompatMatrixStatus.UNDEFINED

        # TODO: not yes, does not imply no ... could be depends
        lc_value = value_ab.replace("\"","").lower()
        if lc_value == "yes":
            return CompatMatrixStatus.TRUE
        elif lc_value == "no":
            return CompatMatrixStatus.FALSE
        elif lc_value == "Dep.":
            return CompatMatrixStatus.DEPENDS
        else:
            return CompatMatrixStatus.UNDEFINED
        

    def _a_compatible_with_b(self, license_a, license_b):
        indices = self.matrix_map['license_indices']

        if not license_a in indices:
            msg = license_a + " is not a supported license."
            error(msg)
            raise Exception(msg)
        if not license_b in indices:
            msg = license_b + " is not a supported license."
            error(msg)
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
            print("Exception when check compatibility: "  + str(e))
            print(" " + license_a + " index: " + str(index_a))
            print(" " + license_b + " index: " + str(index_b))
            return None

    
    
#
# TODO: move to test file in test dir
#
def test_a_compatible_with_b(compat_matrix, a, b):
    value = compat_matrix.a_compatible_with_b(a, b)
    #print(a + " compatible with " + b + ": " + str(value))
    value = compat_matrix.a_compatible_with_b(b, a)
    #print(b + " compatible with " + a + ": " + str(value))
    value = compat_matrix.compatible(b, a)
    #print(b + " compatible both " + a + ": " + str(value))
    

def main():
    global VERBOSE
    #VERBOSE=True
    compat_matrix = CompatibilityMatrix("osadl-matrix.csv")
    compat_matrix.compatible("MIT", "BSD-3-Clause")
    compat_matrix.compatible("BSD-3-Clause", "MIT")
    compat_matrix.compatible("GPL-2.0-only", "BSD-3-Clause")
    compat_matrix.compatible("BSD-3-Clause", "GPL-2.0-only")
    compat_matrix.compatible("GPL-2.0-only", "LGPL-2.1-only")
    compat_matrix.compatible("LGPL-2.1-only", "GPL-2.0-only")

    test_a_compatible_with_b(compat_matrix, "LGPL-2.1-or-later", "GPL-2.0-only")
    test_a_compatible_with_b(compat_matrix, "BSD-3-Clause", "MIT")

if __name__ == '__main__':
    main()
    
    
