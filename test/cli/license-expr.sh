#!/bin/bash

FLICT="./flict.py"

source $(dirname ${BASH_SOURCE[0]}/)/common-funs
if [ $? -ne 0 ];
then
    echo "Failed reading common-funs... bailing out";
    exit 1;
fi

begin_test

compare_exec     "$FLICT -le 'MIT'"         "MIT" 0 "MIT only"
compare_exec     "$FLICT -le 'MIT and MIT'" "MIT" 0 "Simplify MIT and MIT "
compare_exec     "$FLICT -le 'MIT and MIT and BSD-3-Clause'" "BSD-3-Clause AND MIT" 0 "MIT and MIT and BSD-3-Clause"


compare_exec     "$FLICT -le 'BSD'"         "BSD-3-Clause" 0 "Expand BSD to BSD-3-Clause"
compare_exec     "$FLICT -le 'MIT and MIT and BSD'" "BSD-3-Clause AND MIT" 0 "MIT and .. BSD"
compare_exec     "$FLICT -le 'MIT and MIT or BSD'" "BSD-3-Clause OR MIT" 0 "MIT and MIT or BSD"

compare_exec     "$FLICT -le 'GPL-2.0-only'"         "GPL-2.0-only" 0 "No relicense GPL-2.0-only"
compare_exec     "$FLICT -le 'GPL-2.0-only'"         "GPL-2.0-only" 0 "No relicense GPL-2.0-only"
compare_exec     "$FLICT -le 'GPL-2.0-or-later'"     "GPL-2.0-only OR GPL-3.0-only" 0 "Relicense GPL-2.0-or-later"
compare_exec     "$FLICT -le 'GPL-2.0-or-later and MIT'"     "MIT AND (GPL-2.0-only OR GPL-3.0-only)" 0 "Relicense GPL-2.0-or-later and MIT"

end_test

