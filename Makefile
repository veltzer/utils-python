##############
# PARAMETERS #
##############
# do you want to see the commands executed ?
DO_MKDBG:=0
ALL_PACKAGES:=$(dir $(wildcard */__init__.py))

########
# CODE #
########
# silent stuff
ifeq ($(DO_MKDBG),1)
Q:=
# we are not silent in this branch
else # DO_MKDBG
Q:=@
#.SILENT:
endif # DO_MKDBG

ALL:=

#########
# RULES #
#########
.DEFAULT_GOAL=all
.PHONY: all
all: $(ALL)

.PHONY: install
install:
	$(Q)pymakehelper symlink_install --source_folder bin --target_folder ~/install/bin
	$(Q)pymakehelper symlink_install --source_folder python --target_folder ~/install/python

.PHONY: pylint
pylint:
	@pylint --reports=n --score=n $(ALL_PACKAGES)

.PHONT: check_shebang
check_shebang:
	@head --lines=1 --quiet bin/*.py | sort -u
