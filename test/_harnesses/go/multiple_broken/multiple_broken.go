package main

import (
	"encoding/binary"
	"flag"
	"io"
	"os"
	"path/filepath"

	"messages/broken_messages"
)

var ok bool = true

func softAssert(condition bool, label string) {
	if !condition {
		os.Stderr.WriteString("FAILED! Go: " + label + "\n")
		ok = false
	}
}

func main() {
	var trunc broken_messages.TruncatedMessage
	trunc.X = 1.0
	trunc.Y = 2.0

	var full broken_messages.FullMessage
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
		binary.Write(dat, binary.LittleEndian, broken_messages.FullMessageType)
		trunc.WriteBytes(dat, false)

		full.WriteBytes(dat, true)
		full.WriteBytes(dat, true)
		full.WriteBytes(dat, true)

		size := 6 * full.GetSizeInBytes()
		size += 6 // markers, one byte each
		size += trunc.GetSizeInBytes()
		size += 1 // trunc marker

		seek, _ := dat.Seek(0, io.SeekCurrent)
		softAssert(size == (int)(seek), "written bytes check")
	} else if len(*readPathPtr) > 0 {
		dat, err := os.Open(*readPathPtr)
		if err != nil {
			panic(err)
		}
		defer dat.Close()

		_, err = broken_messages.ProcessRawBytes(dat)
		softAssert(err != nil, "read broken stream")
		softAssert(err.Error() == "Unknown message type: 63", "broken stream error message")
	}

	if !ok {
		os.Stderr.WriteString("Failed assertions.\n")
		os.Exit(1)
	}
}
