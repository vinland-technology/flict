# SPDX-FileCopyrightText: 2022 Henrik Sandklef
# SPDX-FileCopyrightText: 2022 Jens Erdmann
#
# SPDX-License-Identifier: GPL-3.0-or-later

import json
import logging

from flict.flictlib.return_codes import FlictError, ReturnCodes
from flict.flictlib.license import compatible_license

DEPENDENCY_TAGS = ['DYNAMIC_LINK', 'STATIC_LINK', 'DEPENDS_ON', 'CONTAINS', 'COPY_OF']

class Project:

    def __init__(self, project_file, project_dirs):
        project_reader = ProjectReaderFactory.get_projectreader(project_file, project_dirs)
        self.project = project_reader.read_project()

    @staticmethod
    def dependencies_license(package):
        licenses = [f' ( {Project.package_license(dep)} ) ' for dep in package.get('dependencies', [])]
        return ' AND  '.join(licenses)

    @staticmethod
    def package_license(package):
        if 'license' not in package:
            raise FlictError(ReturnCodes.RET_INVALID_PROJECT, f'Package does not contain "license": {package}')
        return package['license']

    @staticmethod
    def combined_work_license(package):
        if Project.dependencies_license(package).strip() != '':
            return f' ( {Project.package_license(package)} ) AND ( {Project.dependencies_license(package)} ) '
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

    def prepare_project(self, project):
        for package in project.get('packages', []):
            self.__update_dep_license(package)
        return project

    def __update_dep_license(self, package):
        package['original_license'] = package.get('license')
        compat = compatible_license(package.get('license'), update_dual=self.update_dual)
        fixed_license = compat['compat_license']
        package['license'] = fixed_license

        for dep in package['dependencies']:
            self.__update_dep_license(dep)

    def _flatten_packages(self, packages):
        package_list = []

        for _package in packages:
            tmp_dict = {}
            for dep in _package.get('dependencies', []):
                tmp_dict.update(self._flatten_package_tree(dep))
            dep_list = tmp_dict.values()

            for dep in dep_list:
                dep['dependencies'] = []

            package = {
                'name': _package['name'],
                'version': _package['version'],
                'license': _package['license'],
                'description': _package['description'],
                'dependencies': list(dep_list),
            }

            package_list.append(package)

        return package_list


class ProjectReaderFactory:

    @staticmethod
    def get_projectreader(project_file=None, project_dirs=None, project_format=None, update_dual=True):
        if not project_dirs:
            project_dirs = ['.']
        logging.debug(f'get_projectreader({project_file}, {project_dirs}, {project_format}, {update_dual})')
        if project_format is None:
            if 'spdx' in project_file:
                return SPDXJsonProjectReader(project_dirs, update_dual)
            if 'flict' in project_file:
                return FlictProjectReader(project_dirs, update_dual)
        elif project_format == 'flict':
            return FlictProjectReader(project_dirs, update_dual)
        elif project_format == 'spdx':
            return SPDXJsonProjectReader(project_dirs, update_dual)


class FlictProjectReader(ProjectReader):
    """Class for reading flict project files"""

    def __init__(self, project_dirs, update_dual=True):
        self.update_dual = update_dual

    def __read_project_data(self, _project_data):
        project = _project_data['project']
        project_data = {
            'project_name': project['name'],
            'packages': [
                {
                    'name': project['name'],
                    'version': project['version'],
                    'license': project['license'],
                    'description': '',
                    'dependencies': project['dependencies'],
                },
            ],
        }
        fixed_project_data = self.prepare_project(project_data)
        return fixed_project_data

    def read_project_data(self, project_data):
        return self.__read_project_data(project_data)

    def read_project(self, project_file):
        try:
            with open(project_file, 'r') as f:
                project_data = json.load(f)
                return self.__read_project_data(project_data)
        except json.JSONDecodeError:
            raise FlictError(ReturnCodes.RET_INVALID_PROJECT, f'File "{project_file}" does not contain valid JSON data')
        except (FileNotFoundError, IsADirectoryError):
            raise FlictError(ReturnCodes.RET_FILE_NOT_FOUND, f'File "{project_file}" could not be found or is a directory')
        except Exception as e:
            raise FlictError(ReturnCodes.RET_INVALID_PROJECT,
                             f'File "{project_file}" could not be parsed, probably not a flict project file: {e}')


class SPDXJsonProjectReader(ProjectReader):
    """Class for reading SBoM files in SPDX 2.2
    If more SPDX versions need to be supported, we may need to subclass this in version specific classes....
    """

    def __init__(self, project_dirs, update_dual=True):
        self.spdx_dirs = project_dirs
        self.files_read = []
        self.update_dual = update_dual

    def read_project(self, project_file):
        packages_project_name = self._read_spdx(project_file)
        packages = packages_project_name['packages']
        project_name = packages_project_name['project_name']
        flat_packages = self._flatten_packages(packages)

        fixed_project_data = self.prepare_project({
            'project_name': project_name,
            'packages': flat_packages,
        })
        return fixed_project_data

    def _relationship_is_dependency(self, relationshiptype):
        return relationshiptype in DEPENDENCY_TAGS

    def _read_spdx_2_2(self, only_packages=None):
        project_name = self.project['name']
        packages = {}
        for pkg in self.project['packages']:
            elem_id = pkg['SPDXID']
            packages[elem_id] = {
                'id': elem_id,
                'name': pkg['name'],
                'version': pkg.get('versionInfo', ''),
                'license': pkg['licenseConcluded'],
                'description': pkg['description'],
                'dependencies': [],
            }

        for dep in self.project.get('relationships', []):
            top_package = dep['relatedSpdxElement']
            relationshiptype = dep['relationshipType']
            if not self._relationship_is_dependency(relationshiptype):
                logging.debug(f"relationship {dep.get('spdxElementId')} ignored since {relationshiptype} is not defined to be a dependency tag.")
                continue

            if 'DocumentRef' in dep['spdxElementId'] and ':' in dep['spdxElementId']:
                dep_package_doc = dep['spdxElementId'].split(':')[0]
                dep_package_name = dep['spdxElementId'].split(':')[1]
                dep_spdx = dep_package_doc.replace('DocumentRef-', '') + '.spdx.json'
                if self._already_read(dep_spdx):
                    continue
                self._add_files_read(dep_spdx)
                dep_spdx_path = self.spdx_dirs[0] + '/' + dep_spdx
                packages_proj_name = self._read_spdx(dep_spdx_path, self.spdx_dirs)
                _packages = packages_proj_name.get('packages')
                for _pkg in _packages:
                    _pkg_name = _pkg['id']
                    if dep_package_name == _pkg_name:
                        packages[top_package]['dependencies'].append({_pkg_name: _pkg})
            else:
                dep_id = dep['spdxElementId']
                for package in self.project['packages']:
                    if dep_id == package['SPDXID']:
                        if top_package not in packages:
                            logging.warning(f'package {top_package} marked as a relationship, but without corresponding package definition.')
                        else:
                            _pkg = {
                                'id': dep_id,
                                'name': pkg['name'],
                                'version': pkg.get('versionInfo', ''),
                                'license': pkg['licenseConcluded'],
                                'description': pkg['description'],
                                'dependencies': [],
                            }
                            packages[top_package]['dependencies'].append({dep_id: _pkg})

        packages_list = list(packages.values())

        ret = {
            'packages': packages_list,
            'project_name': project_name,
        }
        return ret

    def _read_spdx(self, spdx_file, only_packages=None):

        try:
            with open(spdx_file, 'r') as f:
                self.project = json.load(f)

        except json.JSONDecodeError:
            raise FlictError(
                ReturnCodes.RET_INVALID_PROJECT,
                f'File "{spdx_file}" does not contain valid JSON data',
            )

        spdx_version = self.project['spdxVersion'].replace('SPDX-', '')

        if spdx_version.startswith('2.2'):
            return self._read_spdx_2_2(only_packages=None)
        raise FlictError(ReturnCodes.RET_INTERNAL_ERROR,
                         f'SPDX version ({spdx_version}) not supported.')

    def _flatten_package_tree(self, packages):
        package_dict = {}

        for _package in packages.values():
            package_dict.update(
                {f"{_package['name']}--{_package['version']}": _package},
            )
            for dep in _package.get('dependencies', []):
                package_dict.update(self._flatten_package_tree(dep))

        return package_dict
