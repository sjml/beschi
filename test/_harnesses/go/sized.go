package main

import (
	"flag"
	"io"
	"os"
	"path/filepath"

	"./src/SizedMessage"
)

var ok bool = true

func softAssert(condition bool, label string) {
	if !condition {
		os.Stderr.WriteString("FAILED! Go: " + label + "\n")
		ok = false
	}
}

func main() {
	var shortList SizedMessage.TextContainer
	shortList.Label = "lsit that fits in a byte"
	shortList.Collection = []string{
		"Lorem", "ipsum", "dolor", "sit", "amet", "consectetur",
		"adipiscing", "elit", "sed", "do", "eiusmod", "tempor",
		"incididunt", "ut", "labore", "et", "dolore", "magna",
		"aliqua", "Ut", "enim", "ad", "minim", "veniam",
		"quis", "nostrud", "exercitation", "ullamco", "laboris", "nisi",
		"ut", "aliquip", "ex", "ea", "commodo", "consequat",
		"Duis", "aute", "irure", "dolor", "in", "reprehenderit",
		"in", "voluptate", "velit", "esse", "cillum", "dolore",
		"eu", "fugiat", "nulla", "pariatur", "Excepteur", "sint",
		"occaecat", "cupidatat", "non", "proident", "sunt", "in",
		"culpa", "qui", "officia", "deserunt", "mollit", "anim",
		"id", "est", "laborum",
	}

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

		shortList.WriteBytes(dat, false)

		softAssert(shortList.GetSizeInBytes() == 464, "short list size calculation check")
		seek, _ := dat.Seek(0, io.SeekCurrent)
		softAssert(shortList.GetSizeInBytes() == (int)(seek), "written bytes check")
	} else if len(*readPathPtr) > 0 {
		dat, err := os.Open(*readPathPtr)
		if err != nil {
			panic(err)
		}
		defer dat.Close()

		input := SizedMessage.TextContainerFromBytes(dat)

		softAssert(input.Label == shortList.Label, "readback label comparison")
		softAssert(len(input.Collection) == len(shortList.Collection), "readback list length")
		for i := 0; i < len(input.Collection); i++ {
			softAssert(input.Collection[i] == shortList.Collection[i], "short list comparison")
		}
	}

	if !ok {
		os.Stderr.WriteString("Failed assertions.\n")
		os.Exit(1)
	}
}
