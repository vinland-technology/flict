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

    RET_SUCCESS = 0
    # 1
    # 2
    # 3
    # 4
    RET_MISSING_ARGS = 5
    # 6
    # 7
    # 8
    # 9

    RET_INVALID_PROJECT = 10
    RET_INVALID_EXPRESSSION = 11


class FLictException(Exception):

    def __init__(self, error_code, error_message):
        self._error_code = error_code
        self._error_message = error_message

    def error_code(self):
        return self._error_code

    def error_message(self):
        return self._error_message
