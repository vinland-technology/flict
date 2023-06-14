# SPDX-FileCopyrightText: 2022 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later

import logging

from flict.flictlib.lic_comp import LicenseCompatibilty
from flict.flictlib.project.reader import Project
from flict.flictlib.utils import meta_information
from flict.flictlib.utils import timestamp
from flict.flictlib.return_codes import FlictError, ReturnCodes


class Arbiter:
    """Arbiter is a class to verify compatibility"""

    def __init__(self, license_db=None, licenses_preferences=None, denied_licenses=None, alias_file=None):
        """Initializes Arbiter objects
             Parameters:
                 license_db: license database to use instead of builtin
                 licenses_preferences: license preferences to use instead of builtin
                 denied_licenses: licenses that cannot be used
        """
        self.license_compatibility = LicenseCompatibilty(
            license_db=license_db, licenses_preferences=licenses_preferences, denied_licenses=denied_licenses, alias_file=alias_file)

    def supported_licenses(self):
        """Returns the supported licenses"""
        return self.license_compatibility.supported_licenses()

    def verify_package(self, package, licenses):
        """Verifies a package's license to a list of outbounds and returns the
        compatibility between the liceses.
             Parameters:
                 package: the package (with its license) to check for compatibility
                 licenses: the licenses to check the package's license against
        """
        logging.debug(f"* verify package {package['name']} (\"{package['license']}\"")

        logging.debug(f"   * All licenses: {licenses}")
        inbound_license = package['license']
        logging.debug(f"   * Inbound license:  {inbound_license}")

        return [self.inbounds_outbound_check(outbound_license, [inbound_license]) for outbound_license in licenses]

    def _package_info_compatibility(self, package_info, outbound):
        for compat in package_info['compatibility']:
            logging.debug(f"            *** outbound: \"{compat['outbound']}\"  <--->  \"{compat}\"")

            if compat['outbound']['name'] == outbound:
                logging.debug("         *** found outbound in compats")

                allowed = compat['allowed']
                compatibility = compat['compatibility']
                compatible = compatibility == "Yes"
                name = compat['name']
                logging.debug(f"         *** type:          {type}")
                logging.debug(f"         *** allowed:       {allowed}")
                logging.debug(f"         *** compatibility: {compatibility}")
                logging.debug(f"         *** compatible:    {compatible}")
                logging.debug(f"         *** name:          {name}")

                return (compatible, compat['name'])

        return (False, None)

    def _combined_work_compatible_dependencies(self, outbound_license, dep_infos):
        compatible = True
        for dep_info in dep_infos:
            # Get the corresponding compatiblity for outbound_license for dep_info
            compatible_license = self._package_info_compatibility(dep_info, outbound_license)
            dep_compatible = compatible_license[0]
            compatible = compatible and dep_compatible
            logging.debug("        {dep_info['name']}: {dep_compatible} ===> {compatible}")
        return compatible

    def _combined_work_compatible(self, outbound_license, package_info, dep_infos):
        compatible_license = self._package_info_compatibility(package_info, outbound_license)
        if not compatible_license:
            raise FlictError(ReturnCodes.RET_INTERNAL_ERROR,
                             f"Found license incompatibility for \"{package_info}\", \"{outbound_license}\"")
        else:
            compatible = compatible_license[0]

        # AND together compatible status from dependencies
        compatible = compatible and self._combined_work_compatible_dependencies(outbound_license, dep_infos)

        logging.debug(f"    --> combined work compatible: {compatible}\n")
        return compatible

    def _top_package_license(self, all_licenses, package_info, dep_infos):
        outbound_licenses = set()
        logging.debug("TOP LEVEL OUTBOUND")
        #
        # Start with checking top package's license as outbound
        #
        compatible = self._combined_work_compatible(package_info['license'], package_info, dep_infos)
        if compatible:
            outbound_licenses.add(package_info['license'])

        #
        # Let's loop through all the other licenses in the combined work
        #
        for lic in all_licenses:
            compatible = self._combined_work_compatible(lic, package_info, dep_infos)
            if compatible:
                outbound_licenses.add(lic)

        return list(outbound_licenses)

    def _package_info(self, package, licenses):
        compats = self.verify_package(package, licenses)

        return {
            'name': package['name'],
            'license': package['license'],
            'licenses_to_check': list(licenses),
            'version': package['version'],
            'description': package.get('description', ""),
            'compatibility': compats,
        }

    def verify(self, project, supplied_licenses=None):
        """Verifies a project's license to a list of outbounds and returns the
        compatibility between the liceses.
             Parameters:
                 project: the project (with its packages and their licenses) to check for compatibility
                 supplied_licenses: the licenses to check the package's license against
        """

        start_time = timestamp()

        project_name = project['project_name']

        package_infos = []
        all_licenses = set()

        for package in project['packages']:
            license_expression = Project.combined_work_license(package)

            if supplied_licenses is None:
                licenses = self.license_compatibility.licenses(license_expression)
            else:
                licenses = supplied_licenses

            all_licenses.update(licenses)

            package_info = self._package_info(package, licenses)

            dep_infos = [self._package_info(dep, licenses) for dep in package.get('dependencies', [])]

            # Get a list of the outbound licenses for all packages
            outbound_licenses = self._top_package_license(licenses, package_info, dep_infos)

            # Get the alias for all outbound licenses
            outbound_licenses_aliased = [self.license_compatibility.replace_aliases(lic) for lic in outbound_licenses]

            # Identify single outbound (chosen) license (from the aliased outbound licenses)
            chosen_alias = self.license_compatibility.choose_license(outbound_licenses_aliased)
            if chosen_alias is None:
                chosen_license = None
            else:
                # Find the index of the aliased license
                # and use that to identify the original (not aliased) license
                index = outbound_licenses_aliased.index(chosen_alias)
                chosen_license = outbound_licenses[index]

            package_info.update({
                'dependencies': dep_infos,
                'outbound_licenses': outbound_licenses,
                'outbound_licenses_aliased': outbound_licenses_aliased,
                'outbound_license': chosen_license,
                'outbound_license_aliased': chosen_alias,
            })
            package_infos.append(package_info)

        return {
            "project_name": project_name,
            "packages": package_infos,
            "meta": meta_information(start_time),
            "all_licenses": list(all_licenses),
        }

    def _compat_ok_to_use(self, compat):
        """
        Checks if a compatibility is OK to use by checking if
        * the license is compatible
        * the license is not denied
        """
        return compat['compatibility'] == "Yes" and compat['allowed']

    def inbounds_outbound_check(self, outbound, expr):
        """Check an outbound license against inbound licenses
             Parameters:
                 outbound: the outbound license (e.g. "GPL-2.0-only")
                 expr: license expr with inbound license (e.g. "MPL-2.0 OR MIT")
        """
        return self.license_compatibility.inbounds_outbound_compatibility(outbound, expr)

    def inbound_outbound_check(self, outbound, inbound):
        """Check an outbound license against an inbound license
             Parameters:
                 outbound: the outbound license (e.g. "GPL-2.0-only")
                 ibound: inbound license (e.g. "MPL-2.0")
        """
        return self.license_compatibility.inbound_outbound_compatibility(outbound, inbound)

    def check_compatibilities(self, licenses, check_all=False):
        """Check compatbilitiy between supplied licenses"""
        return self.license_compatibility.check_compatibilities(licenses, check_all)

    def extend_license_db(self, file_name, oformat="JSON"):
        return self.license_compatibility.extend_license_db(file_name, oformat)

    def simplify_license(self, expr):
        return self.license_compatibility.simplify_license(expr)

    def parse_license(self, expr):
        return self.license_compatibility.parse_license(expr)

    def licenses(self, expr):
        return self.license_compatibility.licenses(expr)
