#!/bin/sh
# SPDX-FileCopyrightText: 2021 Konrad Weihmann
# SPDX-License-Identifier: GPL-3.0-or-later
pip3 install -e .[dev] --user
python3 setup.py build sdist && twine upload dist/*