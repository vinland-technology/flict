###################################################################
#
# flict - FOSS License Compatibility Tool
#
# SPDX-FileCopyrightText: 2020 Henrik Sandklef, 2021 Konrad Weihmann
#
# SPDX-License-Identifier: GPL-3.0-or-later
#
###################################################################

import json
import os

from osadl_matrix import OSADL_MATRIX


def read_user_config():
    for path in [
        os.environ.get('FLICT_USERCONFIG'),
        os.path.join(os.environ.get('HOME'), '.flict.cfg')
    ]:
        try:
            with open(path) as i:
                return json.load(i)
        except Exception: # noqa: S110 - it's okay ignore all errors here
            pass
    return {}


_userconfig = read_user_config()

flict_version = "0.1"

SCRIPT_DIR = os.path.realpath(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../"))

# TODO: replace this with something that makes installation easy
VAR_DIR = os.path.join(SCRIPT_DIR, "var")

DEFAULT_TRANSLATIONS_BASE_FILE = "translation.json"
DEFAULT_GROUP_BASE_FILE = "license-group.json"
DEFAULT_RELICENSE_BASE_FILE = "relicense.json"

DEFAULT_TRANSLATIONS_FILE = _userconfig.get('translations-file', os.path.join(VAR_DIR, DEFAULT_TRANSLATIONS_BASE_FILE))
DEFAULT_GROUP_FILE = _userconfig.get('group-file', os.path.join(VAR_DIR, DEFAULT_GROUP_BASE_FILE))
DEFAULT_RELICENSE_FILE = _userconfig.get('relicense-file', os.path.join(VAR_DIR, DEFAULT_RELICENSE_BASE_FILE))
DEFAULT_MATRIX_FILE = _userconfig.get('matrix-file', OSADL_MATRIX)
DEFAULT_OUTPUT_FORMAT = _userconfig.get('output-format', "JSON")
