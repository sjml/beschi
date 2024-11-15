using System;
using System.IO;

using ComprehensiveMessage;

class BasicHarness: TestHarness {

    static void Main(string[] args) {
        var example = new ComprehensiveMessage.TestingMessage();

        var parsedArgs = parseArguments(args);

        if (parsedArgs.ContainsKey("generate"))
        {
            string outPath = parsedArgs["generate"];
            string outDir = System.IO.Path.GetDirectoryName(outPath);
            System.IO.Directory.CreateDirectory(outDir);
            FileStream f = new FileStream(outPath, FileMode.Create);
            BinaryWriter bw = new BinaryWriter(f);
            example.WriteBytes(bw, false);
            softAssert(example.GetSizeInBytes() == bw.BaseStream.Position, "written bytes check");
        }
        else if (parsedArgs.ContainsKey("read"))
        {
            FileStream f = File.OpenRead(parsedArgs["read"]);
            BinaryReader br = new BinaryReader(f);
            ComprehensiveMessage.TestingMessage input = ComprehensiveMessage.TestingMessage.FromBytes(br);
            softAssert(input != null, "parsing test message");

            softAssert(input.b == example.b, "byte");
            softAssert(input.tf == example.tf, "bool");
            softAssert(input.i16 == example.i16, "i16");
            softAssert(input.ui16 == example.ui16, "ui16");
            softAssert(input.i32 == example.i32, "i32");
            softAssert(input.ui32 == example.ui32, "ui32");
            softAssert(input.i64 == example.i64, "i64");
            softAssert(input.ui64 == example.ui64, "ui64");
            softAssert(input.f == example.f, "float");
            softAssert(input.d == example.d, "double");
            softAssert(input.s == example.s, "string");
            softAssert(input.v2.x == example.v2.x, "Vec2");
            softAssert(input.v2.y == example.v2.y, "Vec2");
            softAssert(input.v3.x == example.v3.x, "Vec3");
            softAssert(input.v3.y == example.v3.y, "Vec3");
            softAssert(input.v3.z == example.v3.z, "Vec3");
            softAssert(input.c.r == example.c.r, "Color");
            softAssert(input.c.g == example.c.g, "Color");
            softAssert(input.c.b == example.c.b, "Color");
            softAssert(input.sl.Count == example.sl.Count, "[string].length");
            for (int i = 0; i < input.sl.Count; i++)
            {
                softAssert(input.sl[i] == example.sl[i], "[string]");
            }
            softAssert(input.v2l.Count == example.v2l.Count, "[Vec2].length");
            for (int i = 0; i < input.v2l.Count; i++)
            {
                softAssert(input.v2l[i].x == example.v2l[i].x, "[Vec2].x");
                softAssert(input.v2l[i].y == example.v2l[i].y, "[Vec2].y");
            }
            softAssert(input.v3l.Count == example.v3l.Count, "[Vec3].length");
            for (int i = 0; i < input.v3l.Count; i++)
            {
                softAssert(input.v3l[i].x == example.v3l[i].x, "[Vec3].x");
                softAssert(input.v3l[i].y == example.v3l[i].y, "[Vec3].y");
                softAssert(input.v3l[i].z == example.v3l[i].z, "[Vec3].z");
            }
            softAssert(input.cl.Count == example.cl.Count, "[Color].length");
            for (int i = 0; i < input.cl.Count; i++)
            {
                softAssert(input.cl[i].r == example.cl[i].r, "[Color].r");
                softAssert(input.cl[i].g == example.cl[i].g, "[Color].g");
                softAssert(input.cl[i].b == example.cl[i].b, "[Color].b");
            }
            softAssert(input.cx.identifier == example.cx.identifier, "ComplexData.identifier");
            softAssert(input.cx.label == example.cx.label, "ComplexData.label");
            softAssert(input.cx.backgroundColor.r == example.cx.backgroundColor.r, "ComplexData.backgroundColor.r");
            softAssert(input.cx.backgroundColor.g == example.cx.backgroundColor.g, "ComplexData.backgroundColor.g");
            softAssert(input.cx.backgroundColor.b == example.cx.backgroundColor.b, "ComplexData.backgroundColor.b");
            softAssert(input.cx.textColor.r == example.cx.textColor.r, "ComplexData.textColor.r");
            softAssert(input.cx.textColor.g == example.cx.textColor.g, "ComplexData.textColor.g");
            softAssert(input.cx.textColor.b == example.cx.textColor.b, "ComplexData.textColor.b");
            softAssert(input.cx.spectrum.Count == example.cx.spectrum.Count, "ComplexData.spectrum.length");
            for (int i = 0; i < input.cx.spectrum.Count; i++)
            {
                softAssert(input.cx.spectrum[i].r == example.cx.spectrum[i].r, "ComplexData.spectrum.r");
                softAssert(input.cx.spectrum[i].g == example.cx.spectrum[i].g, "ComplexData.spectrum.g");
                softAssert(input.cx.spectrum[i].b == example.cx.spectrum[i].b, "ComplexData.spectrum.b");
            }
            softAssert(input.cxl.Count == example.cxl.Count, "[ComplexData].length");
            for (int i=0; i < input.cxl.Count; i++)
            {
                softAssert(input.cxl[i].identifier == example.cxl[i].identifier, "[ComplexData].identifier");
                softAssert(input.cxl[i].label == example.cxl[i].label, "[ComplexData].label");
                softAssert(input.cxl[i].backgroundColor.r == example.cxl[i].backgroundColor.r, "[ComplexData].backgroundColor.r");
                softAssert(input.cxl[i].backgroundColor.g == example.cxl[i].backgroundColor.g, "[ComplexData].backgroundColor.g");
                softAssert(input.cxl[i].backgroundColor.b == example.cxl[i].backgroundColor.b, "[ComplexData].backgroundColor.b");
                softAssert(input.cxl[i].textColor.r == example.cxl[i].textColor.r, "[ComplexData].textColor.r");
                softAssert(input.cxl[i].textColor.g == example.cxl[i].textColor.g, "[ComplexData].textColor.g");
                softAssert(input.cxl[i].textColor.b == example.cxl[i].textColor.b, "[ComplexData].textColor.b");
                softAssert(input.cxl[i].spectrum.Count == example.cxl[i].spectrum.Count, "[ComplexData].spectrum.length");
                for (int j = 0; j < input.cxl[i].spectrum.Count; j++)
                {
                    softAssert(input.cxl[i].spectrum[j].r == example.cxl[i].spectrum[j].r, "[ComplexData].spectrum.r");
                    softAssert(input.cxl[i].spectrum[j].g == example.cxl[i].spectrum[j].g, "[ComplexData].spectrum.g");
                    softAssert(input.cxl[i].spectrum[j].b == example.cxl[i].spectrum[j].b, "[ComplexData].spectrum.b");
                }
            }
        }


        check();
    }
}
