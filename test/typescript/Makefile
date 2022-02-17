BASE_DIR = $(shell pwd)
LIB_DIR = $(BASE_DIR)
LIB_SRC = $(BASE_DIR)/../../out/generated/typescript/WireMessage.ts
NODE_LIBS = $(BASE_DIR)/node_modules

EXE = $(BASE_DIR)/harness.js

$(NODE_LIBS):
	npm install

.DEFAULT_GOAL := $(EXE)
$(EXE): harness.ts $(LIB_SRC) $(NODE_LIBS)
	npx tsc

.PHONY: clean
clean:
	rm -rf $(EXE)
	rm -rf ./WireMessage.*

.PHONY: generate
generate: $(EXE) harness.ts $(LIB_SRC)
	node $(EXE) --generate

.PHONY: read
read: $(EXE) harness.ts $(LIB_SRC)
	node $(EXE) --read
