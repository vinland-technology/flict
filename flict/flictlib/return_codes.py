#!/usr/bin/python3

###################################################################
#
# flict - FOSS License Compatibility Tool
#
# SPDX-FileCopyrightText: 2021 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later
#
###################################################################

from enum import IntEnum

class ReturnCodes(IntEnum):
    # common
    ##" range 0 - 10

    RET_SUCCESS = 0 

    #1
    #2
    RET_MISSING_ARGS = 5

    # verify
    ## range 11 - 20

    # simplify
    ## range 21 -30

    # list
    ## range 31 -40

    # display-compatibility
    ## range 41 - 50

    # outbound-candidate
    ## range 51 - 60

    # policy-report
    ## range 61 - 70


class FLictException(Exception):
    
    def __init__(self, error_code, error_message):
        self.error_code = error_code
        self.error_message = error_message

    def error_code(self):
        return self.error_code

    def error_message(self):
        return self.error_message

