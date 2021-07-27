#!/bin/bash

# SPDX-FileCopyrightText: 2021 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later

FLICT="PYTHONPATH=. flict/__main__.py -ol "

source $(dirname ${BASH_SOURCE[0]}/)/common-funs
if [ $? -ne 0 ];
then
    echo "Failed reading common-funs... bailing out";
    exit 1;
fi

begin_test

compare_exec     "$FLICT 'MIT'"          '["MIT"]' 0 "MIT only"

compare_exec     "$FLICT  'MIT and MIT'" '["MIT"]' 0 "Simplify MIT and MIT "

compare_exec     "$FLICT  'MIT and MIT and BSD-3-Clause'" \
                 '["BSD-3-Clause", "MIT"]' 0 "MIT and MIT and BSD-3-Clause"

compare_exec     "$FLICT  'GPL-2.0-only and (MIT or BSD-3-Clause)'" \
                 '["GPL-2.0-only"]' 0 "GPL-2-only and (MIT or BSD-3-Clause)"

compare_exec     "$FLICT  'GPL-2.0-only or (MIT and BSD-3-Clause)'" \
                 '["BSD-3-Clause", "GPL-2.0-only", "MIT"]' 0 "GPL-2-only or (MIT and BSD-3-Clause)"

compare_exec     "$FLICT  'GPL-2.0-only and (Apache-2.0 or MIT)'" \
                 '["GPL-2.0-only"]' 0 'GPL-2.0-only and (Apache-2.0 or MIT)'

compare_exec     "$FLICT  'GPL-2.0-only or (Apache-2.0 and MIT)'" \
                 '["Apache-2.0", "GPL-2.0-only", "MIT"]' 0 'GPL-2.0-only or (Apache-2.0 and MIT)'

end_test
