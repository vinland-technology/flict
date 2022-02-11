#!/usr/bin/env python3

###################################################################
#
# flict - FOSS License Compatibility Tool
#
# SPDX-FileCopyrightText: 2020 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later
#
###################################################################

import json
from flict.flictlib import logger
from flict.flictlib.return_codes import FlictError, ReturnCodes


def update_license(translations, license_expr):
    new_license = []
    for license in license_expr.replace("(", " ( ").replace(")", " ) ").split():
        if license in translations['translations_map']:
            new_license.append(translations['translations_map'][license]["spdx_id"])
        else:
            new_license.append(license)
    return ' '.join(new_license)


def update_packages(translations, dependencies):
    updates_deps = []
    for dep in dependencies:
        license = dep["license"].strip()
        dep["license"] = update_license(translations, license)
        dep_deps = dep["dependencies"]
        updates_deps = update_packages(translations, dep_deps)
    return updates_deps


def read_translations(translations_file):
    symbols = {}
    try:
        with open(translations_file) as file_:
            translations_object = json.load(file_)
    except (FileNotFoundError, PermissionError, json.JSONDecodeError):
        raise FlictError(ReturnCodes.RET_FILE_NOT_FOUND,
                         "reading translations file failed")

    translations = translations_object["translations"]
    translations_map = {item['value']: item
                        for item in translations
                        if item.get('translation', False)}

    for item in translations:
        if 'license_expression' in item and 'spdx_id' in item:
            le = item['license_expression'].lower()
            if "scancode" in le:
                logger.main_logger.debug(" IGNORING since scancode")
            else:
                transl = item['spdx_id']
                key = item['license_expression']
                if transl not in symbols:
                    symbols[transl] = []
                symbols[transl].append(key)
        else:
            raise FlictError(ReturnCodes.RET_INVALID_PROJECT,
                             f"Failed parsing item: {item} in translations.")
    results = {'original': translations_object,
               'translations_map': translations_map,
               'symbols': symbols}
    # enabling this crashes lots of tests :)
    # return results
    read_translations.results = results
    return symbols


def read_packages_file(jsonfile, translations):
    try:
        with open(jsonfile) as file_:
            packages = json.load(file_)
    except (FileNotFoundError, PermissionError, json.JSONDecodeError):
        raise FlictError(ReturnCodes.RET_FILE_NOT_FOUND,
                         "reading package file failed")
    # TODO: sync with flict (should be "package")
    package = packages["component"]
    deps = package["dependencies"]
    license = package["license"].strip()
    package["license"] = update_license(translations, license)
    update_packages(translations, deps)
    return packages

