using System;
using System.IO;
using System.Collections.Generic;

using SizedMessage;

class SizedHarness: TestHarness {

    static void Main(string[] args) {
        Dictionary<string, string> parsedArgs = parseArguments(args);

        var shortList = new SizedMessage.TextContainer();
        shortList.label = "list that fits in a byte";
        shortList.collection = new string[] {
            "Lorem", "ipsum", "dolor", "sit", "amet", "consectetur",
            "adipiscing", "elit", "sed", "do", "eiusmod", "tempor",
            "incididunt", "ut", "labore", "et", "dolore", "magna",
            "aliqua", "Ut", "enim", "ad", "minim", "veniam",
            "quis", "nostrud", "exercitation", "ullamco", "laboris", "nisi",
            "ut", "aliquip", "ex", "ea", "commodo", "consequat",
            "Duis", "aute", "irure", "dolor", "in", "reprehenderit",
            "in", "voluptate", "velit", "esse", "cillum", "dolore",
            "eu", "fugiat", "nulla", "pariatur", "Excepteur", "sint",
            "occaecat", "cupidatat", "non", "proident", "sunt", "in",
            "culpa", "qui", "officia", "deserunt", "mollit", "anim",
            "id", "est", "laborum",
        };

        if (parsedArgs.ContainsKey("generate"))
        {
            string outPath = parsedArgs["generate"];
            string outDir = System.IO.Path.GetDirectoryName(outPath);
            System.IO.Directory.CreateDirectory(outDir);
            FileStream f = new FileStream(outPath, FileMode.Create);
            BinaryWriter bw = new BinaryWriter(f);
            shortList.WriteBytes(bw, false);

            softAssert(shortList.GetSizeInBytes() == 464, "short list size calculation check");
            softAssert(shortList.GetSizeInBytes() == bw.BaseStream.Position, "written bytes check");
        }
        else if (parsedArgs.ContainsKey("read"))
        {
            FileStream f = File.OpenRead(parsedArgs["read"]);
            BinaryReader br = new BinaryReader(f);

            var input = SizedMessage.TextContainer.FromBytes(br);

            softAssert(input.label == shortList.label, "readback label comparison");
            softAssert(input.collection.Length == shortList.collection.Length, "readback list length");
            for (int i = 0; i < input.collection.Length; i++)
            {
                softAssert(input.collection[i] == shortList.collection[i], "short list comparison");
            }
        }


        check();
    }
}
