#!/bin/bash

# SPDX-FileCopyrightText: 2021 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later

FLICT_DIR=$(dirname ${BASH_SOURCE[0]}/)/../../

source $(dirname ${BASH_SOURCE[0]}/)/common-funs
if [ $? -ne 0 ];
then
    echo "Failed reading common-funs... bailing out";
    exit 1;
fi

begin_test

compare_exec     "flict outbound-candidate 'MIT'"          '["MIT"]' 0 "MIT only"

compare_exec     "flict outbound-candidate  'MIT and MIT'" '["MIT"]' 0 "Simplify MIT and MIT "

compare_exec     "flict outbound-candidate  'MIT and MIT and BSD-3-Clause'" \
                 '["BSD-3-Clause", "MIT"]' 0 "MIT and MIT and BSD-3-Clause"

compare_exec     "flict outbound-candidate  'GPL-2.0-only and (MIT or BSD-3-Clause)'" \
                 '["GPL-2.0-only"]' 0 "GPL-2-only and (MIT or BSD-3-Clause)"

compare_exec     "flict outbound-candidate  'GPL-2.0-only or (MIT and BSD-3-Clause)'" \
                 '["BSD-3-Clause", "GPL-2.0-only", "MIT"]' 0 "GPL-2-only or (MIT and BSD-3-Clause)"

compare_exec     "flict outbound-candidate  'GPL-2.0-only and (Apache-2.0 or MIT)'" \
                 '["GPL-2.0-only"]' 0 'GPL-2.0-only and (Apache-2.0 or MIT)'

compare_exec     "flict outbound-candidate  'GPL-2.0-only or (Apache-2.0 and MIT)'" \
                 '["Apache-2.0", "GPL-2.0-only", "MIT"]' 0 'GPL-2.0-only or (Apache-2.0 and MIT)'

compare_exec     "flict outbound-candidate  'GPL-2.0-only and Apache-2.0'" \
                 '[]' 0 'GPL-2.0-only and Apache-2.0'

# no relicense
compare_exec     "flict -nr outbound-candidate  'GPL-2.0-only and MPL-2.0'" \
                 '["GPL-2.0-only"]' 0 'GPL-2.0-only and MPL-2.0'

# no relicense
compare_exec     "flict -rf \"\" outbound-candidate  'GPL-2.0-only and MPL-2.0'" \
                 '["GPL-2.0-only"]' 0 'GPL-2.0-only and MPL-2.0'

compare_exec     "flict outbound-candidate  'GPL-2.0-only and Apache-2.0 and MPL-2.0'" \
                 '[]' 0 'GPL-2.0-only and Apache-2.0 and MPL-2.0'

compare_exec     "flict outbound-candidate  'GPL-2.0-only and MPL-2.0'" \
                 '["GPL-2.0-only", "GPL-2.0-or-later"]' 0 'GPL-2.0-only and MPL-2.0'

compare_exec     "flict outbound-candidate  'GPL-2.0-only and MPL-2.0'" \
                 '["GPL-2.0-only", "GPL-2.0-or-later"]' 0 'GPL-2.0-only and MPL-2.0'

compare_exec     "flict outbound-candidate  'GPL-2.0-only and (MPL-2.0 or Apache-2.0) and BSD-3-Clause'" \
                 '["GPL-2.0-only", "GPL-2.0-or-later"]' 0 'GPL-2.0-only and (MPL-2.0 or Apache-2.0) and BSD-3-Clause'

compare_exec     "flict outbound-candidate  '(GPL-2.0-only or MPL-2.0) and (Apache-2.0 or BSD-3-Clause)'" \
                 '["AGPL-3.0-or-later", "GPL-2.0-only", "GPL-2.0-or-later", "GPL-3.0-or-later", "LGPL-2.1-or-later"]' 0 ''

end_test
