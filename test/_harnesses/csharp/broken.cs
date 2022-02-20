using System;
using System.IO;
using System.Collections.Generic;

using BrokenMessages;

class ProtocolHarness {

    static bool OK = true;
    static void softAssert(bool condition, string label)
    {
        if (!condition)
        {
            Console.Error.WriteLine("FAILED! CSharp: " + label);
            OK = false;
        }
    }

    // super basic, just turn it into dict please; don't want another dependency
    static Dictionary<string, string> parseArguments(string[] args)
    {
        Dictionary<string, string> parsed = new Dictionary<string, string>();

        string currentKeyword = null;
        for (int i = 0; i < args.Length; i++)
        {
            if (args[i].StartsWith("--"))
            {
                currentKeyword = args[i].Substring(2);
                continue;
            }
            if (currentKeyword != null)
            {
                parsed[currentKeyword] = args[i];
                currentKeyword = null;
                continue;
            }
            // shouldn't get here in current usage
            parsed[args[i]] = "";
        }

        return parsed;
    }

    static void Main(string[] args) {
        Dictionary<string, string> parsedArgs = parseArguments(args);

        BrokenMessages.TruncatedMessage trunc = new BrokenMessages.TruncatedMessage();
        trunc.x = 1.0f;
        trunc.y = 2.0f;

        BrokenMessages.ListMessage lmsg = new BrokenMessages.ListMessage();
        lmsg.ints = new short[]{1, 2, 32767, 4, 5};

        if (parsedArgs.ContainsKey("generateBroken"))
        {
            string outPath = parsedArgs["generateBroken"];
            string outDir = System.IO.Path.GetDirectoryName(outPath);
            System.IO.Directory.CreateDirectory(outDir);
            FileStream f = new FileStream(outPath, FileMode.Create);
            BinaryWriter bw = new BinaryWriter(f);
            trunc.WriteBytes(bw);
        }
        else if (parsedArgs.ContainsKey("readBroken"))
        {
            FileStream f = File.OpenRead(parsedArgs["readBroken"]);
            BinaryReader br = new BinaryReader(f);
            BrokenMessages.FullMessage input = BrokenMessages.FullMessage.FromBytes(br);
            softAssert(input == null, "reading broken message");
        }

        else if (parsedArgs.ContainsKey("generateTruncated"))
        {
            byte[] buffer = new byte[16];
            MemoryStream m = new MemoryStream(buffer);
            BinaryWriter bw = new BinaryWriter(m);
            lmsg.WriteBytes(bw);

            // tweak the buffer so the message looks longer
            buffer[0] = 0xFF;

            string outPath = parsedArgs["generateTruncated"];
            string outDir = System.IO.Path.GetDirectoryName(outPath);
            System.IO.Directory.CreateDirectory(outDir);

            File.WriteAllBytes(outPath, buffer);
        }
        else if (parsedArgs.ContainsKey("readTruncated"))
        {
            FileStream f = File.OpenRead(parsedArgs["readTruncated"]);
            BinaryReader br = new BinaryReader(f);
            BrokenMessages.ListMessage input = BrokenMessages.ListMessage.FromBytes(br);
            softAssert(input == null, "reading truncated message");
        }

        if (!OK)
        {
            Console.Error.WriteLine("Failed assertions.");
            Environment.Exit(1);
        }
    }
}
