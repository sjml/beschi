using System;
using System.IO;
using System.Collections.Generic;

using BrokenMessages;

class TruncatedHarness: TestHarness {

    static void Main(string[] args) {
        Dictionary<string, string> parsedArgs = parseArguments(args);

        var lmsg = new BrokenMessages.ListMessage();
        lmsg.ints = new short[]{1, 2, 32767, 4, 5};

        if (parsedArgs.ContainsKey("generate"))
        {
            byte[] buffer = new byte[14];
            MemoryStream m = new MemoryStream(buffer);
            BinaryWriter bw = new BinaryWriter(m);
            lmsg.WriteBytes(bw, false);

            softAssert(lmsg.GetSizeInBytes() == bw.BaseStream.Position, "written bytes check");

            // tweak the buffer so the message looks longer
            buffer[0] = 0xFF;

            string outPath = parsedArgs["generate"];
            string outDir = System.IO.Path.GetDirectoryName(outPath);
            System.IO.Directory.CreateDirectory(outDir);

            File.WriteAllBytes(outPath, buffer);
        }
        else if (parsedArgs.ContainsKey("read"))
        {
            FileStream f = File.OpenRead(parsedArgs["read"]);
            BinaryReader br = new BinaryReader(f);
            BrokenMessages.ListMessage input = BrokenMessages.ListMessage.FromBytes(br);
            softAssert(input == null, "reading truncated message");
        }


        check();
    }
}
