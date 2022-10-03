#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2022 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later

import json
import os
import re

from flict.flictlib.flict_config import DEFAULT_FLICT_ALIAS_FILE
from flict.flictlib.flict_config import VAR_DIR

FLICT_ALIAS_FILE = os.path.join(VAR_DIR, DEFAULT_FLICT_ALIAS_FILE)

alias_object = None


def _read_aliases(alias_file=FLICT_ALIAS_FILE):
    global alias_object
    with open(alias_file) as fp:
        alias_object = json.load(fp)


def _replace_aliases(lic):
    if not lic:
        return None
    for alias in alias_object['aliases']:
        if lic == alias['alias']:
            return alias['license']
    return lic


def replace_aliases(license_expr):
    """Replaces license expression aliases (e.g GPLv2+) with supported
    license identifiers (e.g. GPL-2.0-or-later)

    Parameters:
        license_expr - a list of licenses

    """
    if not license_expr:
        return None

    if not alias_object:
        _read_aliases()

    # in case we have multiple spaces separating tokens, remove them
    license_expr = re.sub(r' +', ' ', license_expr)

    new_license_expr = []
    for lic in license_expr.replace(" WITH ", "_WITH_").split():
        new_license_expr.append(_replace_aliases(lic.replace("_WITH_", " WITH ")))

    return " ".join(new_license_expr)


def format_aliased(lic):
    alias = replace_aliases(lic)
    if alias != lic:
        return lic + " (aliased to " + alias + ")"
    return lic
