BASE_DIR = $(shell pwd)
LANGS = csharp typescript go

.PHONY: test
test:
	@$(BASE_DIR)/env/bin/python $(BASE_DIR)/scripts/example.py
	@$(BASE_DIR)/env/bin/python $(BASE_DIR)/scripts/verify.py $(LANGS)

.DEFAULT_GOAL := all
.PHONY: all
all:
	@$(BASE_DIR)/env/bin/python $(BASE_DIR)/example.py

clean:
	rm -rf $(BASE_DIR)/out/*
