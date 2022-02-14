BASE_DIR = $(shell pwd)
LIB_DIR = $(BASE_DIR)
LIB_SRC = $(LIB_DIR)/WireMessage.ts
NODE_LIBS = $(BASE_DIR)/node_modules

EXE = $(BASE_DIR)/harness.js

$(NODE_LIBS):
	npm install

$(LIB_SRC): $(BASE_DIR)/../../../protocol.toml
	cp $(BASE_DIR)/../../../out/typescript/WireMessage.ts $(BASE_DIR)/WireMessage.ts

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
