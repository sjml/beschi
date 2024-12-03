using System;
using System.IO;
using System.Collections.Generic;


class PackedHarness: TestHarness {
    static void Main(string[] args) {
        var parsedArgs = parseArguments(args);

        var msgList = new List<SmallMessages.Message> {
            new SmallMessages.IntMessage(),
            new SmallMessages.FloatMessage(),
            new SmallMessages.FloatMessage(),
            new SmallMessages.FloatMessage(),
            new SmallMessages.IntMessage(),
            new SmallMessages.EmptyMessage(),
            new SmallMessages.LongMessage(),
            new SmallMessages.LongMessage(),
            new SmallMessages.LongMessage(),
            new SmallMessages.IntMessage(),
        };

        if (parsedArgs.ContainsKey("generate"))
        {
            string outPath = parsedArgs["generate"];
            string outDir = System.IO.Path.GetDirectoryName(outPath);
            System.IO.Directory.CreateDirectory(outDir);
            FileStream f = new FileStream(outPath, FileMode.Create);
            BinaryWriter bw = new BinaryWriter(f);
            SmallMessages.Message.PackMessages(msgList, bw);

            softAssert(bw.BaseStream.Position == 67, "written bytes check");
        }
        else if (parsedArgs.ContainsKey("read"))
        {
            FileStream f = File.OpenRead(parsedArgs["read"]);
            BinaryReader br = new BinaryReader(f);

            var unpacked = SmallMessages.Message.UnpackMessages(br);

            softAssert(unpacked.Length == 10, "packed count");
            softAssert(unpacked[0].GetMessageType() == SmallMessages.MessageType.IntMessageType,   "packed[0]");
            softAssert(unpacked[1].GetMessageType() == SmallMessages.MessageType.FloatMessageType, "packed[1]");
            softAssert(unpacked[2].GetMessageType() == SmallMessages.MessageType.FloatMessageType, "packed[2]");
            softAssert(unpacked[3].GetMessageType() == SmallMessages.MessageType.FloatMessageType, "packed[3]");
            softAssert(unpacked[4].GetMessageType() == SmallMessages.MessageType.IntMessageType,   "packed[4]");
            softAssert(unpacked[5].GetMessageType() == SmallMessages.MessageType.EmptyMessageType, "packed[5]");
            softAssert(unpacked[6].GetMessageType() == SmallMessages.MessageType.LongMessageType,  "packed[6]");
            softAssert(unpacked[7].GetMessageType() == SmallMessages.MessageType.LongMessageType,  "packed[7]");
            softAssert(unpacked[8].GetMessageType() == SmallMessages.MessageType.LongMessageType,  "packed[8]");
            softAssert(unpacked[9].GetMessageType() == SmallMessages.MessageType.IntMessageType,   "packed[9]");
        }

        check();
    }
}
