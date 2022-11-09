# SPDX-FileCopyrightText: 2022 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later

import datetime
import os

from flict.flictlib.flict_config import flict_version
from flict.flictlib.flict_config import FLICT_HOMEPAGE
from flict.flictlib.flict_config import FLICT_BUGS

def timestamp():
    return str(datetime.datetime.now())


def meta_information(start_time=''):
    uname = os.uname()
    return {
        'os': uname.sysname,
        'osRelease': uname.release,
        'osVersion': uname.version,
        'machine': uname.machine,
        'host': uname.nodename,
        'user': os.environ.get('USER'),
        'start_time': start_time,
        'stop_time': timestamp(),
        'flict': flict_information(),
    }

def flict_information():
    return {
        'tool': 'flict',
        'version': flict_version,
        'homepage': FLICT_HOMEPAGE,
        'issues': FLICT_BUGS,
    }
