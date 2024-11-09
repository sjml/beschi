package main

import (
	"bytes"
	"flag"
	"io"
	"os"
	"path/filepath"

	"messages/nested"
	"messages/smallmessages"
)

var ok bool = true

func softAssert(condition bool, label string) {
	if !condition {
		os.Stderr.WriteString("FAILED! Go: " + label + "\n")
		ok = false
	}
}

func main() {
	var nested nested.DeepData
	nested.Data.Data.Data.Data.Data.Data.Data.Data.Datums = make([]float32, 2)

	var emptyMsg smallmessages.EmptyMessage
	var byteMsg smallmessages.ByteMessage
	byteMsg.ByteMember = 242
	var intMsgA smallmessages.IntMessage
	intMsgA.IntMember = -42
	var intMsgB smallmessages.IntMessage
	intMsgB.IntMember = 2048
	var floatMsg smallmessages.FloatMessage
	floatMsg.FloatMember = 1234.5678
	var longMsg smallmessages.LongMessage
	longMsg.IntMember = 2147483647 + 10 // (2^31 - 1) + 10

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

		byteMsg.WriteBytes(dat, true)  //  0
		intMsgA.WriteBytes(dat, true)  //  1
		intMsgB.WriteBytes(dat, true)  //  2
		emptyMsg.WriteBytes(dat, true) //  3
		longMsg.WriteBytes(dat, true)  //  4
		floatMsg.WriteBytes(dat, true) //  5
		intMsgA.WriteBytes(dat, true)  //  6
		intMsgB.WriteBytes(dat, true)  //  7
		intMsgB.WriteBytes(dat, true)  //  8
		intMsgB.WriteBytes(dat, true)  //  9
		intMsgA.WriteBytes(dat, true)  // 10
		emptyMsg.WriteBytes(dat, true) // 11

		size := 0
		size += byteMsg.GetSizeInBytes()
		size += intMsgA.GetSizeInBytes() * 3
		size += intMsgB.GetSizeInBytes() * 4
		size += emptyMsg.GetSizeInBytes() * 2
		size += longMsg.GetSizeInBytes()
		size += floatMsg.GetSizeInBytes()
		size += 12

		seek, _ := dat.Seek(0, io.SeekCurrent)
		softAssert(size == (int)(seek), "written bytes check")
	} else if len(*readPathPtr) > 0 {
		dat, err := os.Open(*readPathPtr)
		if err != nil {
			panic(err)
		}
		defer dat.Close()

		content, err := io.ReadAll(dat)
		if err != nil {
			panic(err)
		}
		buffer := make([]byte, len(content)+25)
		copy(buffer, content)
		reader := bytes.NewReader(buffer)

		msgList, err := smallmessages.ProcessRawBytes(reader)
		softAssert(err == nil, "reading multiple messages")

		softAssert(len(msgList) == 12, "reading multiple messages length")

		softAssert(msgList[0].GetMessageType() == smallmessages.ByteMessageType, "msg 0 type")
		softAssert(msgList[0].(*smallmessages.ByteMessage).ByteMember == byteMsg.ByteMember, "msg 0 content")

		softAssert(msgList[1].GetMessageType() == smallmessages.IntMessageType, "msg 1 type")
		softAssert(msgList[1].(*smallmessages.IntMessage).IntMember == intMsgA.IntMember, "msg 1 content")

		softAssert(msgList[2].GetMessageType() == smallmessages.IntMessageType, "msg 2 type")
		softAssert(msgList[2].(*smallmessages.IntMessage).IntMember == intMsgB.IntMember, "msg 2 content")

		softAssert(msgList[3].GetMessageType() == smallmessages.EmptyMessageType, "msg 3 type")

		softAssert(msgList[4].GetMessageType() == smallmessages.LongMessageType, "msg 4 type")
		softAssert(msgList[4].(*smallmessages.LongMessage).IntMember == longMsg.IntMember, "msg 4 content")

		softAssert(msgList[5].GetMessageType() == smallmessages.FloatMessageType, "msg 5 type")
		softAssert(msgList[5].(*smallmessages.FloatMessage).FloatMember == floatMsg.FloatMember, "msg 5 content")

		softAssert(msgList[6].GetMessageType() == smallmessages.IntMessageType, "msg 6 type")
		softAssert(msgList[6].(*smallmessages.IntMessage).IntMember == intMsgA.IntMember, "msg 6 content")

		softAssert(msgList[7].GetMessageType() == smallmessages.IntMessageType, "msg 7 type")
		softAssert(msgList[7].(*smallmessages.IntMessage).IntMember == intMsgB.IntMember, "msg 7 content")

		softAssert(msgList[8].GetMessageType() == smallmessages.IntMessageType, "msg 8 type")
		softAssert(msgList[8].(*smallmessages.IntMessage).IntMember == intMsgB.IntMember, "msg 8 content")

		softAssert(msgList[9].GetMessageType() == smallmessages.IntMessageType, "msg 9 type")
		softAssert(msgList[9].(*smallmessages.IntMessage).IntMember == intMsgB.IntMember, "msg 9 content")

		softAssert(msgList[10].GetMessageType() == smallmessages.IntMessageType, "msg 10 type")
		softAssert(msgList[10].(*smallmessages.IntMessage).IntMember == intMsgA.IntMember, "msg 10 content")

		softAssert(msgList[11].GetMessageType() == smallmessages.EmptyMessageType, "msg 11 type")
	}

	if !ok {
		os.Stderr.WriteString("Failed assertions.\n")
		os.Exit(1)
	}
}
