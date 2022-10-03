#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2022 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later

import datetime
import os


def timestamp():
    return str(datetime.datetime.now())


def meta_information(start_time=""):
    uname = os.uname()
    return {
        'os': uname.sysname,
        'osRelease': uname.release,
        'osVersion': uname.version,
        'machine': uname.machine,
        'host': uname.nodename,
        'user': os.environ.get('USER'),
        "start_time": start_time,
        'stop_time': timestamp()
    }

