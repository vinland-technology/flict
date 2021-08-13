#!/bin/bash

# SPDX-FileCopyrightText: 2021 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later

FLICT="flict display-compatibility "

source $(dirname ${BASH_SOURCE[0]}/)/common-funs
if [ $? -ne 0 ];
then
    echo "Failed reading common-funs... bailing out";
    exit 1;
fi

begin_test

FLICT_CMD="$FLICT "

compare_exec     "$FLICT_CMD MIT"                          \
                 '{"compatibilities": [{"license": "MIT", "licenses": []}]}' \
                 0 "MIT only"

compare_exec     "$FLICT_CMD GPL-2.0-only WITH Classpath-exception-2.0"                          \
                 '{"compatibilities": [{"license": "GPL-2.0-only WITH Classpath-exception-2.0", "licenses": []}]}' \
                 0 "GPL-2.0-only WITH Classpath-exception-2.0 only"

compare_exec     "$FLICT_CMD GPL-2.0-only WITH Classpath-exception-2.0 MIT"                          \
                 '{"compatibilities": [{"license": "MIT", "licenses": [{"license": "GPL-2.0-only WITH Classpath-exception-2.0", "compatible_right": "true", "compatible_left": "false"}]}, {"license": "GPL-2.0-only WITH Classpath-exception-2.0", "licenses": [{"license": "MIT", "compatible_right": "false", "compatible_left": "true"}]}]}' \
                 0 "GPL-2.0-only WITH Classpath-exception-2.0 and MIT"



