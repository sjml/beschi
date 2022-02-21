package main

import (
	"bytes"
	"flag"
	"os"
	"path/filepath"

	"./src/BrokenMessages"
)

var ok bool = true

func softAssert(condition bool, label string) {
	if !condition {
		os.Stderr.WriteString("FAILED! Go: " + label + "\n")
		ok = false
	}
}

func main() {
	var lmsg BrokenMessages.ListMessage
	lmsg.Ints = []int16{1, 2, 32767, 4, 5}

	generatePathPtr := flag.String("generate", "", "")
	readPathPtr := flag.String("read", "", "")
	flag.Parse()

	if len(*generatePathPtr) > 0 {
		var mem bytes.Buffer
		blank := []byte{0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0}
		mem.Write(blank)
		mem.Reset()
		lmsg.WriteBytes(&mem, false)

		softAssert(lmsg.GetSizeInBytes() == len(blank), "written bytes check")

		// tweak the buffer so the message looks longer
		buffer := mem.Bytes()
		buffer[0] = 0xFF

		os.MkdirAll(filepath.Dir(*generatePathPtr), os.ModePerm)
		dat, err := os.Create(*generatePathPtr)
		if err != nil {
			panic(err)
		}
		defer dat.Close()

		dat.Write(buffer)
	} else if len(*readPathPtr) > 0 {
		dat, err := os.Open(*readPathPtr)
		if err != nil {
			panic(err)
		}
		defer dat.Close()

		input := BrokenMessages.ListMessageFromBytes(dat)

		softAssert(input == nil, "reading truncated message")
	}

	if !ok {
		os.Stderr.WriteString("Failed assertions.\n")
		os.Exit(1)
	}
}
