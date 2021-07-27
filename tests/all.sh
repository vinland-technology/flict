#!/bin/bash

# SPDX-FileCopyrightText: 2021 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later

source $(dirname ${BASH_SOURCE[0]}/)/cli/common-funs
if [ $? -ne 0 ];
then
    echo "Failed reading cli/common-funs... bailing out";
    exit 1;
fi


PY_SCRIPTS="test_compat_matrix.py  test_license.py  test_project.py "
SH_SCRIPTS="cli/license-expr.sh cli/outbounds.sh"
LOG_FILE=$(dirname ${BASH_SOURCE[0]}/)/all.log

for ps in $PY_SCRIPTS
do
    inform_n "$ps"
    ./$ps >> $LOG_FILE 2>&1
    exit_on_error $? "Failed running $ps"
    echo "OK"
done

for bs in $SH_SCRIPTS
do
    echo
    echo $bs
    ./$bs
done



