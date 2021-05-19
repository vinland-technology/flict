#!/bin/sh
# SPDX-FileCopyrightText: 2021 Konrad Weihmann
# SPDX-License-Identifier: GPL-3.0-or-later
pip3 install -e .[dev] --user
# Replace the development version (git based) by the one from setup.py
sed -i "s#__COMPLIANCE_UTILS_VERSION__#$(python3 setup.py --version)#g" flict/__main__.py
python3 setup.py build sdist && twine upload dist/*