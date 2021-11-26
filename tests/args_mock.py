# SPDX-FileCopyrightText: 2021 Jens Erdmann
#
# SPDX-License-Identifier: GPL-3.0-or-later


from flict.flictlib import flict_config
from dataclasses import dataclass

@dataclass(frozen=True)
class ArgsMock:
    debug_licenses : bool = False
    enable_scancode : bool = False
    extended_licenses : bool = False
    license_expression : str = ''
    license_group_file : str = flict_config.DEFAULT_GROUP_FILE
    licenses : str = None
    matrix_file : str = flict_config.DEFAULT_MATRIX_FILE
    no_relicense : str = False
    outbound_licenses : str = None
    output_format : str = 'JSON'
    relicense_file : str = flict_config.DEFAULT_RELICENSE_FILE
    scancode_file : str = None
    translations_file : str = flict_config.DEFAULT_TRANSLATIONS_FILE
    verbose : str = False
    version : str = False
