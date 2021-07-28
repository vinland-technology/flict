#!/bin/bash

# SPDX-FileCopyrightText: 2021 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later

FLICT_DIR=$(dirname ${BASH_SOURCE[0]}/)/../../

FLICT="PYTHONPATH=${FLICT_DIR} ${FLICT_DIR}/flict/__main__.py -of json  "

source $(dirname ${BASH_SOURCE[0]}/)/common-funs
if [ $? -ne 0 ];
then
    echo "Failed reading common-funs... bailing out";
    exit 1;
fi

begin_test

simple_test()
{
    local OPTIONS="$1"
    local EXP_RET="$2"
    local MSG="$3"

    if [ "$MSG" = "" ]
    then
        MSG=$OPTIONS
    fi
    
    inform_n "${MSG}"
    VAL=$(echo ${FLICT} ${OPTIONS} | bash | jq .)
    RET=$?
    
    compare_exit "$RET" "$EXP_RET" "Return values \"$RET\" and \"$EXP_RET\" differs" "$OPTIONS" "$MSG"
    inform "OK"

    SUCC_CNT=$(( $SUCC_CNT + 1 ))

#    echo $VAL
}    

simple_test "list" 0 
simple_test "list -g" 0
simple_test "list -lg MIT" 0

end_test
