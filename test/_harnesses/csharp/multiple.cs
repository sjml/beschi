using System;
using System.IO;

using SmallMessages;
using Nested;

class MultipleHarness: TestHarness {

    static void Main(string[] args) {
        var parsedArgs = parseArguments(args);

        var emptyMsg = new SmallMessages.EmptyMessage();
        var byteMsg = new SmallMessages.ByteMessage();
        byteMsg.byteMember = 242;
        var intMsgA = new SmallMessages.IntMessage();
        intMsgA.intMember = -42;
        var intMsgB = new SmallMessages.IntMessage();
        intMsgB.intMember = 2048;
        var floatMsg = new SmallMessages.FloatMessage();
        floatMsg.floatMember = 1234.5678f;
        var longMsg = new SmallMessages.LongMessage();
        longMsg.intMember = 2147483647L + 10; // (2^31 - 1) + 10

        if (parsedArgs.ContainsKey("generate"))
        {
            string outPath = parsedArgs["generate"];
            string outDir = System.IO.Path.GetDirectoryName(outPath);
            System.IO.Directory.CreateDirectory(outDir);
            FileStream f = new FileStream(outPath, FileMode.Create);
            BinaryWriter bw = new BinaryWriter(f);

            byteMsg.WriteBytes(bw, true);   //  0
            intMsgA.WriteBytes(bw, true);   //  1
            intMsgB.WriteBytes(bw, true);   //  2
            emptyMsg.WriteBytes(bw, true);  //  3
            longMsg.WriteBytes(bw, true);   //  4
            floatMsg.WriteBytes(bw, true);  //  5
            intMsgA.WriteBytes(bw, true);   //  6
            intMsgB.WriteBytes(bw, true);   //  7
            intMsgB.WriteBytes(bw, true);   //  8
            intMsgB.WriteBytes(bw, true);   //  9
            intMsgA.WriteBytes(bw, true);   // 10
            emptyMsg.WriteBytes(bw, true);  // 11

            int size = 0;
            size += byteMsg.GetSizeInBytes();
            size += intMsgA.GetSizeInBytes() * 3;
            size += intMsgB.GetSizeInBytes() * 4;
            size += emptyMsg.GetSizeInBytes() * 2;
            size += longMsg.GetSizeInBytes();
            size += floatMsg.GetSizeInBytes();
            size += sizeof(byte) * 12;

            softAssert(size == bw.BaseStream.Position, "written bytes check");
        }
        else if (parsedArgs.ContainsKey("read"))
        {
            FileStream f = File.OpenRead(parsedArgs["read"]);
            BinaryReader br = new BinaryReader(f);

            SmallMessages.Message[] msgList = SmallMessages.Message.ProcessRawBytes(br);

            softAssert(msgList.Length == 12, "reading multiple messages length");

            softAssert(msgList[0].GetMessageType() == SmallMessages.MessageType.ByteMessageType, "msg 0 type");
            softAssert((msgList[0] as ByteMessage).byteMember == byteMsg.byteMember, "msg 0 content");

            softAssert(msgList[1].GetMessageType() == SmallMessages.MessageType.IntMessageType, "msg 1 type");
            softAssert((msgList[1] as IntMessage).intMember == intMsgA.intMember, "msg 1 content");

            softAssert(msgList[2].GetMessageType() == SmallMessages.MessageType.IntMessageType, "msg 2 type");
            softAssert((msgList[2] as IntMessage).intMember == intMsgB.intMember, "msg 2 content");

            softAssert(msgList[3].GetMessageType() == SmallMessages.MessageType.EmptyMessageType, "msg 3 type");

            softAssert(msgList[4].GetMessageType() == SmallMessages.MessageType.LongMessageType, "msg 4 type");
            softAssert((msgList[4] as LongMessage).intMember == longMsg.intMember, "msg 4 content");

            softAssert(msgList[5].GetMessageType() == SmallMessages.MessageType.FloatMessageType, "msg 5 type");
            softAssert((msgList[5] as FloatMessage).floatMember == floatMsg.floatMember, "msg 5 content");

            softAssert(msgList[6].GetMessageType() == SmallMessages.MessageType.IntMessageType, "msg 6 type");
            softAssert((msgList[6] as IntMessage).intMember == intMsgA.intMember, "msg 6 content");

            softAssert(msgList[7].GetMessageType() == SmallMessages.MessageType.IntMessageType, "msg 7 type");
            softAssert((msgList[7] as IntMessage).intMember == intMsgB.intMember, "msg 7 content");

            softAssert(msgList[8].GetMessageType() == SmallMessages.MessageType.IntMessageType, "msg 8 type");
            softAssert((msgList[8] as IntMessage).intMember == intMsgB.intMember, "msg 8 content");

            softAssert(msgList[9].GetMessageType() == SmallMessages.MessageType.IntMessageType, "msg 9 type");
            softAssert((msgList[9] as IntMessage).intMember == intMsgB.intMember, "msg 9 content");

            softAssert(msgList[10].GetMessageType() == SmallMessages.MessageType.IntMessageType, "msg 10 type");
            softAssert((msgList[10] as IntMessage).intMember == intMsgA.intMember, "msg 10 content");

            softAssert(msgList[11].GetMessageType() == SmallMessages.MessageType.EmptyMessageType, "msg 11 type");
        }


        check();
    }
}
