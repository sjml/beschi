package main

import (
	"flag"
	"io"
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

		seek, _ := dat.Seek(0, io.SeekCurrent)
		softAssert((int)(seek) == 67, "written bytes check")
	} else if len(*readPathPtr) > 0 {
		dat, err := os.Open(*readPathPtr)
		if err != nil {
			panic(err)
		}
		defer dat.Close()

		msgList, err := small_messages.UnpackMessages(dat)
		if err != nil {
			panic(err)
		}
		softAssert(err == nil, "packed read")

		softAssert(len(msgList) == 10, "packed count")

		softAssert(msgList[0].GetMessageType() == small_messages.IntMessageType, "msg 0 type")
		softAssert(msgList[1].GetMessageType() == small_messages.FloatMessageType, "msg 1 type")
		softAssert(msgList[2].GetMessageType() == small_messages.FloatMessageType, "msg 2 type")
		softAssert(msgList[3].GetMessageType() == small_messages.FloatMessageType, "msg 3 type")
		softAssert(msgList[4].GetMessageType() == small_messages.IntMessageType, "msg 4 type")
		softAssert(msgList[5].GetMessageType() == small_messages.EmptyMessageType, "msg 5 type")
		softAssert(msgList[6].GetMessageType() == small_messages.LongMessageType, "msg 6 type")
		softAssert(msgList[7].GetMessageType() == small_messages.LongMessageType, "msg 7 type")
		softAssert(msgList[8].GetMessageType() == small_messages.LongMessageType, "msg 8 type")
		softAssert(msgList[9].GetMessageType() == small_messages.IntMessageType, "msg 9 type")
	}

	if !ok {
		os.Stderr.WriteString("Failed assertions.\n")
		os.Exit(1)
	}
}
