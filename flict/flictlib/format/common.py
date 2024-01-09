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
        'true': {'markdown': '--->'},
        'false': {'markdown': '---|'},
        'undefined': {'markdown': '---U'},
        'depends': {'markdown': '---D'},
        'question': {'markdown': '---Q'},
    },
    'right': {
        'true': {'markdown': '<----'},
        'false': {'markdown': '|--'},
        'undefined': {'markdown': 'U---'},
        'depends': {'markdown': 'D---'},
        'question': {'markdown': 'Q---'},
    },
}

def extract_compatibilities(verification):
    """
    this method assumes 1 package with 1 dependency
    """
    compats = []
    for package in verification['packages']:
        dependency = package['dependencies'][0]
        compats.append({
            'name': package['name'],
            'version': package['version'],
            'original_outbound': package['original_license'],
            'outbound': package['license'],
            'inbound': dependency['license'],
            'original_inbound': dependency['original_license'],
            'result': {
                'outbound_licenses': package['outbound_licenses'],
                'allowed_outbound_licenses': package['allowed_outbound_licenses'],
                'outbound_license': package['outbound_license'],
                'problems': package['problems'],
            },
        })
    return compats
