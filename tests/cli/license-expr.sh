#!/bin/bash

# SPDX-FileCopyrightText: 2021 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later

FLICT="PYTHONPATH=.. ../flict/__main__.py -le "

source $(dirname ${BASH_SOURCE[0]}/)/common-funs
if [ $? -ne 0 ];
then
    echo "Failed reading common-funs... bailing out";
    exit 1;
fi

begin_test

FLICT_CMD="PYTHONPATH=. $FLICT verify -le"

compare_exec     "$FLICT_CMD MIT"                            '["MIT"]' 0 "MIT only"
compare_exec     "$FLICT_CMD 'MIT and MIT'"                  '["MIT"]' 0 "Simplify MIT and MIT "
compare_exec     "$FLICT_CMD 'MIT and MIT and BSD-3-Clause'" '["BSD-3-Clause", "MIT"]' 0 "MIT and MIT and BSD-3-Clause"


compare_exec     "$FLICT_CMD 'BSD'"                          '["BSD-3-Clause"]' 0 "Expand BSD to BSD-3-Clause"
compare_exec     "$FLICT_CMD 'MIT and MIT and BSD'"          '["BSD-3-Clause", "MIT"]' 0 "MIT and .. BSD"
compare_exec     "$FLICT_CMD 'MIT and MIT or BSD'"           '["BSD-3-Clause OR MIT]"' 0 "MIT and MIT or BSD"

compare_exec     "$FLICT_CMD 'GPL-2.0-only'"         "GPL-2.0-only" 0 "No relicense GPL-2.0-only"
compare_exec     "$FLICT_CMD 'GPL-2.0-only'"         "GPL-2.0-only" 0 "No relicense GPL-2.0-only"
compare_exec     "$FLICT_CMD 'GPL-2.0-or-later'"     "GPL-2.0-only OR GPL-3.0-only" 0 "Relicense GPL-2.0-or-later"
compare_exec     "$FLICT_CMD 'GPL-2.0-or-later and MIT'"     "MIT AND (GPL-2.0-only OR GPL-3.0-only)" 0 "Relicense GPL-2.0-or-later and MIT"

end_test
