using System;
using System.IO;

using WireMessage;

class ProtocolHarness {
    static void assert(bool condition, string label)
    {
        if (!condition)
        {
            Console.Error.WriteLine("FAILED! " + label);
        }
    }

    static void Main(string[] args) {
        WireMessage.TestingMessage example = new WireMessage.TestingMessage();
        example.b = 250;
        example.tf = true;
        example.i16 = -32000;
        example.ui16 = 65000;
        example.i32 = -2000000000;
        example.ui32 = 4000000000;
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

        if (Array.IndexOf(args, "--generate") >= 0)
        {
            FileStream f = new FileStream("../../data/test.csharp.msg", FileMode.Create);
            BinaryWriter bw = new BinaryWriter(f);
            example.WriteBytes(bw);
        }
        else if (Array.IndexOf(args, "--read") >= 0)
        {
            FileStream f = File.OpenRead("../../data/test.csharp.msg");
            BinaryReader br = new BinaryReader(f);
            WireMessage.TestingMessage input = WireMessage.TestingMessage.FromBytes(br);

            assert(input.b == example.b, "byte");
            assert(input.tf == example.tf, "bool");
            assert(input.i16 == example.i16, "i16");
            assert(input.ui16 == example.ui16, "ui16");
            assert(input.i32 == example.i32, "i32");
            assert(input.ui32 == example.ui32, "ui32");
            assert(input.f == example.f, "float");
            assert(input.d == example.d, "double");
            assert(input.s == example.s, "string");
            assert(input.v2.x == example.v2.x, "Vec2");
            assert(input.v2.y == example.v2.y, "Vec2");
            assert(input.v3.x == example.v3.x, "Vec3");
            assert(input.v3.y == example.v3.y, "Vec3");
            assert(input.v3.z == example.v3.z, "Vec3");
            assert(input.c.r == example.c.r, "Color");
            assert(input.c.g == example.c.g, "Color");
            assert(input.c.b == example.c.b, "Color");
            assert(input.sl.Length == example.sl.Length, "[string].length");
            for (int i = 0; i < input.sl.Length; i++)
            {
                assert(input.sl[i] == example.sl[i], "[string]");
            }
            assert(input.v2l.Length == example.v2l.Length, "[Vec2].length");
            for (int i = 0; i < input.v2l.Length; i++)
            {
                assert(input.v2l[i].x == example.v2l[i].x, "[Vec2].x");
                assert(input.v2l[i].y == example.v2l[i].y, "[Vec2].y");
            }
            assert(input.v3l.Length == example.v3l.Length, "[Vec3].length");
            for (int i = 0; i < input.v3l.Length; i++)
            {
                assert(input.v3l[i].x == example.v3l[i].x, "[Vec3].x");
                assert(input.v3l[i].y == example.v3l[i].y, "[Vec3].y");
                assert(input.v3l[i].z == example.v3l[i].z, "[Vec3].z");
            }
            assert(input.cl.Length == example.cl.Length, "[Color].length");
            for (int i = 0; i < input.cl.Length; i++)
            {
                assert(input.cl[i].r == example.cl[i].r, "[Color].r");
                assert(input.cl[i].g == example.cl[i].g, "[Color].g");
                assert(input.cl[i].b == example.cl[i].b, "[Color].b");
            }
        }
    }
}
