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


SH_SCRIPTS="$(find cli/ -name '*.sh')"
LOG_FILE=$(dirname ${BASH_SOURCE[0]}/)/all.log

rm -f $LOG_FILE

# Switch to enable CI to generate a JUnit format report
# to be consumed in GitHub pull request UI.
if [ "${JUNIT_REPORT:-0}" -eq "1" ]; then
    PYTEST_ARGS="--junitxml=TEST-pytest-junit.xml"
fi

echo
inform "Python test scripts"
echo "---------------------------------"
sh -c "cd .. && pytest ${PYTEST_ARGS}" || exit 1


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



