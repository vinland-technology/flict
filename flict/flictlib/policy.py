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

from flict.flictlib.logger import main_logger as logger
from flict.flictlib.return_codes import FlictError, ReturnCodes


def timestamp():
    return str(datetime.datetime.now())


class Policy:
    def __init__(self, policy_file):
        self.policy_report = {}
        self.policy_report['meta'] = self.meta()
        self.policy_report['policy_file'] = policy_file
        try:
            with open(policy_file) as file_:
                self.policy_report['policy'] = json.load(file_)
        except json.decoder.JSONDecodeError:
            error = "Internal error, policy file has improper JSON format"
            raise FlictError(ReturnCodes.RET_INTERNAL_ERROR, error)

    def sanity(self, json_obj, requirements):
        logger.debug(f"Checking sanity of report {json_obj}")

        def exists(json_, chain):
            key = chain.pop(0) # this empties list, hence reqscopy as list.copy()
            if key in json_:
                return exists(json_[key], chain) if chain else key
            return None

        expected = [req[-1] for req in requirements]
        reqscopy = [[it for it in line] for line in requirements] # noqa: C416
        checked = [exists(json_obj, req) for req in requirements]
        on_failure = "Improper file format, missing key: '{expected}' in {path}"
        fail = False
        for i, _ in enumerate(expected):
            expected_it, pathway = expected[i], " -> ".join(reqscopy[i])
            error = on_failure.format(expected=expected_it, path=pathway)
            try:
                if checked[i] != expected[i]:
                    logger.error(error)
                    fail = True
            except IndexError:
                logger.error(error)
                fail = True
        if fail:
            on_error = "Internal error, file is missing required keys"
            raise FlictError(ReturnCodes.RET_INTERNAL_ERROR, on_error)

    def report(self, report):
        if not self.policy_report['policy']:
            return None

        requirements = [["project", "project_definition", "license"],
                        ["project", "project_definition", "name"],
                        ["project", "project_file"],
                        ["licensing", "outbound_candidates"]]
        self.sanity(report, requirements)

        policy = self.policy_report['policy'].get('policy', {})

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
