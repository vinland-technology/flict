###################################################################
#
# SPDX-FileCopyrightText: 2021 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later
#
###################################################################

import logging

logging.basicConfig(level=logging.DEBUG)

main_logger = logging.getLogger('flict')
    
license_logger = logging.getLogger("flict.license")


def setup(debug_license, verbose):
    if debug_license and verbose:
        license_logger.setLevel(logging.DEBUG)
    elif debug_license:
        license_logger.setLevel(logging.INFO)
    else:
        license_logger.setLevel(logging.WARN)

    if verbose:
        main_logger.setLevel(logging.DEBUG)
    else: 
        main_logger.setLevel(logging.WARNING)
