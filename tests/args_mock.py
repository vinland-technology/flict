# SPDX-FileCopyrightText: 2021 Jens Erdmann
#
# SPDX-License-Identifier: GPL-3.0-or-later


from flict.flictlib import flict_config
from dataclasses import dataclass

@dataclass(frozen=True)
class ArgsMock:
    debug_licenses : bool = False
    default_no : bool = False
    extended_licenses : bool = False
    license_combination_count : bool = False
    license_expression : str = ''
    licenses : str = None
    list_project_licenses : bool = False
    license_matrix_file : str = flict_config.DEFAULT_MATRIX_FILE
    licenses_info_file = None
    in_license_expr = None
    out_license = None
    outbound_licenses : str = None
    output_format : str = 'JSON'
    verify_flict = None
    verify_sbom = None
    alias_file = None
    licenses_denied_file = None
    licenses_preference_file = None
    licenses_info_file = None
    suggest_outbound_candidate = False
    out_license = None
    in_license = None
    no_relicense = False
    ignore_problems = False
    verbose : str = False
    version : str = False
    def __init__(self, **kwargs):
        for key in kwargs:
            self.__dict__.update({key: kwargs[key]})
