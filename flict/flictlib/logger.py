###################################################################
#
# SPDX-FileCopyrightText: 2021 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later
#
###################################################################

import logging

main_logger = logging.getLogger('flict')
license_logger = logging.getLogger("flict.license")

def setup(args):
    if args.debug_license and args.verbose:
        license_logger.setLevel(logging.DEBUG)
    elif args.debug_license:
        license_logger.setLevel(logging.INFO)
    else:
        license_logger.setLevel(logging.WARN)

    if args.verbose:
        main_logger.setLevel(logging.DEBUG)
