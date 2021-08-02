# SPDX-FileCopyrightText: 2021 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later


#
# target for testing locally (under devel)
#
test:
	cd tests && ./all.sh
	@echo
	@echo
	@echo "Misc tests"
	@echo "---------------------------------"
	@echo -n "Checking spdx tags with reuse:            "
	@reuse lint > /dev/null && echo OK

#
# target for testing installed flict
#
pip-test:
	@echo
	@echo
	@echo "installation tests"
	@echo "---------------------------------"
	@echo "uninstalling flict"
	@-pip3 uninstall -y flict
	@echo
	@echo "installing flict"
	@pip3 install .
	@echo
	@echo "run tests"
	@cd tests && ./all.sh flict

#
# test locally and installed
#
all: test pip-test

loc:
	@echo "Line counts"
	@printf "Python:   %4s\n" `find . -name "*.py" | xargs wc -l | tail -1 | sed 's,total,,g'`
	@printf "Bash:     %4s\n" `find . -name "*.sh" | xargs wc -l | tail -1 | sed 's,total,,g'`
	@printf "Total:    %4s\n" `find . -name "*.py" -o -name "*.sh" | xargs wc -l | tail -1 | sed 's,total,,g'`
