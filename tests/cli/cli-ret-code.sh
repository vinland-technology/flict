#!/bin/bash

# SPDX-FileCopyrightText: 2021 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later

FLICT_DIR=$(dirname ${BASH_SOURCE[0]}/)/../../

FLICT="flict "

source $(dirname ${BASH_SOURCE[0]}/)/common-funs
if [ $? -ne 0 ];
then
    echo "Failed reading common-funs... bailing out";
    exit 1;
fi

begin_test

#
# tests return value alone
# - uses jq to check JSON content
# 
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
#    echo "command: " ${FLICT} ${OPTIONS}
    ${FLICT} ${OPTIONS}  >/dev/null  2>/dev/null
    RET=$?
    compare_exit "$RET" "$EXP_RET" "Return values \"$RET\" and \"$EXP_RET\" differs" "$OPTIONS" "$MSG"
    inform "OK"

    SUCC_CNT=$(( $SUCC_CNT + 1 ))

#    echo "RET:$RET"
}    

# verify,simplify,list,display-compatibility,outbound-candidate,policy-report

# verify
simple_test "verify -pf ${FLICT_DIR}/example-data/europe-small.json" 0
simple_test "verify -pf ${FLICT_DIR}/example-data" 12
simple_test "verify -pf ${FLICT_DIR}/setup.py" 10
simple_test "verify -pf ${FLICT_DIR}/example-data/europe-small.json -lcc" 0 
simple_test "verify -pf ${FLICT_DIR}/example-data/europe-small.json -lpl" 0 

# simplify
simple_test "simplify MIT" 0 
simple_test "simplify MIT and BSD ,,," 11

# display-compatibility
simple_test "display-compatibility MIT" 0 
simple_test "display-compatibility MIT ..." 11

# list
## not possible to do wrong??

# outbound-candidate
simple_test "outbound-candidate MIT" 0 
simple_test "outbound-candidate MIT ,,," 11

end_test
