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

import json

class JsonFormatter(FormatInterface):

    def format_support_licenses(self, compatibility):
        
        supported_licenses = compatibility.supported_licenses()

        return "JSON implmentation | format_support_licenses(): " + json.dumps(compatibility.supported_licenses())

        
