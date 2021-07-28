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

#
# File and class to keep information and behavious related to a project
#

import json
from flict.flictlib import logger

DEFAULT_MATRIX_FILE = "osadl-matrix.csv"


class Project:
    """Project class

    Member variables:
    * project - defintion of the project
    * dep_list - the project's dependencies
    * expanded - whether it has been expanded (see below) or not
    * license_handler - the license handler object for use below
    * tot_combinations - when the project has been expanded, this variable contains the number of combinations this project has (can be turned into)

    """

    def __init__(self, project_file, license_handler, license_expression=None):
        if license_expression is None:
            """
            Reads a project definition from a JSON file.
            expands the licenses (see below)

            """
            self.expanded = False
            self.dep_list = None
            self.project_file = project_file
            self.read_project_file()
            self.license_handler = license_handler
            self._expand_licenses()
            self.tot_combinations = None
            # self.expand_projects()
        else:
            """Creates a project definition, with no dependencies, from a license
            expression.

            expands the licenses (see below)

            """
            self.expanded = False
            self.dep_list = None
            self.project_file = None
            project = {}
            project['name'] = "dummy"
            project['version'] = "0.0.0"
            project['license'] = license_expression
            project['dependencies'] = []
            self.project = project
            self.license_handler = license_handler
            self._expand_licenses()
            self.tot_combinations = None
            # self.expand_projects()

    def read_project_file(self):
        """This function reads a project file (JSON)

        using either the new
        format ("project") or the old one ("component"), stored in self.project
        If there is a meta section in the project def, this is added under self.meta
        """
        with open(self.project_file) as fp:
            self.project_object = json.load(fp)
            if 'project' in self.project_object:
                self.project = self.project_object['project']
            elif 'component' in self.project_object:
                self.project = self.project_object['component']
            else:
                return None
            if 'meta' in self.project_object:
                self.meta = self.project_object['meta']

    # Some nifty methods to hide the storage structure

    def name(self):
        return self.project['name']

    def license(self):
        return self.project['license']

    def version(self):
        return self.project['version']

    def dependencies(self):
        return self.project['dependencies']

    def _dependency_list(self, dep):
        """internal function

        returns the list of dependencies (as the name suggests)
        """
        dep_list = []
        #logger.main_logger.debug(" * adding: " + dep['name'])
        me = {}
        #print("dep: " +str(dep))
        me['name'] = dep['name']
        me['license'] = dep['license']
        if 'version' in dep:
            me['version'] = dep['version']
        else:
            me['version'] = ""
        me['dependencies'] = []
        dep_list.append(me)
        #print("me: " + json.dumps(me))
        if 'dependencies' in dep:
            for d in dep['dependencies']:
                dep_list = dep_list + self._dependency_list(d)
                #logger.main_logger.debug(" * dep list: " + str(dep_list))
        return dep_list

    def dependencies_pile_map(self):
        """Returns the pile ("flattened tree")

        of a project's dependencies as a map
        """
        dep_pile = self.dependencies_pile()
        dep_pile_json = []
        for d in dep_pile:
            dep_json = d
            dep_json['expanded_license'] = d['expanded_license']
            dep_pile_json.append(dep_json)

        return dep_pile_json

    def dependencies_pile(self):
        """Returns the pile ("flattened tree")

        of a project's dependencies as a list

        """
        if self.dep_list is None:
            self.dep_list = self._dependency_list(self.project)
        return self.dep_list

    def license_set(self):
        """Returns a set of the licenses

        (implied by set is that this is a uniqe collection of the project's licenses (including its dependencies)
        """
        licenses = set()
        dep_pile = self.dependencies_pile()
        for d in dep_pile:
            #print("\n\ndep_licenses_map:\n" + json.dumps(d))

            dep_licenses = d['expanded_license']

            for license_list in dep_licenses['set_list']:
                #print("license_list: " + str(license_list))
                for _license in license_list:
                    #print("license: " + str(_license))
                    license = _license.replace("(", "").replace(")", "")
                    if license == "AND" or license == "and" or license == "OR" or license == "or":
                        pass
                    elif license == "":
                        pass
                    else:
                        #print("add: " + license)
                        licenses.add(license)
        return licenses

    def license_piled_license_check(self):
        """returns a list of the licenses

        of the project's dependencies OR together.
        This expression is simplified (with regards to boolean algebra).
        """
        license_handler = self.license_handler
        # print("new_license_set...")
        combined_license = ""
        for proj in self.dependencies_pile():
            simplified = proj['expanded_license']['simplified']
            if combined_license == "":
                combined_license = " ( " + simplified + " ) "
            else:
                combined_license = combined_license + \
                    " and ( " + simplified + " ) "
            #print("adding: " + proj['name'])
        #print("new_license_set(): " + str(combined_license))
        simplified = license_handler.simplify(combined_license)
        #print("new_license_set(): " + str(simplified))
        return simplified

    def project_combinations(self, license_handler, dep):
        """returns the number of combinations

        (number of licenses in list_set) for the dependency given as argument
        (ignoring the dependencies of this dependency).

        """
        #proj_license = dep['license']
        managed_expression = dep['expanded_license']
        set_list = managed_expression['set_list']

        #print("managed_expression:  " + str(set_list))
        return len(set_list)

    # internal only
    def _project_combinations(self, dep):
        """returns the number of combinations

        (number of licenses in list_set) for the dependency given as argument
        (ignoring the dependencies of this dependency).
        """
        return self.project_combinations(self.license_handler, dep)

    def projects_combinations(self):
        """returns the number of combinations

        (number of licenses in list_set) for this projects and its dependencies.
        """
        dep_pile = self.dependencies_pile()
        tot_combinations = 1
        for proj in dep_pile:
            tot_combinations = tot_combinations * \
                self._project_combinations(proj)
        self.tot_combinations = tot_combinations
        return tot_combinations

    def __str__(self):
        return self.name()

    def _expand_licenses(self):
        """For each of the project's dependencies

        this function adds a list of license expressions (from license_expression_list)
        to the project.

        This function is reponsible for expanding the licenses of a
        project. See license_expression_list() in license_handler for more information
        how this is done.

        """
        dep_pile = self.dependencies_pile()
        for proj in dep_pile:
            #print(" --- : " + str(proj))
            exp_lic = self.license_handler.license_expression_list(
                proj['license'], True)
            proj['expanded_license'] = exp_lic.to_json()
            #print("ADDING: " + str(proj['expanded_license'].set_list) + " type: " + str(type(exp_lic)))

        logger.main_logger.debug("piles: " + str(dep_pile))

        #combinations = self.projects_combinations(self.license_handler, dep_pile, True)
        #logger.main_logger.debug("combinations: " +str(combinations))
        # return combinations

    def expand_projects(self):
        """
        Expand projects

        From a project pile like this:
        [
          A:[ {a1}, {a2} ]
          B:[ {b1}, {b2} ]
        ]
        which has (2*2=4) 4 combinations
        this functions expands the above to:
        [
          A:
            [ {a1} ],
            [ {a1} ],
            [ {a2} ],
            [ {a2} ]
        ],
        [
          B
            [ {b1} ],
            [ {b2} ],
            [ {b1} ],
            [ {b2} ]
        ]
        So the first index is for the project and the second is for the license

        This will in turn be made in to:

        [
           [ { "project": A, "license": a1 }
             { "project": B, "license": b1 }
           ],
           [ { "project": A, "license": a1 }
             { "project": B, "license": b2 }
           ],
           [ { "project": A, "license": a2 }
             { "project": B, "license": b1 }
           ],
           [ { "project": A, "license": a2 }
             { "project": B, "license": b2 }
           ]
        ]
        """
        if self.expanded:
            return

        dep_pile = self.dependencies_pile()
        combinations = self.projects_combinations()
        expanded_projects = []

        left = combinations
        for proj in dep_pile:
            expanded_project = []
            for i in range(combinations):
                nr_licenses = len(proj['expanded_license']['set_list'])
                divisor = left // nr_licenses
                index = (i // divisor) % nr_licenses

                license = proj['expanded_license']['set_list'][index]
                name = proj['name']
                version = proj['version']
                exp_project = ExpandedProject(name, license, version)
                expanded_project.append(exp_project)
                #print("adding: " + str(exp_project))
                #print("   to:  " + str(expanded_project))
            # print("")
            expanded_projects.append(expanded_project)
            # update for next round
            left = left // nr_licenses

        # print(self._expanded_projects_string(expanded_projects))

        #
        # Second phase, create map
        #
        self._project_combination_list = []
        for i in range(combinations):
            project_combination = []
            for j in range(len(expanded_projects)):
                project = {}
                project['name'] = expanded_projects[j][i].name
                project['license'] = expanded_projects[j][i].license
                # project['license']=list(expanded_projects[j][i].license)
                project['version'] = expanded_projects[j][i].version
                project_combination.append(project)
            self._project_combination_list.append(project_combination)
        # print(self.project_combination_list)
        self.expanded = True

    def project_combination_list(self):
        if not self.expanded:
            self.expand_projects()
        return self._project_combination_list


class ExpandedProject:
    def __init__(self, name, license, version):
        self.name = name
        self.license = license
        self.version = version

    def __str__(self):
        return self.name + " (" + str(self.license) + ")"


