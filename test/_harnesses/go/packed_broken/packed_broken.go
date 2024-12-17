package main

import (
	"flag"
	"os"
	"path/filepath"

	"messages/small_messages"
)

var ok bool = true

func softAssert(condition bool, label string) {
	if !condition {
		os.Stderr.WriteString("FAILED! Go: " + label + "\n")
		ok = false
	}
}

func main() {
	var msgList = []small_messages.Message{
		small_messages.IntMessage{},
		small_messages.FloatMessage{},
		small_messages.FloatMessage{},
		small_messages.FloatMessage{},
		small_messages.IntMessage{},
		small_messages.EmptyMessage{},
		small_messages.LongMessage{},
		small_messages.LongMessage{},
		small_messages.LongMessage{},
		small_messages.IntMessage{},
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

		small_messages.PackMessages(msgList, dat)
		_, err = dat.WriteAt([]byte{15}, 4)
		if err != nil {
			panic(err)
		}
	} else if len(*readPathPtr) > 0 {
		dat, err := os.Open(*readPathPtr)
		if err != nil {
			panic(err)
		}
		defer dat.Close()

		_, err = small_messages.UnpackMessages(dat)
		softAssert(err != nil, "broken unpack")
		softAssert(err.Error() == "unexpected number of messages in buffer", "broken unpack message")
	}

	if !ok {
		os.Stderr.WriteString("Failed assertions.\n")
		os.Exit(1)
	}
}
