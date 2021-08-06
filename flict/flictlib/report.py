#!/usr/bin/python3

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


def timestamp():
    return str(datetime.datetime.now())


class Report:

    def __init__(self, project, compatibility):
        self.report_map = {}
        self.project = project
        self.compatibility = compatibility

    def report(self):
        self.report_map['meta'] = self.meta()
        self.report_map['project'] = self.project_data()
        self.report_map['compatibility_report'] = self.compatibility.report(
            self.project)
        if self.report_map['compatibility_report'] is None:
            return None
        self.report_map['licensing'] = self.licensing_data()
        return self.report_map

    def project_data(self):
        project_meta = {}
        project_meta['project_file'] = self.project.project_file
        project_meta['project_definition'] = self.project.project
        project_meta['project_pile'] = self.project.dependencies_pile_map()

        return project_meta

    def licensing_data(self):
        licensing = {}

        outbounds = self.report_map['compatibility_report']['compatibilities']['outbound_candidates']
        licensing['outbound_candidates'] = outbounds

        return licensing

    def meta(self):
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
        return json.dumps(self.report_map)


def outbound_candidates(report):
    return report['compatibility_report']['compatibilities']['outbound_candidates']
