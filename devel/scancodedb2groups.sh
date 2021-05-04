#!/bin/bash
# yes bash ;)

###################################################################
#
# SPDX-FileCopyrightText: 2021 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later
#
###################################################################

SCANCODE_DB_URL="https://scancode-licensedb.aboutcode.org/"
SCANCODE_DB_HTML=/tmp/${USER}-flict-scancodedb.html

TMP_FILE=/tmp/${USER}-flict-scancodedb.tmp

error()
{
    echo "$*" >&2
}

errorn()
{
    echo -n "$*" >&2
}

exit_if_error()
{
    RET=$1
    if [ $RET -ne 0 ]
    then
        error "Error"
        if [ "$2" != "" ]
        then
            error " error message: $2"
        fi
        exit $RET
    fi
}

#
# Get html page
# 
if [ ! -s "${SCANCODE_DB_HTML}" ]
then
    curl "${SCANCODE_DB_URL}" -o "${SCANCODE_DB_HTML}"
    exit_if_error $?
fi

#
# Get tbody
#
sed -n '/<tbody/,/<\/tbody/p' "${SCANCODE_DB_HTML}" \
    | grep -v -e "tbody>" \
    | grep -v -e "^[ \t]*$" \
           > ${TMP_FILE}

DATA_DATE=$(grep -i generated "${SCANCODE_DB_HTML}" | cut -d ">" -f 4 | cut -d "<" -f 1 | sed -e 's,^[ \t]*[0-9\.]* on,,g' -e 's,\.$,,g' -e 's,^[ ]*,,g')

echo "{"
echo "    \"meta\": {"
echo "        \"software\":\"FOSS License Compliance Tool\","
echo "        \"type\": \"Scancode licenses\","
echo "        \"version\":\"0.1\","
echo "        \"date\":\"$(LC_ALL=en.US date '+%Y-%m-%d %H:%M:%S')\""
echo "    },"
echo "    \"original_data\" : {"
echo "        \"source\": \"https://scancode-licensedb.aboutcode.org/\","
echo "        \"date\": \"${DATA_DATE}\","
echo "        \"license\": \"Creative Commons Attribution License 4.0 (CC-BY-4.0)\","
echo "        \"license_url\": \"https://scancode-licensedb.aboutcode.org/cc-by-4.0.html\""
echo "    },"
echo "    \"scancode_licenses\": ["

ITEMS=0
CNT=0
while read _LINE
do
    LINE=$( echo $_LINE | sed -e 's,^[ \t]*,,g' -e 's,",,g')
    if [ "$LINE" = "<tr>" ]
    then
        CNT=0
    elif [ "$LINE" = "</tr>" ]
    then
        if [ $ITEMS -ne 0 ]
        then
            echo "        ,"
        fi
        ITEMS=$(( $ITEMS + 1 ))
        echo "        {"
        echo "            \"key\": \"$KEY\"",
        echo "            \"short_name\": \"$SHORT\"",
        echo "            \"spdx\": \"$SPDX\"",
        echo "            \"group\": \"$CAT\"",
        echo "            \"link\": \"$LINK\""
        echo "        }"
    fi
    #echo $CNT ": \"$LINE\""
    case $CNT in
        1)
            KEY=$(echo $LINE | cut -d ">" -f 3 | cut -d "<" -f 1)
            ;;
        2)
            SHORT=$(echo $LINE | sed 's,<[/]*td>,,g')
            ;;
        4)
            SPDX=$(echo $LINE | cut -d "=" -f 2 | cut -d ">" -f 2 | sed -e 's,</a[>]*,,g' -e 's,^-$,,g')
            ;;
        7)
            CAT=$(echo $LINE  | cut -d ";" -f 2 | sed -e s',[\"]*>,,g' -e 's,</a[>]*,,g')
            ;;
        12)
            LINK_=$(echo $LINE | cut -d ">" -f 1 | cut -d "=" -f 2 | sed 's,",,g')
            LINK="https://scancode-licensedb.aboutcode.org/${LINK_}"
    esac
    CNT=$(( $CNT + 1 ))
    #errorn "."
    #if [ $ITEMS -gt 2 ];
    #then
    #    break
    #fi
done < ${TMP_FILE}

echo "    ]"
echo "}"

error "$ITEMS added"
