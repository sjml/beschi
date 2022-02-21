using System;
using System.IO;

using ComprehensiveMessage;

class BasicHarness: TestHarness {

    static void Main(string[] args) {
        var example = new ComprehensiveMessage.TestingMessage();
        example.b = 250;
        example.tf = true;
        example.i16 = -32000;
        example.ui16 = 65000;
        example.i32 = -2000000000;
        example.ui32 = 4000000000;
        example.i64 = -9000000000000000000;
        example.ui64 = 18000000000000000000;
        example.f = 3.1415927410125732421875f;
        example.d = 2.718281828459045090795598298427648842334747314453125;
        example.s = "Lorem ipsum dolor sit amet, consectetur adipiscing elit.";
        example.v2 = new ComprehensiveMessage.Vec2();
        example.v2.x = 256.512f;
        example.v2.y = 1024.768f;
        example.v3 = new ComprehensiveMessage.Vec3();
        example.v3.x = 128.64f;
        example.v3.y = 2048.4096f;
        example.v3.z = 16.32f;
        example.c = new ComprehensiveMessage.Color();
        example.c.r = 255;
        example.c.g = 128;
        example.c.b = 0;
        example.sl = new string[] {
            "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
            "Quisque est eros, placerat ut libero ut, pellentesque tincidunt sem.",
            "Vivamus pellentesque turpis aliquet pretium tincidunt.",
            "Nulla facilisi.",
            "🐼❤️✝️",
            "用ねぼ雪入文モ段足リフケ報通ンさーを応細めい気川ヤセ車不古6治ニフサコ悩段をご青止ぽっ期年ト量報驚テルユ役1家埋詰軟きぎ。",
            "لآخر نشجب ونستنكر هؤلاء الرجال المفتونون بنشوة اللحظة الهائمون في رغبات",
        };
        var v21 = new ComprehensiveMessage.Vec2();
        v21.x = 10.0f;
        v21.y = 15.0f;
        var v22 = new ComprehensiveMessage.Vec2();
        v22.x = 20.0f;
        v22.y = 25.0f;
        var v23 = new ComprehensiveMessage.Vec2();
        v23.x = 30.0f;
        v23.y = 35.0f;
        var v24 = new ComprehensiveMessage.Vec2();
        v24.x = 40.0f;
        v24.y = 45.0f;
        example.v2l = new ComprehensiveMessage.Vec2[] {
            v21, v22, v23, v24
        };
        var v31 = new ComprehensiveMessage.Vec3();
        v31.x = 10.0f;
        v31.y = 15.0f;
        v31.z = 17.5f;
        var v32 = new ComprehensiveMessage.Vec3();
        v32.x = 20.0f;
        v32.y = 25.0f;
        v32.z = 27.5f;
        var v33 = new ComprehensiveMessage.Vec3();
        v33.x = 30.0f;
        v33.y = 35.0f;
        v33.z = 37.5f;
        var v34 = new ComprehensiveMessage.Vec3();
        v34.x = 40.0f;
        v34.y = 45.0f;
        v34.z = 47.5f;
        example.v3l = new ComprehensiveMessage.Vec3[] {
            v31, v32, v33, v34
        };
        var c1 = new ComprehensiveMessage.Color();
        c1.r = 255;
        c1.g = 0;
        c1.b = 0;
        var c2 = new ComprehensiveMessage.Color();
        c2.r = 0;
        c2.g = 255;
        c2.b = 0;
        var c3 = new ComprehensiveMessage.Color();
        c3.r = 0;
        c3.g = 0;
        c3.b = 255;
        example.cl = new ComprehensiveMessage.Color[] {
            c1, c2, c3
        };
        example.cx = new ComprehensiveMessage.ComplexData();
        example.cx.identifier = 127;
        example.cx.label = "ComplexDataObject";
        example.cx.backgroundColor = c1;
        example.cx.textColor = c2;
        example.cx.spectrum = new ComprehensiveMessage.Color[] {
            c3, c2, c1
        };
        var cx1 = new ComprehensiveMessage.ComplexData();
        cx1.identifier = 255;
        cx1.label = "Complex1";
        cx1.backgroundColor = c3;
        cx1.textColor = c1;
        cx1.spectrum = new ComprehensiveMessage.Color[] {c3, c2, c1, c2, c3};
        var cx2 = new ComprehensiveMessage.ComplexData();
        cx2.identifier = 63;
        cx2.label = "Complex2";
        cx2.backgroundColor = c1;
        cx2.textColor = c3;
        cx2.spectrum = new ComprehensiveMessage.Color[] {c1, c2, c3, c2, c1};
        example.cxl = new ComprehensiveMessage.ComplexData[] {cx1, cx2};

        var parsedArgs = parseArguments(args);

        if (parsedArgs.ContainsKey("generate"))
        {
            string outPath = parsedArgs["generate"];
            string outDir = System.IO.Path.GetDirectoryName(outPath);
            System.IO.Directory.CreateDirectory(outDir);
            FileStream f = new FileStream(outPath, FileMode.Create);
            BinaryWriter bw = new BinaryWriter(f);
            example.WriteBytes(bw, false);

            softAssert(example.GetSizeInBytes() == 899, "size calculation check");
            softAssert(example.GetSizeInBytes() == bw.BaseStream.Position, "written bytes check");
        }
        else if (parsedArgs.ContainsKey("read"))
        {
            FileStream f = File.OpenRead(parsedArgs["read"]);
            BinaryReader br = new BinaryReader(f);
            ComprehensiveMessage.TestingMessage input = ComprehensiveMessage.TestingMessage.FromBytes(br);
            softAssert(example != null, "parsing test message");

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
            softAssert(input.sl.Length == example.sl.Length, "[string].length");
            for (int i = 0; i < input.sl.Length; i++)
            {
                softAssert(input.sl[i] == example.sl[i], "[string]");
            }
            softAssert(input.v2l.Length == example.v2l.Length, "[Vec2].length");
            for (int i = 0; i < input.v2l.Length; i++)
            {
                softAssert(input.v2l[i].x == example.v2l[i].x, "[Vec2].x");
                softAssert(input.v2l[i].y == example.v2l[i].y, "[Vec2].y");
            }
            softAssert(input.v3l.Length == example.v3l.Length, "[Vec3].length");
            for (int i = 0; i < input.v3l.Length; i++)
            {
                softAssert(input.v3l[i].x == example.v3l[i].x, "[Vec3].x");
                softAssert(input.v3l[i].y == example.v3l[i].y, "[Vec3].y");
                softAssert(input.v3l[i].z == example.v3l[i].z, "[Vec3].z");
            }
            softAssert(input.cl.Length == example.cl.Length, "[Color].length");
            for (int i = 0; i < input.cl.Length; i++)
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
            softAssert(input.cx.spectrum.Length == example.cx.spectrum.Length, "ComplexData.spectrum.length");
            for (int i = 0; i < input.cx.spectrum.Length; i++)
            {
                softAssert(input.cx.spectrum[i].r == example.cx.spectrum[i].r, "ComplexData.spectrum.r");
                softAssert(input.cx.spectrum[i].g == example.cx.spectrum[i].g, "ComplexData.spectrum.g");
                softAssert(input.cx.spectrum[i].b == example.cx.spectrum[i].b, "ComplexData.spectrum.b");
            }
        }


        check();
    }
}
