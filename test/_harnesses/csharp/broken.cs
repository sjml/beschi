using System;
using System.IO;
using System.Collections.Generic;

using BrokenMessages;

class BrokenHarness: TestHarness {

    static void Main(string[] args) {
        Dictionary<string, string> parsedArgs = parseArguments(args);

        var broken = new BrokenMessages.TruncatedMessage();
        broken.x = 1.0f;
        broken.y = 2.0f;

        if (parsedArgs.ContainsKey("generate"))
        {
            string outPath = parsedArgs["generate"];
            string outDir = System.IO.Path.GetDirectoryName(outPath);
            System.IO.Directory.CreateDirectory(outDir);
            FileStream f = new FileStream(outPath, FileMode.Create);
            BinaryWriter bw = new BinaryWriter(f);
            broken.WriteBytes(bw, false);

            softAssert(broken.GetSizeInBytes() == bw.BaseStream.Position, "written bytes check");
        }
        else if (parsedArgs.ContainsKey("read"))
        {
            FileStream f = File.OpenRead(parsedArgs["read"]);
            BinaryReader br = new BinaryReader(f);
            string errMsg = "";
            try
            {
                var input = BrokenMessages.FullMessage.FromBytes(br);
            }
            catch (BrokenMessages.DataReadErrorException e)
            {
                errMsg = e.Message;
            }
            softAssert(errMsg == "Could not read FullMessage from offset 8", "reading broken message");
        }


        check();
    }
}
