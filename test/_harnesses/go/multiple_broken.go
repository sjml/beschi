package main

import (
	"encoding/binary"
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

	var full BrokenMessages.FullMessage
	full.X = 1.0
	full.Y = 2.0
	full.Z = 3.0

	generatePathPtr := flag.String("generate", "", "")
	readPathPtr := flag.String("read", "", "")
	flag.Parse()

	if len(*generatePathPtr) > 0 {
		os.MkdirAll(filepath.Dir(*generatePathPtr), os.ModePerm)
		dat, err := os.Create(*generatePathPtr)
		if err != nil {
			panic(err)
		}
		defer dat.Close()

		full.WriteBytes(dat, true)
		full.WriteBytes(dat, true)
		full.WriteBytes(dat, true)

		// write a truncated message tagged as a full one
		binary.Write(dat, binary.LittleEndian, BrokenMessages.FullMessageType)
		trunc.WriteBytes(dat, false)

		full.WriteBytes(dat, true)
		full.WriteBytes(dat, true)
		full.WriteBytes(dat, true)
	} else if len(*readPathPtr) > 0 {
		dat, err := os.Open(*readPathPtr)
		if err != nil {
			panic(err)
		}
		defer dat.Close()

		msgList := BrokenMessages.ProcessRawBytes(dat)

		softAssert(len(msgList) == 5, "read broken stream length")
		softAssert(msgList[4] == nil, "read broken stream null sentinel")
	}

	if !ok {
		os.Stderr.WriteString("Failed assertions.\n")
		os.Exit(1)
	}
}
