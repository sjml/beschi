BASE_DIR = $(shell pwd)

.PHONY: test
test:
	pytest -x

clean:
	rm -rf $(BASE_DIR)/out/*
