BASE_DIR = $(shell pwd)
LANGS = csharp typescript go

.PHONY: test
test:
	@$(BASE_DIR)/env/bin/python $(BASE_DIR)/example.py
	@$(BASE_DIR)/env/bin/python $(BASE_DIR)/verify.py $(LANGS)

.DEFAULT_GOAL := all
.PHONY: all
all:
	@$(BASE_DIR)/env/bin/python $(BASE_DIR)/example.py
