#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2022 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later

import logging

from enum import Enum
import osadl_matrix

from flict.flictlib.return_codes import FlictError, ReturnCodes
from flict.flictlib.alias import Alias


class CompatibilityStatus(Enum):
    LICENSE_COMPATIBILITY_COMPATIBLE = "Yes"
    LICENSE_COMPATIBILITY_INCOMPATIBLE = "No"
    LICENSE_COMPATIBILITY_UNKNOWN = "Unknown"
    LICENSE_COMPATIBILITY_MANUALLY_CHECK = "Check dependencies manually"
    LICENSE_COMPATIBILITY_UNDEFINED = "Undefined"


LICENSE_COMPATIBILITY_AND = "AND"
LICENSE_COMPATIBILITY_OR = "OR"
COMPATIBILITY_TAG = "compatibility"


class CompatibilityFactory:
    """Class to provide Compatibility objects via get_compatibility
    """

    @staticmethod
    def get_compatibility(alias=None, license_db=None):
        """Returns a Compatibility object.

            Parameters:
                alias: alias object
                licensedb: licensedb to use if not using default

        Currently only OsadlCompatibility is available.
        """
        return OsadlCompatibility(alias or Alias(), license_db)


class Compatibility:
    """Class to determine compatibility between licenses.

    This class need to be implemented in sub classes.
    """
    def __init__(self, alias, license_db=None):
        return None

    def check_compat(self, outbound, inbound):
        return None

    def supported_licenses(self):
        return None

    def display_compatibility(self):
        try:
            # build up license string from all expressions
            lic_str = " ".join(self._args.license_expression)

            # encode (flict) all the license expression
            lic_str = self._encode_license_expression(lic_str)

            # build up license string from the expression string
            _licenses = set()
            for lic in lic_str.split():

                lic_list = lic.replace("(", "").replace(
                    ")", "").replace(" ", "").replace("OR", " ").replace("AND", " ").strip().split(" ")

                for lic in lic_list:
                    if lic != "":
                        _licenses.add(self._decode_license_expression(lic))

            licenses = list(_licenses)

            inter_compats = self.check_compatibilities(licenses, self._args.extended_licenses)
        except:
            raise FlictError(ReturnCodes.RET_INVALID_EXPRESSSION,
                             f'Could not parse license expression: {self._args.license_expression}')

        return inter_compats

    def _encode_license_expression(self, license_expression):
        return license_expression.replace(" WITH ", "_WITH_")

    def _decode_license_expression(self, license_expression):
        return license_expression.replace("_WITH_", " WITH ")

    def check_compatibilities(self, licenses, check_all=False):
        """Check compatbilitiy between supplied licenses"""
        compats = []

        if check_all:
            supported = self.supported_licenses()
            if 'Compatibility' in supported:
                supported.remove('Compatibility')

            licenses_set = set(licenses + supported)
            outer_licenses = list(licenses_set)
        else:
            outer_licenses = list(licenses)

        for lic_a in outer_licenses:
            inner_licenses = []
            for lic_b in licenses:

                comp_left = self.check_compat(lic_a, lic_b)['compatibility']
                comp_right = self.check_compat(lic_b, lic_a)['compatibility']

                if comp_left == CompatibilityStatus.LICENSE_COMPATIBILITY_UNKNOWN.value or comp_right == CompatibilityStatus.LICENSE_COMPATIBILITY_UNKNOWN.value:
                    raise FlictError(ReturnCodes.RET_INVALID_EXPRESSSION,
                                     f'One of the license expressions "{lic_a}" and "{lic_b}" is not supported.')

                inner_licenses.append({
                    'license': lic_b,
                    'compatible_right': self._compatibility_status_json(comp_right),
                    'compatible_left': self._compatibility_status_json(comp_left)
                })

            compats.append({
                'license': lic_a,
                'licenses': inner_licenses
            })

        return {
            'compatibilities': compats
        }

    def _compatibility_status_json(self, status):
        if status == "Yes":
            return "true"
        elif status == "No":
            return "false"
        elif status == "Undefined":
            return "undefined"
        elif status == "Check dependencies manually":
            return "depends"
        elif status == "Unknown":
            return "question"

    def extend_license_db(self, file_name):
        return None


class OsadlCompatibility(Compatibility):
    """Class to determine compatibility between licenses using OSADL's matrix

    This class implements Compatibility
    """

    def __init__(self, alias, license_db=None):
        self.license_db = license_db
        self.alias = alias

    def check_compat(self, _outbound, _inbound):

        #print(f"check_compat({_outbound}, {_inbound})")
        outbound = self.alias.replace_aliases(_outbound)
        inbound = self.alias.replace_aliases(_inbound)
        #print(f"check_compat({outbound}, {inbound})")
        raw_result = osadl_matrix.get_compatibility(outbound, inbound, self.license_db)

        logging.info(f"check_compat({outbound}, {inbound} => {raw_result}")

        #import sys
        #print("raw_result: " + str(raw_result))
        if raw_result == osadl_matrix.OSADLCompatibility.YES:
            result = CompatibilityStatus.LICENSE_COMPATIBILITY_COMPATIBLE.value
        elif raw_result == osadl_matrix.OSADLCompatibility.NO:
            result = CompatibilityStatus.LICENSE_COMPATIBILITY_INCOMPATIBLE.value
        elif raw_result == osadl_matrix.OSADLCompatibility.UNKNOWN:
            result = CompatibilityStatus.LICENSE_COMPATIBILITY_UNKNOWN.value
            logging.debug(f"compatibility: {outbound}  --> {inbound}: {result}")
        elif raw_result == osadl_matrix.OSADLCompatibility.CHECKDEP:
            result = CompatibilityStatus.LICENSE_COMPATIBILITY_MANUALLY_CHECK.value
            logging.debug(f"compatibility: {outbound}  --> {inbound}: {result}")
        elif raw_result == osadl_matrix.OSADLCompatibility.UNDEF:
            result = CompatibilityStatus.LICENSE_COMPATIBILITY_UNKNOWN.value

            #raise FlictError(ReturnCodes.RET_INVALID_EXPRESSSION, f"Compatibility between \"{outbound}\" and \"{inbound}\" could not be determined since (at least) one of the licenses are not supported.")

        else:
            raise FlictError(ReturnCodes.RET_INVALID_EXPRESSSION, f"Compatibility between \"{outbound}\" and \"{inbound}\" could not be determined. The result was: {result}")

        return {
            "inbound": inbound,
            "outbound": outbound,
            COMPATIBILITY_TAG: result
        }

    def supported_licenses(self):
        """Returns a list of supported licenses"""
        return list(osadl_matrix.supported_licenses(self.license_db))

    def _create_matrix(self, raw):
        """
        Copied from https://github.com/priv-kweihmann/osadl-matrix/blob/master/scripts/scrapper.py
        Modified by Henrik Sandklef
        # SPDX-FileCopyrightText: 2021 Konrad Weihmann
        # SPDX-FileCopyrightText: 2022 Henrik Sandklef
        # SPDX-License-Identifier: Unlicensed
        """
        # create a csv

        _csv = [
            ['Compatibility*'] + sorted(raw.keys())
        ]

        for key in sorted(raw.keys()):
            _line = [key]
            for key2 in sorted(raw.keys()):
                _line.append(raw[key][key2])
            _csv.append(_line)

        for line in _csv:
            if len(line) < 3:
                continue
            #print(line)
        return _csv

    def _create_matrix_csv_data(self, file_name):
        import json
        # read file with additional license data
        with open(file_name) as fp:
            additional_data = json.load(fp)['osadl_additional_licenses']

        # read osadl matrix data
        import osadl_matrix
        with open(osadl_matrix.OSADL_MATRIX_JSON) as fp:
            osadl_data = json.load(fp)

        # merge osadl and our data
        for key, value in additional_data.items():
            if key in osadl_data:
                osadl_data[key].update(value)
            else:
                osadl_data[key] = value

        new_matrix_data = self._create_matrix(osadl_data)
        rows = []
        for row in new_matrix_data:
            rows.append(",".join(row))
        return "\n".join(rows)

    def extend_license_db(self, file_name):
        """Extends the current license db with licese db provided in file_name.

        Parameters:
            file_name - file (str) with license db (JSON)

        See SETTINGS.md for more information about format and
        requirements for a custom database.
        """
        return self._create_matrix_csv_data(file_name)


class LicenseChoser:
    """Interface for classes to choose from inbound licenses (where a
    choice is offered via OR).

    """

    def __init__(self, licenses):
        """Parameters:
               licenses - the licenses to create a chose object for
        """
        self.licenses = licenses

    def chose(self, licenses):
        """Chose the most preferred license

        Parameters:
            licenses - list of licenses to chose the most preferred from
        """
        index = None
        for lic in licenses:
            lic_index = self.licenses.index(lic)
            if index is None or lic_index < index:
                index = lic_index

        if index is None:
            return None
        else:
            return self.licenses[index]

    def list(self):
        """returns a list of licenses in preference order"""
        return self.licenses


class CustomLicenseChoser(LicenseChoser):
    """This class provides a custom way to choose from inbound licenses
    (where a choice is offered via OR). By providing a list of licenses in order of preference, this list is used"""
    pass


class CompatibilityLicenseChoser(LicenseChoser):
    """This class provides a simple way to choose from inbound licenses
    (where a choice is offered via OR).

    It counts how many other licenses each license is compatible
    with. The more licenses a license is compatible with the more
    preferred it will be. If two licenses have the same number of
    compaitbilities alpabetical order will be used to chose license.
    """

    def __init__(self, licenses):
        """Parameters:
               licenses - the licenses to create a choser object for
        """
        self.licenses = self._license_preferences(licenses)

    def _count_compat(self, inbound, supported_licenses):
        compat_cnt = 0
        for outbound in supported_licenses:
            if osadl_matrix.is_compatible(outbound, inbound):
                compat_cnt += 1
        return {
            "inbound": inbound,
            "compatible_count": compat_cnt
        }

    def _count_compats(self, supported_licenses):
        compats = []
        for inbound in supported_licenses:
            compats.append(self._count_compat(inbound, supported_licenses))
        compats_sorted = sorted(compats, key = lambda element: (element['compatible_count'], element['inbound']))
        compats_sorted.reverse()
        return compats_sorted

    def _license_preferences(self, supported_licenses):
        compats_sorted = self._count_compats(supported_licenses)
        pref_list = []
        for lic in compats_sorted:
            pref_list.append(lic['inbound'])

        return pref_list
