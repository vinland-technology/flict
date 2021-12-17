#!/bin/bash

# SPDX-FileCopyrightText: 2021 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later

FLICT_DIR=$(dirname ${BASH_SOURCE[0]}/)/../../

FLICT="flict -of json  "

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
    VAL=$(echo ${FLICT} ${OPTIONS} | bash | jq .)
    RET=$?
    
    compare_exit "$RET" "$EXP_RET" "Return values \"$RET\" and \"$EXP_RET\" differs" "$OPTIONS" "$MSG"
    inform "OK"

    SUCC_CNT=$(( $SUCC_CNT + 1 ))

#    echo $VAL
}    


stdin_test()
{
    local FILE=$1
    local OPTIONS="$2"
    local EXP_RET="$3"
    local MSG="$4"

    if [ "$MSG" = "" ]
    then
        MSG=$OPTIONS
    fi
    
    inform_n "${MSG}"
    VAL=$(cat ${FLICT_DIR}/example-data/europe-small.json | ${FLICT} verify -pf - | jq . > /dev/null)
    RET=$?
    
    compare_exit "$RET" "$EXP_RET" "Return values \"$RET\" and \"$EXP_RET\" differs" "$OPTIONS" "$MSG"
    inform "OK"

    SUCC_CNT=$(( $SUCC_CNT + 1 ))

#    echo $VAL
    
}

# list
simple_test "list" 0 

# verify
simple_test "verify -pf ${FLICT_DIR}/example-data/europe-small.json" 0
simple_test "verify -pf ${FLICT_DIR}/example-data/europe-small.json -lcc" 0 
simple_test "verify -pf ${FLICT_DIR}/example-data/europe-small.json -lpl" 0 
stdin_test  "${FLICT_DIR}/example-data/europe-small.json" "verify -pf -" 0 "reading from stdin"
stdin_test  "${FLICT_DIR}/example-data/europe-small.json" "verify -pf - -lcc" 0 "reading from stdin"
stdin_test  "${FLICT_DIR}/example-data/europe-small.json" "verify -pf - -lpl" 0 "reading from stdin"

# outbound-candidate
simple_test "outbound-candidate MIT" 0 
simple_test "outbound-candidate MIT and GPL-2.0-only" 0 

# simplify
simple_test "simplify MIT" 0 
simple_test "simplify MIT and BSD" 0 
simple_test "simplify MIT and GPL-2.0-only WITH Classpath-exception-2.0 and MIT" 0 

# display-compatibility
simple_test "display-compatibility MIT" 0 
simple_test "display-compatibility MIT BSD GPL-2.0-only WITH Classpath-exception-2.0 " 0 


end_test
