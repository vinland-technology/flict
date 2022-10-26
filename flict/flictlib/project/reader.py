# SPDX-FileCopyrightText: 2022 Henrik Sandklef
# SPDX-FileCopyrightText: 2022 Jens Erdmann
#
# SPDX-License-Identifier: GPL-3.0-or-later

import json
import logging

from flict.flictlib.return_codes import FlictError, ReturnCodes


class Project:

    def __init__(self, project_file, project_dirs):
        project_reader = ProjectReaderFactory.get_projectreader(project_file, project_dirs)
        self.project = project_reader.read_project()

    @staticmethod
    def dependencies_license(package):
        licenses = []
        for dep in package.get('dependencies', []):
            if 'license' not in dep:
                raise FlictError(ReturnCodes.RET_INVALID_PROJECT, f'Dependency does not contain "license": {dep}')
            licenses.append(f" ( {dep['license']}) ")
        return " AND ".join(licenses)

    @staticmethod
    def package_license(package):
        if 'license' not in package:
            raise FlictError(ReturnCodes.RET_INVALID_PROJECT, f'Package does not contain "license": {package}')
        return package['license']

    @staticmethod
    def combined_work_license(package):
        if Project.dependencies_license(package).strip() != "":
            return f" ( {Project.package_license(package)} ) AND ( {Project.dependencies_license(package)} ) "
        else:
            return Project.package_license(package)


class ProjectReader:
    """Interface for classes that reads project from some kind of format"""
    def read_project(self):
        return

    def _add_files_read(self, project_file):
        self.files_read.append(project_file)

    def _already_read(self, project_file):
        return project_file in self.files_read

    def _flatten_packages(self, packages):
        package_list = []

        for _package in packages.values():
            tmp_dict = {}

            for dep in _package['dependencies']:
                tmp_dict.update(self._flatten_package_tree(dep))

            dep_list = tmp_dict.values()

            package = {
                'name': _package['name'],
                'version': _package['version'],
                'license': _package['license'],
                'description': _package['description'],
                'dependencies': dep_list
            }

            package_list.append(package)
        return(package_list)


class ProjectReaderFactory:

    @staticmethod
    def get_projectreader(project_file=None, project_dirs = None, project_format=None):
        if not project_dirs:
            project_dirs = ["."]
        logging.debug(f'get_projectreader({project_file}, {project_dirs}, {project_format})')
        if project_format is None:
            if "spdx" in project_file:
                return SPDXJsonProjectReader(project_dirs)
            if "flict" in project_file:
                return FlictProjectReader(project_dirs)
        elif project_format == "flict":
            return FlictProjectReader(project_dirs)
        elif project_format == "spdx":
            return SPDXJsonProjectReader(project_dirs)


class FlictProjectReader(ProjectReader):
    """Class for reading flict project files"""

    def __init__(self, project_dirs):
        pass

    def read_project(self, project_file):
        try:
            with open(project_file, 'r') as f:
                project_data = json.load(f)
                project = project_data['project']

                return {
                    "project_name": project['name'],
                    "packages": [
                        {
                            'name': project['name'],
                            'version': project['version'],
                            'license': project['license'],
                            'description': '',
                            'dependencies': project['dependencies']
                        }
                    ]
                }
        except json.JSONDecodeError:
            raise FlictError(ReturnCodes.RET_INVALID_PROJECT, f'File "{project_file}" does not contain valid JSON data')
        except (FileNotFoundError, IsADirectoryError):
            raise FlictError(ReturnCodes.RET_FILE_NOT_FOUND, f'File "{project_file}" could not be found or is a directory')
        except Exception as e:
            raise FlictError(ReturnCodes.RET_INVALID_PROJECT, f'File "{project_file}" could not be parsed, probably not a flict project file: {e}')


class SPDXJsonProjectReader(ProjectReader):
    """Class for reading SBoM files in SPDX 2.2
    If more SPDX versions need to be supported, we may need to subclass this in version specific classes....
    """

    def __init__(self, project_dirs):
        self.spdx_dirs = project_dirs
        self.files_read = []

    def read_project(self, project_file):
        packages_project_name = self._read_spdx(project_file)
        packages = packages_project_name['packages']
        project_name = packages_project_name['project_name']
        flat_packages = self._flatten_packages(packages)

        return {
            "project_name": project_name,
            "packages": flat_packages
        }

    def _read_spdx_2_2(self, only_packages=None):
        project_name = self.project['name']
        packages = {}
        for pkg in self.project['packages']:
            elem_id = pkg['SPDXID']
            packages[elem_id] = {
                'id': elem_id,
                'name': pkg['name'],
                'version': pkg['versionInfo'],
                'license': pkg['licenseConcluded'],
                'description': pkg['description'],
                'dependencies': []
            }

        if 'relationships' in self.project:
            for dep in self.project['relationships']:
                top_package = dep['relatedSpdxElement']
                dep_package_doc = dep['spdxElementId'].split(":")[0]
                dep_package_name = dep['spdxElementId'].split(":")[1]
                dep_spdx = dep_package_doc.replace("DocumentRef-", "") + ".spdx.json"
                if self._already_read(dep_spdx):
                    continue
                self._add_files_read(dep_spdx)
                dep_spdx_path = self.spdx_dirs[0] + "/" + dep_spdx
                packages_proj_name = self._read_spdx(dep_spdx_path, self.spdx_dirs)
                _packages = packages_proj_name.get('packages')
                for _pkg in _packages.values():
                    _pkg_name = _pkg['id']
                    if dep_package_name == _pkg_name:
                        packages[top_package]['dependencies'].append({_pkg_name: _pkg})

        return {
            "packages": packages,
            "project_name": project_name
        }

    def _read_spdx(self, spdx_file, only_packages=None):

        try:
            with open(spdx_file, 'r') as f:
                self.project = json.load(f)

        except json.JSONDecodeError:
            raise FlictError(
                ReturnCodes.RET_INVALID_PROJECT,
                f'File "{spdx_file}" does not contain valid JSON data',
            )

        spdx_version = self.project['spdxVersion'].replace("SPDX-", "")

        if spdx_version.startswith("2.2"):
            return self._read_spdx_2_2(only_packages=None)
        raise FlictError(ReturnCodes.RET_INTERNAL_ERROR,
                         f"SPDX version ({spdx_version}) not supported.")

    def _flatten_package_tree(self, packages):
        package_dict = {}

        for _package in packages.values():
            package_dict.update(
                {f"{_package['name']}--{_package['version']}": _package}
            )
            for dep in _package["dependencies"]:
                package_dict.update(self._flatten_package_tree(dep))

        return package_dict
