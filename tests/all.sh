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


PY_SCRIPTS="$(find . -name '*.py' | grep -v __init)"
SH_SCRIPTS="$(find cli/ -name '*.sh')"
LOG_FILE=$(dirname ${BASH_SOURCE[0]}/)/all.log

rm $LOG_FILE

echo
inform "Python test scripts"
echo "---------------------------------"
for ps in $PY_SCRIPTS
do
    inform_n "$ps"
    ./$ps >> $LOG_FILE 2>&1
    exit_on_error $? "Failed running $ps"
    echo "OK"
done


echo
inform "CLI test scripts"
echo "---------------------------------"
for bs in $SH_SCRIPTS
do
    echo $bs
    ./$bs
    echo
done 2>&1 | tee $LOG_FILE

ERRORS=$(grep ERROR $LOG_FILE | wc -l)

exit $ERRORS



