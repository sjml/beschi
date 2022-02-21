using System;
using System.IO;

using BrokenMessages;

class MultipleBrokenHarness: TestHarness {

    static void Main(string[] args) {
        var parsedArgs = parseArguments(args);

        var trunc = new BrokenMessages.TruncatedMessage();
        trunc.x = 1.0f;
        trunc.y = 2.0f;

        var full = new BrokenMessages.FullMessage();
        full.x = 1.0f;
        full.y = 2.0f;
        full.z = 3.0f;

        if (parsedArgs.ContainsKey("generate"))
        {
            string outPath = parsedArgs["generate"];
            string outDir = System.IO.Path.GetDirectoryName(outPath);
            System.IO.Directory.CreateDirectory(outDir);
            FileStream f = new FileStream(outPath, FileMode.Create);
            BinaryWriter bw = new BinaryWriter(f);

            full.WriteBytes(bw, true);
            full.WriteBytes(bw, true);
            full.WriteBytes(bw, true);

            // write a truncated message tagged as a full one
            bw.Write((byte)MessageType.FullMessageType);
            trunc.WriteBytes(bw, false);

            full.WriteBytes(bw, true);
            full.WriteBytes(bw, true);
            full.WriteBytes(bw, true);
        }
        else if (parsedArgs.ContainsKey("read"))
        {
            FileStream f = File.OpenRead(parsedArgs["read"]);
            BinaryReader br = new BinaryReader(f);

            Message[] msgList = BrokenMessages.Message.ProcessRawBytes(br);

            softAssert(msgList.Length == 5, "read broken stream length");
            softAssert(msgList[4] == null, "read broken stream null sentinel");
        }


        check();
    }
}
