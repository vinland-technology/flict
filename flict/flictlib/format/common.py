#!/usr/bin/env python3

###################################################################
#
# flict - FOSS License Compatibility Tool
#
# SPDX-FileCopyrightText: 2021 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later
#
###################################################################


compat_interprets = {
    'left': {
        'true':       {'markdown': '--->'},
        'false':      {'markdown': '---|'},
        'undefined':  {'markdown': '---U'},
        'depends':    {'markdown': '---D'},
        'question':   {'markdown': '---Q'},
    },
    'right': {
        'true':       {'markdown': '<----'},
        'false':      {'markdown': '|--'},
        'undefined':  {'markdown': 'U---'},
        'depends':    {'markdown': 'D---'},
        'question':   {'markdown': 'Q---'},
    },
}
