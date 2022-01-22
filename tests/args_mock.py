# SPDX-FileCopyrightText: 2021 Jens Erdmann
#
# SPDX-License-Identifier: GPL-3.0-or-later


from flict.flictlib import flict_config
from dataclasses import dataclass

@dataclass(frozen=True)
class ArgsMock:
    debug_licenses : bool = False
    extended_licenses : bool = False
    license_combination_count : bool = False
    license_expression : str = ''
    licenses : str = None
    list_project_licenses : bool = False
    matrix_file : str = flict_config.DEFAULT_MATRIX_FILE
    no_relicense : str = False
    outbound_licenses : str = None
    output_format : str = 'JSON'
    project_file : str = None
    report_file : str = None
    relicense_file : str = flict_config.DEFAULT_RELICENSE_FILE
    translations_file : str = flict_config.DEFAULT_TRANSLATIONS_FILE
    verbose : str = False
    version : str = False
    def __init__(self, **kwargs):
        for key in kwargs:
            self.__dict__.update({key: kwargs[key]})
