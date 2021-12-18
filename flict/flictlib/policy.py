#!/usr/bin/python3

###################################################################
#
# flict - FOSS License Compatibility Tool
#
# SPDX-FileCopyrightText: 2021 Henrik Sandklef
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


class Policy:
    def __init__(self, policy_file):
        self.policy_report = {}
        self.policy_report['meta'] = self.meta()
        self.policy_report['policy_file'] = policy_file
        with open(policy_file) as fp:
            self.policy_report['policy'] = json.load(fp)

    def report(self, report):
        if self.policy_report['policy'] is None:
            return None

        policy = self.policy_report['policy']['policy']

        outbounds = report['licensing']['outbound_candidates']
        allowed = policy.get('allowlist', [])
        avoid = policy.get('avoidlist', [])
        denied = policy.get('denylist', [])

        #nr_outbounds = len(outbounds)

        allowed_outbound_candidates = set()
        avoid_outbound_candidates = set()
        denied_outbound_candidates = set()

        for out_lic in outbounds:
            if out_lic in allowed:
                allowed_outbound_candidates.add(out_lic)
            elif out_lic in avoid:
                avoid_outbound_candidates.add(out_lic)
            elif out_lic in denied:
                denied_outbound_candidates.add(out_lic)
            else:
                allowed_outbound_candidates.add(out_lic)

        result = 2
        if len(allowed_outbound_candidates) > 0:
            result = 0
        elif len(avoid_outbound_candidates) > 0:
            result = 1

        self.policy_report['policy_outbounds'] = {
            'allowed': list(allowed_outbound_candidates),
            'avoided': list(avoid_outbound_candidates),
            'denied': list(denied_outbound_candidates),
            'policy_result': result
        }

        project = report['project']
        project_definition = project['project_definition']

        self.policy_report['project'] = {
            'project_file': project['project_file'],
            'name': project_definition['name'],
            'license': project_definition['license'],
            'version': project_definition['version'] if 'version' in project_definition else ""
        }

        return self.policy_report

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
