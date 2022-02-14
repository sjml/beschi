BASE_DIR = $(shell pwd)
LIB_SRC = $(BASE_DIR)/src/WireMessage/WireMessage.go

EXE = $(BASE_DIR)/../../harnesses/harness_go

$(LIB_SRC): $(BASE_DIR)/../../../protocol.toml
	cp $(BASE_DIR)/../../../out/go/WireMessage.go $(LIB_SRC)

.DEFAULT_GOAL := $(EXE)
$(EXE): $(BASE_DIR)/harness.go $(LIB_SRC)
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
