BASE_DIR = $(shell pwd)

.PHONY: test
test:
	pytest

clean:
	rm -rf $(BASE_DIR)/out/*
