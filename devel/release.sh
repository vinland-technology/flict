#!/bin/bash
###################################################################
#
# SPDX-FileCopyrightText: 2021 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later
#
###################################################################

VERSION=$1

if [ -z ${VERSION} ]
then
    echo "Missing version argument"
    exit 1
fi

if [ "$2" = "--set" ]
then
    echo "Setting and pushing tag"
    git tag -f $VERSION
    if [ $? -ne 0 ]; then echo "Failed setting tag $VERSION"; exit 2; fi

    git push
    if [ $? -ne 0 ]; then echo "Failed pushing"; exit 2; fi
    
    git push --tags --force
    if [ $? -ne 0 ]; then echo "Failed pushing tags"; exit 2; fi

    exit 0
fi

verify()
{
    FLICT_CFG=flict/flictlib/flict_config.py

    if [ ! -f ${FLICT_CFG} ]
    then
        echo "Can't find ${FLICT_CFG} ... when running this script make sure in the top directory"
        exit 1
    fi

    CFG_VERSION=$(grep flict_version ${FLICT_CFG}  | cut -d = -f 2| sed 's,[" ]*,,g')

    GIT_BRANCH=$(git branch | grep "^\*" |awk ' { print $2}')

    GIT_TAG_PRESENT=$(git tag -l | grep -w $VERSION | wc -l)

    # Check versions
    if [ -z "${CFG_VERSION}" ]
    then
        echo "No version found in $FLICT_CFG"
        exit 1
    fi

    if [ "${CFG_VERSION}" != "${VERSION}" ]
    then
        echo "Versions differ"
        echo " * $FLICT_CFG: $CFG_VERSION"
        echo " * argument:   $VERSION"
        exit 1
    fi

    # Check git
    if [ $GIT_TAG_PRESENT -ne 1 ]
    then
        echo "Git tag ($VERSION) not present. Create it"
        exit 1
    fi

    if [ "$GIT_BRANCH" != "main" ]
    then
        echo "Git branch is not main."
        exit 1
    fi

    GIT_DIFFS=$(git diff | wc -l)
    if [ $GIT_DIFFS -ne 0 ]
    then
        echo "Diffs present. Make sure to commit all changes before releasing"
        exit 1
    fi
    
}




verify

inform()
{
    echo " * $*"
}

inform Clean up
rm -fr /tmp/flict_$VERSION

inform Create temp dir
mkdir  /tmp/flict_$VERSION
if [ $? -ne 0 ]; then echo "Failed creating tmp dir"; exit 2; fi

inform Enter temp dir
cd     /tmp/flict_$VERSION
if [ $? -ne 0 ]; then echo "Failed entering tmp dir"; exit 2; fi

inform Clone repo
git clone git@github.com:vinland-technology/flict.git
if [ $? -ne 0 ]; then echo "Failed cloning"; exit 2; fi

inform Enter flict dir
cd flict
if [ $? -ne 0 ]; then echo "Failed entering flict dir"; exit 2; fi

inform Checkout $VERSION
git checkout $VERSION
if [ $? -ne 0 ]; then echo "Failed checking our $VERSION"; exit 2; fi

inform Build
make
if [ $? -ne 0 ]; then echo "Failed testing"; exit 2; fi

inform "All seem to be fine :)"
exit 0

rm -fr .git
if [ $? -ne 0 ]; then echo "Failed removing git dir"; exit 2; fi

rm  /tmp/flict-$VERSION.zip
zip -r  /tmp/flict-$VERSION.zip .
if [ $? -ne 0 ]; then echo "Failed creating zip file "; exit 2; fi

rm    /tmp/flict-$VERSION.tar
tar cvf /tmp/flict-$VERSION.tar .
if [ $? -ne 0 ]; then echo "Failed creating tar file "; exit 2; fi

rm    /tmp/flict-$VERSION.tar.gz
gzip    /tmp/flict-$VERSION.tar
if [ $? -ne 0 ]; then echo "Failed gzipping tar file "; exit 2; fi

ls -al /tmp/flict-$VERSION.tar.gz /tmp/flict-$VERSION.zip 
if [ $? -ne 0 ]; then echo "relese files not present "; exit 2; fi

echo "ALl fine"



