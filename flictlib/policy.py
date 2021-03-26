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

import json
import os
import sys
import re
from argparse import RawTextHelpFormatter
import argparse
import getpass
import datetime



VERBOSE=False

def error(msg):
    sys.stderr.write(msg + "\n")

def verbose(msg):
    global VERBOSE
    if VERBOSE:
        sys.stderr.write(msg)
        sys.stderr.write("\n")
        sys.stderr.flush()

def verbosen(msg):
    global VERBOSE
    if VERBOSE:
        sys.stderr.write(msg)
        sys.stderr.flush()

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
        if self.policy_report['policy'] == None:
            return None
        
        outbounds = report['licensing']['outbound_suggestions']
        allowed = self.policy_report['policy']['policy']['allowlist']
        avoid = self.policy_report['policy']['policy']['avoidlist']
        denied = self.policy_report['policy']['policy']['denylist']

        
        
        #nr_outbounds = len(outbounds)
        
        allowed_outbound_suggestions = set()
        avoid_outbound_suggestions =  set()
        denied_outbound_suggestions =  set()

        for out_lic in outbounds:
            if out_lic in allowed:
                allowed_outbound_suggestions.add(out_lic)
            elif out_lic in avoid:
                avoid_outbound_suggestions.add(out_lic)
            elif out_lic in denied:
                denied_outbound_suggestions.add(out_lic)
            else:
                allowed_outbound_suggestions.add(out_lic)

        policy_outbounds = {}
        policy_outbounds['allowed'] = list(allowed_outbound_suggestions)
        policy_outbounds['avoid'] = list(avoid_outbound_suggestions)
        policy_outbounds['denied'] = list(denied_outbound_suggestions)

        if len(policy_outbounds['allowed']) > 0:
            policy_outbounds['policy_result'] = 0
        elif len(policy_outbounds['avoid']) > 0:
            policy_outbounds['policy_result'] = 1
        else:
            policy_outbounds['policy_result'] = 2
            
        
        self.policy_report['policy_outbounds'] = policy_outbounds

        project = report['project']
        project_info = {}
        project_info['project_file'] = project['project_file']

        #print(" project :     " + str(project))
        #print(" project def : " + str(project['project_definition']))

        project_definition=project['project_definition']
        project_info['name'] = project_definition['name']
        #project_info['top_project_license'] = project_definition['top_project_license']
        project_info['license'] = project_definition['license']
        if 'version' in project_definition:
            project_info['version'] = project_definition['version']
        else:
            project_info['version'] = ""

        self.policy_report['project'] = project_info

        
        return self.policy_report

    def meta(self):
        uname=os.uname()
        return {
            'os': uname.sysname,
            'osRelease': uname.release,
            'osVersion': uname.version,
            'machine': uname.machine,
            'host': uname.nodename,
            'user': getpass.getuser(),
            'start': timestamp()
        }
    
