# SPDX-FileCopyrightText: 2024 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later

def create_dummy_project(inbound, outbound):
    _version = 0xdeadc0de
    return {
        'meta': {
            'software':'flict',
            'version': _version
        },
        'project': {
            'name': 'dummy_package',
            'description': 'Dummy package for internal use',
            'version': _version,
            'license': ' '.join(outbound),
            'dependencies': [
                {
                    'name': 'dummy_package',
                    'version': _version,
                    'license': ' '.join(inbound),
                    'dependencies': []
                }
            ]
        }
    }

    
