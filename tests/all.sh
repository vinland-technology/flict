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


echo
inform "Python test scripts"
echo "---------------------------------"
sh -c "cd .. && pytest" || exit 1


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

echo LOC stats
printf "Python:   %4s\n" `find . -name "*.py" | xargs wc -l | tail -1 | sed 's,total,,g'`
printf "Bash:     %4s\n" `find . -name "*.sh" | xargs wc -l | tail -1 | sed 's,total,,g'`
printf "Total:    %4s\n" `find . -name "*.py" -o -name "*.sh" | xargs wc -l | tail -1 | sed 's,total,,g'`
exit $ERRORS



