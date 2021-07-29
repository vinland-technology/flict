# SPDX-FileCopyrightText: 2021 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later


FMT="* %-$40s"
CHARS_TO_PRINT=38
test:
	cd tests && ./all.sh
	@echo
	@echo
	@echo "Misc tests"
	@echo "---------------------------------"
	@echo -n "Checking spdx tags with reuse:            "
	@reuse lint > /dev/null && echo OK


loc:
	@echo "Line counts"
	@echo -n "Python: "
	@find . -name "*.py" | xargs wc -l | tail -1 | sed 's,total,lines,g'
	@echo -n "Bash:   "
	@find . -name "*.sh" | xargs wc -l | tail -1 | sed 's,total,lines,g'
	@echo -n "Markdown:   "
	@find . -name "*.markdown" | xargs wc -l | tail -1 | sed 's,total,lines,g'
