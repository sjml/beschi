BASE_DIR = $(shell pwd)
LIB_DIR = $(BASE_DIR)
LIB_SRC = $(BASE_DIR)/../../../out/generated/typescript/WireMessage.ts
NODE_LIBS = $(BASE_DIR)/node_modules

INTERMEDIATE = $(BASE_DIR)/harness.js
EXE = $(BASE_DIR)/../../../out/executables/harness_typescript
MSG = $(BASE_DIR)/../../../out/data/test.typescript.msg

$(NODE_LIBS):
	npm install

.DEFAULT_GOAL := $(EXE)

$(INTERMEDIATE): harness.ts $(LIB_SRC) $(NODE_LIBS)
	npx tsc

$(EXE): $(INTERMEDIATE)
	sed "s/{# EXE_NAME #}/harness/" ./exe_template > $(EXE)
	chmod +x $(EXE)

.PHONY: clean
clean:
	rm -rf $(EXE) $(INTERMEDIATE)
