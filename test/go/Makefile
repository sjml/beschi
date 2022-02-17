BASE_DIR = $(shell pwd)
LIB_SRC_DIR = $(BASE_DIR)/src/WireMessage
LIB_SRC = $(LIB_SRC_DIR)/WireMessage.go

EXE = $(BASE_DIR)/../../out/executables/harness_go

$(LIB_SRC):
	mkdir -p $(LIB_SRC_DIR)
	ln -s $(BASE_DIR)/../../out/generated/go/WireMessage.go $(LIB_SRC)

.DEFAULT_GOAL := $(EXE)
$(EXE): $(BASE_DIR)/harness.go $(LIB_SRC)
	mkdir -p $(@D)
	GO111MODULE=off go build -o $(EXE) $(BASE_DIR)/harness.go

.PHONY: clean
clean:
	rm -rf $(EXE) $(LIB_SRC)

.PHONY: generate
generate: $(EXE)
	$(EXE) --generate

.PHONY: read
read: $(EXE)
	$(EXE) --read
