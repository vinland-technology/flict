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

from enum import Enum


class ReturnCodes(Enum):
    # common

    RET_SUCCESS = (0, "Success")
    # 1
    # 2
    # 3
    # 4
    RET_MISSING_ARGS = (5, "Missing arguments")
    # 6
    # 7
    # 8
    # 9

    RET_INVALID_PROJECT = (10, "Invalid project")
    RET_INVALID_EXPRESSSION = (11, "Invalid expression")
    RET_FILE_NOT_FOUND = (12, "File not found")

    @classmethod
    def get_help(cls, indent="  "):
        """
        Return help string for all defined enum values
        """
        ret = []
        for item in cls.__dict__.keys():
            if not item.startswith("RET_"):
                continue
            _v = getattr(cls, item)
            if not isinstance(_v, Enum):
                continue
            ret.append("{code}: {text}".format(code=_v.value[0], text=_v.value[1]))
        return indent + f"\n{indent}".join(ret)


class FlictException(Exception):

    def __init__(self, error_code, error_message):
        self._error_code = error_code
        self._error_message = error_message

    def error_code(self):
        return self._error_code.value[0]

    def error_message(self):
        return self._error_message
