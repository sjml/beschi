BASE_DIR = $(shell pwd)
LIB_DIR = $(BASE_DIR)/../../../out/csharp
LIB_SRC = $(LIB_DIR)/WireMessage.cs
COMPILER := csc

EXE = $(BASE_DIR)/../../harnesses/harness_csharp

$(EXE): harness.cs $(LIB_SRC)
	$(COMPILER) -nologo -out:$@ $^

.PHONE: clean
clean:
	rm -rf $(EXE)

.PHONY: generate
generate: $(EXE)
	mono $(EXE) --generate

.PHONY: read
read: $(EXE)
	mono $(EXE) --read
