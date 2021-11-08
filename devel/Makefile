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
	@-reuse lint > /dev/null && echo OK || echo "Reuse failed, but build is OK"


loc:
	@echo "Line counts"
	@printf "Python:   %4s\n" `find . -name "*.py" | xargs wc -l | tail -1 | sed 's,total,,g'`
	@printf "Bash:     %4s\n" `find . -name "*.sh" | xargs wc -l | tail -1 | sed 's,total,,g'`
	@printf "Total:    %4s\n" `find . -name "*.py" -o -name "*.sh" | xargs wc -l | tail -1 | sed 's,total,,g'`
