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

from flict.flictlib.format.format import FormatInterface

class TextFormatter(FormatInterface):

    def format_support_licenses(self, compatibility):
        supported_licenses = compatibility.supported_licenses()
        
        ret_str = ""
        for item in supported_licenses:
            lic_group = compatibility.license_group(item)
            if lic_group is not None:
                ret_str += " " + str(item) + ": (" + lic_group + ")\n"
            else:
                ret_str += " " + str(item) + "\n"
        return ret_str

