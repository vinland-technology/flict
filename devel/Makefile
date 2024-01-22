# SPDX-FileCopyrightText: 2021 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later

check: reuse schemas pytest flake8

flake8:
	flake8

schemas:
	FILES=`find flict/var/schemas/ -name "*.json"`
	for file in `find flict/var/schemas/ -name "*.json"` ; do \
		jq . $$file 1>/dev/null; \
	done

pytest:
	PYTHONPATH=. pytest  tests/

reuse:
	reuse lint


