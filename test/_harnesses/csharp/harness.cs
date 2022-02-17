using System;
using System.IO;
using System.Collections.Generic;

using WireMessage;

class ProtocolHarness {

    static bool OK;
    static void softAssert(bool condition, string label)
    {
        if (!condition)
        {
            Console.Error.WriteLine("FAILED! " + label);
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
        WireMessage.TestingMessage example = new WireMessage.TestingMessage();
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
        example.v2 = new WireMessage.Vec2();
        example.v2.x = 256.512f;
        example.v2.y = 1024.768f;
        example.v3 = new WireMessage.Vec3();
        example.v3.x = 128.64f;
        example.v3.y = 2048.4096f;
        example.v3.z = 16.32f;
        example.c = new WireMessage.Color();
        example.c.r = 255;
        example.c.g = 128;
        example.c.b = 0;
        example.sl = new string[] {
            "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
            "Quisque est eros, placerat ut libero ut, pellentesque tincidunt sem.",
            "Vivamus pellentesque turpis aliquet pretium tincidunt.",
            "Nulla facilisi.",
            "🐼❤️✝️",
        };
        WireMessage.Vec2 v21 = new WireMessage.Vec2();
        v21.x = 10.0f;
        v21.y = 15.0f;
        WireMessage.Vec2 v22 = new WireMessage.Vec2();
        v22.x = 20.0f;
        v22.y = 25.0f;
        WireMessage.Vec2 v23 = new WireMessage.Vec2();
        v23.x = 30.0f;
        v23.y = 35.0f;
        WireMessage.Vec2 v24 = new WireMessage.Vec2();
        v24.x = 40.0f;
        v24.y = 45.0f;
        example.v2l = new WireMessage.Vec2[] {
            v21, v22, v23, v24
        };
        WireMessage.Vec3 v31 = new WireMessage.Vec3();
        v31.x = 10.0f;
        v31.y = 15.0f;
        v31.z = 17.5f;
        WireMessage.Vec3 v32 = new WireMessage.Vec3();
        v32.x = 20.0f;
        v32.y = 25.0f;
        v32.z = 27.5f;
        WireMessage.Vec3 v33 = new WireMessage.Vec3();
        v33.x = 30.0f;
        v33.y = 35.0f;
        v33.z = 37.5f;
        WireMessage.Vec3 v34 = new WireMessage.Vec3();
        v34.x = 40.0f;
        v34.y = 45.0f;
        v34.z = 47.5f;
        example.v3l = new WireMessage.Vec3[] {
            v31, v32, v33, v34
        };
        WireMessage.Color c1 = new WireMessage.Color();
        c1.r = 255;
        c1.g = 0;
        c1.b = 0;
        WireMessage.Color c2 = new WireMessage.Color();
        c2.r = 0;
        c2.g = 255;
        c2.b = 0;
        WireMessage.Color c3 = new WireMessage.Color();
        c3.r = 0;
        c3.g = 0;
        c3.b = 255;
        example.cl = new WireMessage.Color[] {
            c1, c2, c3
        };

        Dictionary<string, string> parsed = parseArguments(args);

        if (parsed.ContainsKey("generate"))
        {
            string outPath = parsed["generate"];
            string outDir = System.IO.Path.GetDirectoryName(outPath);
            System.IO.Directory.CreateDirectory(outDir);
            FileStream f = new FileStream(outPath, FileMode.Create);
            BinaryWriter bw = new BinaryWriter(f);
            example.WriteBytes(bw);
        }
        else if (parsed.ContainsKey("read"))
        {
            FileStream f = File.OpenRead(parsed["read"]);
            BinaryReader br = new BinaryReader(f);
            WireMessage.TestingMessage input = WireMessage.TestingMessage.FromBytes(br);

            OK = true;
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

            if (!OK)
            {
                Console.Error.WriteLine("Failed assertions.");
                Environment.Exit(1);
            }
        }
    }
}
