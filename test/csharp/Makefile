BASE_DIR = $(shell pwd)
LIB_DIR = $(BASE_DIR)/../../out/generated/csharp
LIB_SRC = $(LIB_DIR)/WireMessage.cs
COMPILER := csc

EXE = $(BASE_DIR)/../../out/executables/harness_csharp

$(EXE): harness.cs $(LIB_SRC)
	mkdir -p $(@D)
	$(COMPILER) -nologo -target:exe -out:$@ $^

.PHONE: clean
clean:
	rm -rf $(EXE)

.PHONY: generate
generate: $(EXE)
	mono $(EXE) --generate

.PHONY: read
read: $(EXE)
	mono $(EXE) --read
