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
	var trunc BrokenMessages.TruncatedMessage
	trunc.X = 1.0
	trunc.Y = 2.0

	var lmsg BrokenMessages.ListMessage
	lmsg.Ints = []int16{1, 2, 32767, 4, 5}

	generateBrokenPathPtr := flag.String("generateBroken", "", "")
	readBrokenPathPtr := flag.String("readBroken", "", "")
	generateTruncatedPathPtr := flag.String("generateTruncated", "", "")
	readTruncatedPathPtr := flag.String("readTruncated", "", "")
	flag.Parse()

	if len(*generateBrokenPathPtr) > 0 {
		os.MkdirAll(filepath.Dir(*generateBrokenPathPtr), os.ModePerm)
		dat, err := os.Create(*generateBrokenPathPtr)
		if err != nil {
			panic(err)
		}
		defer dat.Close()

		trunc.WriteBytes(dat, false)
	} else if len(*readBrokenPathPtr) > 0 {
		dat, err := os.Open(*readBrokenPathPtr)
		if err != nil {
			panic(err)
		}
		defer dat.Close()

		input := BrokenMessages.FullMessageFromBytes(dat)

		softAssert(input == nil, "reading broken message")
	} else if len(*generateTruncatedPathPtr) > 0 {
		var mem bytes.Buffer
		blank := []byte{0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0}
		mem.Write(blank)
		mem.Reset()
		lmsg.WriteBytes(&mem, false)

		// tweak the buffer so the message looks longer
		buffer := mem.Bytes()
		buffer[0] = 0xFF

		os.MkdirAll(filepath.Dir(*generateTruncatedPathPtr), os.ModePerm)
		dat, err := os.Create(*generateTruncatedPathPtr)
		if err != nil {
			panic(err)
		}
		defer dat.Close()

		dat.Write(buffer)
	} else if len(*readTruncatedPathPtr) > 0 {
		dat, err := os.Open(*readTruncatedPathPtr)
		if err != nil {
			panic(err)
		}
		defer dat.Close()

		input := BrokenMessages.ListMessageFromBytes(dat)

		softAssert(input == nil, "reading broken message")
	}

	if !ok {
		os.Stderr.WriteString("Failed assertions.\n")
		os.Exit(1)
	}
}
