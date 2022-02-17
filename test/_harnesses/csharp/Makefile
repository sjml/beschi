BASE_DIR = $(shell pwd)
LIB_DIR = $(BASE_DIR)/../../../out/generated/csharp
LIB_SRC = $(LIB_DIR)/WireMessage.cs
COMPILER := csc
BUNDLER := mkbundle

INTERMEDIATE = $(BASE_DIR)/../../../out/intermediate/harness_csharp
EXE = $(BASE_DIR)/../../../out/executables/harness_csharp
MSG = $(BASE_DIR)/../../../out/data/test.csharp.msg

.DEFAULT_GOAL := $(EXE)

$(INTERMEDIATE): harness.cs $(LIB_SRC)
	mkdir -p $(@D)
	$(COMPILER) -nologo -target:exe -out:$@ $^

$(EXE): $(INTERMEDIATE)
	mkdir -p $(@D)
	$(BUNDLER) --simple $(INTERMEDIATE) -o $(EXE)

.PHONE: clean
clean:
	rm -rf $(EXE) $(INTERMEDIATE)
