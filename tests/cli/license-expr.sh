#!/bin/bash

# SPDX-FileCopyrightText: 2021 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later


FLICT_DIR=$(dirname ${BASH_SOURCE[0]}/)/../../
if [ "$1" != "" ]
then
    FLICT="$1"
else
    FLICT="PYTHONPATH=${FLICT_DIR} ${FLICT_DIR}/flict/__main__.py"
fi
FLICT="$FLICT simplify "

source $(dirname ${BASH_SOURCE[0]}/)/common-funs
if [ $? -ne 0 ];
then
    echo "Failed reading common-funs... bailing out";
    exit 1;
fi

begin_test

FLICT_CMD="$FLICT "

compare_exec     "$FLICT_CMD MIT"                          \
                 '{"original": "MIT", "simplified": "MIT"}' 0 "MIT only"

compare_exec     "$FLICT_CMD MIT and MIT"                  \
                 '{"original": "MIT and MIT", "simplified": "MIT"}'  0 "Simplify MIT and MIT"

compare_exec     "$FLICT_CMD MIT and MIT and BSD-3-Clause" \
                 '{"original": "MIT and MIT and BSD-3-Clause", "simplified": "BSD-3-Clause AND MIT"}'  0 "MIT and MIT and BSD-3-Clause"

compare_exec     "$FLICT_CMD BSD"                          \
                 '{"original": "BSD", "simplified": "BSD-3-Clause"}' 0 "Expand BSD to BSD-3-Clause"

compare_exec     "$FLICT_CMD MIT and MIT and BSD"          \
                 '{"original": "MIT and MIT and BSD", "simplified": "BSD-3-Clause AND MIT"}' 0 "MIT and .. BSD"

compare_exec     "$FLICT_CMD MIT and MIT or BSD"           \
                 '{"original": "MIT and MIT or BSD", "simplified": "BSD-3-Clause OR MIT"}' 0 "MIT and MIT or BSD"

compare_exec     "$FLICT_CMD GPL-2.0-only"         \
                 '{"original": "GPL-2.0-only", "simplified": "GPL-2.0-only"}' 0 "No relicense GPL-2.0-only"

compare_exec     "$FLICT_CMD GPL-2.0-or-later"     \
                 '{"original": "GPL-2.0-or-later", "simplified": "GPL-2.0-or-later"}' 0 "Relicense GPL-2.0-or-later"

compare_exec     "$FLICT_CMD GPL-2.0-or-later and MIT"     \
                 '{"original": "GPL-2.0-or-later and MIT", "simplified": "GPL-2.0-or-later AND MIT"}' 0 "Relicense GPL-2.0-or-later and MIT"

end_test
