WARNING_LEVEL := -Weverything
SILENCE_WARNINGS := -Wno-float-equal -Wno-poison-system-directories -Wno-unused-parameter -Wno-padded
BASE_DIR = $(shell pwd)
INCLUDE_DIR := $(BASE_DIR)/../../../out/generated/c

basic: basic.c $(INCLUDE_DIR)/ComprehensiveMessage.h
	clang $(WARNING_LEVEL) $(SILENCE_WARNINGS) -I$(INCLUDE_DIR) -O3 -g -o $@ basic.c

.PHONY: clean
clean:
	rm -rf basic

.PHONY: check
check: basic
	leaks -atExit -- ./basic
