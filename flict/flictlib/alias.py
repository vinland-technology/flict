#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2022 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later

import json
import os
import re

from flict.flictlib.flict_config import DEFAULT_FLICT_ALIAS_FILE
from flict.flictlib.flict_config import VAR_DIR
from flict.flictlib.return_codes import FlictError, ReturnCodes

FLICT_ALIAS_FILE = os.path.join(VAR_DIR, DEFAULT_FLICT_ALIAS_FILE)


class Alias:

    def __init__(self, alias_file=None):
        try:
            with open(alias_file or FLICT_ALIAS_FILE) as fp:
                self.alias_object = json.load(fp)
        except:
            raise FlictError(ReturnCodes.RET_INVALID_ALIAS_FILE,
                             f'Could not open or parse alias file: {alias_file}')

    def _replace_aliases(self, lic):
        if not lic:
            return None
        for alias in self.alias_object['aliases']:
            if lic == alias['alias']:
                return alias['license']
        return lic

    def replace_aliases(self, license_expr, license_file=None):
        """Replaces license expression aliases (e.g GPLv2+) with supported
        license identifiers (e.g. GPL-2.0-or-later)

        Parameters:
            license_expr - a list of licenses

        """
        if not license_expr:
            return None

        # in case we have multiple spaces separating tokens, remove them
        license_expr = re.sub(r' +', ' ', license_expr)

        new_license_expr = []
        for lic in license_expr.replace(" WITH ", "_WITH_").split():
            new_license_expr.append(self._replace_aliases(lic.replace("_WITH_", " WITH ")))

        return " ".join(new_license_expr)

    def format_aliased(self, lic):
        alias = self.replace_aliases(lic)
        if alias != lic:
            return f'{lic} (aliased to {alias})'
        return lic
