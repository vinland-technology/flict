#!/bin/bash
###################################################################
#
# SPDX-FileCopyrightText: 2022 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later
#
###################################################################

NON_INTERACTIVE=0
if [ "$1" = "-ni" ]
then
    NON_INTERACTIVE=1
fi

handle_ret()
{
    echo "Return code: $1          [args:   $2]"
    echo ""
    echo "Press enter to continue"
    read next
    if [ $1 -ne 0 ]
    then
        exit 1
    fi
}

flct_exec()
{
    if [ $NON_INTERACTIVE -eq 1 ]
    then
        PYTHONPATH=. ./flict/__main__.py $* > /dev/null
        echo -n "$? "
    else
        PYTHONPATH=. ./flict/__main__.py $*
        handle_ret $? "$*"
    fi
}

MERGED_MATRIX=devel/merged.csv

PYTHONPATH=.: ./flict/__main__.py  merge -lf devel/additional_matrix.json > ${MERGED_MATRIX}
flct_exec  verify -il "MIT-style" -ol GPL-3.0-only
flct_exec  -lmf ${MERGED_MATRIX}  verify -ol "MIT-style" -il "GPL-3.0-or-later WITH GCC-exception-3.1"
flct_exec  -of dot display-compatibility X11 BSD-3-Clause  Zlib curl > /dev/null
flct_exec  -lmf  ${MERGED_MATRIX} -of markdown verify -f example-data/cairo-pile-flict.json 
flct_exec  -of markdown verify -s ./example-data/freetype-2.9.spdx.json -sd ./example-data/ 
flct_exec  simplify MIT AND X11 AND MIT AND MIT

PYTHONPATH=.: ./flict/__main__.py -lmf  ${MERGED_MATRIX}  -of  dot display-compatibility  X11 BSD-3-Clause "GPL-3.0-or-later WITH GCC-exception-3.1" Zlib curl > /dev/null
echo

