package main

import (
	"flag"
	"io"
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
	var broken BrokenMessages.TruncatedMessage
	broken.X = 1.0
	broken.Y = 2.0

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

		broken.WriteBytes(dat, false)

		seek, _ := dat.Seek(0, io.SeekCurrent)
		softAssert(broken.GetSizeInBytes() == (int)(seek), "written bytes check")
	} else if len(*readPathPtr) > 0 {
		dat, err := os.Open(*readPathPtr)
		if err != nil {
			panic(err)
		}
		defer dat.Close()

		input := BrokenMessages.FullMessageFromBytes(dat)

		softAssert(input == nil, "reading broken message")
	}

	if !ok {
		os.Stderr.WriteString("Failed assertions.\n")
		os.Exit(1)
	}
}
