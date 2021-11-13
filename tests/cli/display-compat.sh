#!/bin/bash

# SPDX-FileCopyrightText: 2021 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later

FLICT="flict -of JSON -nr -tf \"\" display-compatibility "

source $(dirname ${BASH_SOURCE[0]}/)/common-funs
if [ $? -ne 0 ];
then
    echo "Failed reading common-funs... bailing out";
    exit 1;
fi

begin_test

FLICT_CMD="$FLICT "

echo "-------------------------"
echo "command: $FLICT_CMD MIT"
echo $FLICT_CMD MIT | sh
echo "-------------------------"
FLICT_CMD="$FLICT_CMD MIT"
echo $FLICT_CMD | bash
echo "-------------------------"
$FLICT_CMD 
echo "-------------------------"



FLICT_CMD="$FLICT_CMD MIT"
compare_exec     "$FLICT_CMD"                          \
                 '{"compatibilities": [{"license": "MIT", "licenses": []}]}' \
                 0 "MIT only"

