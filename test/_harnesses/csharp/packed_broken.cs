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
            bw.Flush();
            bw.BaseStream.Seek(4, SeekOrigin.Begin);
            bw.Write((byte)15);
            bw.Flush();
        }
        else if (parsedArgs.ContainsKey("read"))
        {
            FileStream f = File.OpenRead(parsedArgs["read"]);
            BinaryReader br = new BinaryReader(f);

            string errMsg = "";
            try
            {
                var unpacked = SmallMessages.Message.UnpackMessages(br);
            }
            catch (SmallMessages.DataReadErrorException e)
            {
                errMsg = e.Message;
            }
            softAssert(errMsg == "Unexpected number of messages in buffer.", "broken unpack error:" + errMsg);

        }

        check();
    }
}
