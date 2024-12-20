package main

import (
	"bytes"
	"flag"
	"io"
	"os"
	"path/filepath"

	"messages/nested"
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
	var nested nested.DeepData
	nested.Data.Data.Data.Data.Data.Data.Data.Data.Datums = make([]float32, 2)

	var emptyMsg small_messages.EmptyMessage
	var byteMsg small_messages.ByteMessage
	byteMsg.ByteMember = 242
	var intMsgA small_messages.IntMessage
	intMsgA.IntMember = -42
	var intMsgB small_messages.IntMessage
	intMsgB.IntMember = 2048
	var floatMsg small_messages.FloatMessage
	floatMsg.FloatMember = 1234.5678
	var longMsg small_messages.LongMessage
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

		msgList, err := small_messages.ProcessRawBytes(reader, -1)
		softAssert(err == nil, "reading multiple messages")

		softAssert(len(msgList) == 12, "reading multiple messages length")

		softAssert(msgList[0].GetMessageType() == small_messages.ByteMessageType, "msg 0 type")
		softAssert(msgList[0].(*small_messages.ByteMessage).ByteMember == byteMsg.ByteMember, "msg 0 content")

		softAssert(msgList[1].GetMessageType() == small_messages.IntMessageType, "msg 1 type")
		softAssert(msgList[1].(*small_messages.IntMessage).IntMember == intMsgA.IntMember, "msg 1 content")

		softAssert(msgList[2].GetMessageType() == small_messages.IntMessageType, "msg 2 type")
		softAssert(msgList[2].(*small_messages.IntMessage).IntMember == intMsgB.IntMember, "msg 2 content")

		softAssert(msgList[3].GetMessageType() == small_messages.EmptyMessageType, "msg 3 type")

		softAssert(msgList[4].GetMessageType() == small_messages.LongMessageType, "msg 4 type")
		softAssert(msgList[4].(*small_messages.LongMessage).IntMember == longMsg.IntMember, "msg 4 content")

		softAssert(msgList[5].GetMessageType() == small_messages.FloatMessageType, "msg 5 type")
		softAssert(msgList[5].(*small_messages.FloatMessage).FloatMember == floatMsg.FloatMember, "msg 5 content")

		softAssert(msgList[6].GetMessageType() == small_messages.IntMessageType, "msg 6 type")
		softAssert(msgList[6].(*small_messages.IntMessage).IntMember == intMsgA.IntMember, "msg 6 content")

		softAssert(msgList[7].GetMessageType() == small_messages.IntMessageType, "msg 7 type")
		softAssert(msgList[7].(*small_messages.IntMessage).IntMember == intMsgB.IntMember, "msg 7 content")

		softAssert(msgList[8].GetMessageType() == small_messages.IntMessageType, "msg 8 type")
		softAssert(msgList[8].(*small_messages.IntMessage).IntMember == intMsgB.IntMember, "msg 8 content")

		softAssert(msgList[9].GetMessageType() == small_messages.IntMessageType, "msg 9 type")
		softAssert(msgList[9].(*small_messages.IntMessage).IntMember == intMsgB.IntMember, "msg 9 content")

		softAssert(msgList[10].GetMessageType() == small_messages.IntMessageType, "msg 10 type")
		softAssert(msgList[10].(*small_messages.IntMessage).IntMember == intMsgA.IntMember, "msg 10 content")

		softAssert(msgList[11].GetMessageType() == small_messages.EmptyMessageType, "msg 11 type")
	}

	if !ok {
		os.Stderr.WriteString("Failed assertions.\n")
		os.Exit(1)
	}
}
