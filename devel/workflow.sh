#!/bin/bash
###################################################################
#
# SPDX-FileCopyrightText: 2021 Jens Erdmann
#
# SPDX-License-Identifier: GPL-3.0-or-later
#
###################################################################


# Python revision to select the docker container
PYTHON_VERSION="${PYTHON_VERSION:-3.9.8}"
# default project directory
PROJECT_DIR="${PROJECT_DIR:-/project}"
# Project source directory
SRC_DIR="${SRC_DIR:-${PWD}}"
# directory to store virtual environment at
VENV_DIR="${VENV_DIR:-/tmp/venv}"
# option to install test dependencies
INSTALL_TEST="${INSTALL_TEST:-1}"
# Docker run arguments
DOCKERARGS="${DOCKERARGS:-\-\-rm}"

start_container()
{
    docker run --rm -it \
        --name flict-container \
        -v ${SRC_DIR}:${PROJECT_DIR} \
        --entrypoint="/bin/bash" \
        python:${PYTHON_VERSION}
}

start_environment()
{
    echo "Creating virtual environment at ${VENV_DIR} ..."
    python3 -m venv ${VENV_DIR}
}

install_dependencies()
{
    . ${VENV_DIR}/bin/activate

    echo "Update python package feed ..."
    python3 -m pip install --upgrade pip

    echo "Install base dependencies ..."
    python3 -m pip install -r ${PROJECT_DIR}/requirements.txt

    if [ "${INSTALL_TEST}" -eq "1" ]; then
        echo "Installing test dependencies ..."
        python3 -m pip install -r ${PROJECT_DIR}/requirements-dev.txt
    fi
}

build()
{
    . ${VENV_DIR}/bin/activate
    cd ${PROJECT_DIR}
    python3 setup.py build
}

install()
{
    . ${VENV_DIR}/bin/activate
    cd ${PROJECT_DIR}
    python3 setup.py install
}

run_tests()
{
    . ${VENV_DIR}/bin/activate
    pytest
}

build_and_install()
{
    build && install    
}

build_install_test()
{
    build && install && run_tests
}

full_workflow()
{
    start_environment && \
    install_dependencies && \
    build && \
    install && \
    run_tests
}

usage()
{
    LAYOUT="\t%-20s\t%s\n"
    printf "flict workflow script\n"
    printf "Except 'container' all commands are expected to be run inside a container.\n"
    printf "Usage: ${0} OPTION\n"
    printf "Options:\n"
    printf "${LAYOUT}" "build" "run build procedure"
    printf "${LAYOUT}" "buildinstall" "run procedure to build and install"
    printf "${LAYOUT}" "buildinstalltest" "run procedure to build, install, and test"
    printf "${LAYOUT}" "container" "start a container to develop in"
    printf "${LAYOUT}" "full" "setup development environment and run build, install, and test"
    printf "${LAYOUT}" "install" "run install procedure"
    printf "${LAYOUT}" "test" "run test procedure"
    printf "${LAYOUT}" "venv" "create virtual environment (Python)"
}

case "${1}" in
    build)
        build
        ;;
    buildinstall)
        build_and_install
        ;;
    buildinstalltest)
        build_install_test
        ;;
    container)
        start_container
        ;;
    dependencies)
        install_dependencies
        ;;
    full)
        full_workflow
        ;;
    install)
        install
        ;;
    test)
        run_tests
        ;;
    venv)
        start_environment
        ;;
    *)
        usage ${0}
        exit 1
        ;;
esac
