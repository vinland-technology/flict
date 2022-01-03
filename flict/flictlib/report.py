###################################################################
#
# flict - FOSS License Compatibility Tool
#
# SPDX-FileCopyrightText: 2020 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later
#
###################################################################

import datetime
import getpass
import json
import os

from flict.flictlib.compatibility import Compatibility
from flict.flictlib.project import Project


def timestamp():
    return str(datetime.datetime.now())


class Report:

    def __init__(self, project: Project, compatibility: Compatibility):
        self.meta = self.__meta()
        self.project = self.__project_data(project)
        self.compatibility_report = compatibility.report(project)
        self.licensing = self.__licensing_data()

    def __project_data(self, project: Project):
        return {
            'project_file': project.project_file,
            'project_definition': project.project,
            'project_pile': project.dependencies_pile_map()
        }

    def __licensing_data(self):
        return {
            'outbound_candidates': self.outbound_candidates()
        }

    def __meta(self):
        uname = os.uname()
        return {
            'os': uname.sysname,
            'osRelease': uname.release,
            'osVersion': uname.version,
            'machine': uname.machine,
            'host': uname.nodename,
            'user': getpass.getuser(),
            'start': timestamp(),
        }

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__)

    def outbound_candidates(self):
        return self.compatibility_report['compatibilities']['outbound_candidates']
