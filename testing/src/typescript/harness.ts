import * as fs from 'fs';

import { WireMessage } from './WireMessage';

const example = new WireMessage.TestingMessage();
example.b = 250;
example.tf = true;
example.i16 = -32000;
example.ui16 = 65000;
example.i32 = -2000000000;
example.ui32 = 4000000000;
example.f = 3.1415927410125732421875;
example.d = 2.718281828459045090795598298427648842334747314453125;
example.s = "Lorem ipsum dolor sit amet, consectetur adipiscing elit.";
example.v2 = new WireMessage.Vec2();
example.v2.x = 256.512;
example.v2.y = 1024.768;
example.v3 = new WireMessage.Vec3();
example.v3.x = 128.64;
example.v3.y = 2048.4096;
example.v3.z = 16.32;
example.c = new WireMessage.Color();
example.c.r = 255;
example.c.g = 128;
example.c.b = 0;
example.sl = [
    "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
    "Quisque est eros, placerat ut libero ut, pellentesque tincidunt sem.",
    "Vivamus pellentesque turpis aliquet pretium tincidunt.",
    "Nulla facilisi.",
    "🐼❤️✝️"
];
const v21 = new WireMessage.Vec2();
v21.x = 10.0;
v21.y = 15.0;
const v22 = new WireMessage.Vec2();
v22.x = 20.0;
v22.y = 25.0;
const v23 = new WireMessage.Vec2();
v23.x = 30.0;
v23.y = 35.0;
const v24 = new WireMessage.Vec2();
v24.x = 40.0;
v24.y = 45.0;
example.v2l = [
    v21, v22, v23, v24
];
const v31 = new WireMessage.Vec3();
v31.x = 10.0;
v31.y = 15.0;
v31.z = 17.5;
const v32 = new WireMessage.Vec3();
v32.x = 20.0;
v32.y = 25.0;
v32.z = 27.5;
const v33 = new WireMessage.Vec3();
v33.x = 30.0;
v33.y = 35.0;
v33.z = 37.5;
const v34 = new WireMessage.Vec3();
v34.x = 40.0;
v34.y = 45.0;
v34.z = 47.5;
example.v3l = [
    v31, v32, v33, v34
];
const c1 = new WireMessage.Color();
c1.r = 255;
c1.g = 0;
c1.b = 0;
const c2 = new WireMessage.Color();
c2.r = 0;
c2.g = 255;
c2.b = 0;
const c3 = new WireMessage.Color();
c3.r = 0;
c3.g = 0;
c3.b = 255;
example.cl = [
    c1, c2, c3
];

// soft assertion; just prints errors and keeps going
function assert(condition: boolean, label: string) {
    if (!condition) {
        console.error("FAILED! " + label);
    }
}

if (process.argv.includes('--generate')) {
    const data = new ArrayBuffer(1024);
    const dv = new DataView(data);
    const offset = example.WriteBytes(dv, 0);
    fs.writeFileSync('../../data/test.typescript.msg', Buffer.from(data, 0, offset));
}
else if (process.argv.includes('--read')) {
    fs.readFile('../../data/test.typescript.msg', (_, data) => {
        const dv = new DataView(data.buffer);
        const input = WireMessage.TestingMessage.FromBytes(dv, 0).val;

        assert(input.b == example.b, "byte");
        assert(input.tf == example.tf, "bool");
        assert(input.i16 == example.i16, "i16");
        assert(input.ui16 == example.ui16, "ui16");
        assert(input.i32 == example.i32, "i32");
        assert(input.ui32 == example.ui32, "ui32");
        assert(Math.fround(input.f) == Math.fround(example.f), "float");
        assert(input.d == example.d, "double");
        assert(input.s == example.s, "string");
        assert(Math.fround(input.v2.x) == Math.fround(example.v2.x), "Vec2.x");
        assert(Math.fround(input.v2.y) == Math.fround(example.v2.y), "Vec2.y");
        assert(Math.fround(input.v3.x) == Math.fround(example.v3.x), "Vec3.x");
        assert(Math.fround(input.v3.y) == Math.fround(example.v3.y), "Vec3.y");
        assert(Math.fround(input.v3.z) == Math.fround(example.v3.z), "Vec3.z");
        assert(Math.fround(input.c.r) == Math.fround(example.c.r), "Color.r");
        assert(Math.fround(input.c.g) == Math.fround(example.c.g), "Color.g");
        assert(Math.fround(input.c.b) == Math.fround(example.c.b), "Color.b");
        assert(input.sl.length == example.sl.length, "[string].length");
        for (let i = 0; i < input.sl.length; i++)
        {
            assert(input.sl[i] == example.sl[i], "[string]");
        }
        assert(input.v2l.length == example.v2l.length, "[Vec2].length");
        for (let i = 0; i < input.v2l.length; i++)
        {
            assert(input.v2l[i].x == example.v2l[i].x, "[Vec2].x");
            assert(input.v2l[i].y == example.v2l[i].y, "[Vec2].y");
        }
        assert(input.v3l.length == example.v3l.length, "[Vec3].length");
        for (let i = 0; i < input.v3l.length; i++)
        {
            assert(input.v3l[i].x == example.v3l[i].x, "[Vec3].x");
            assert(input.v3l[i].y == example.v3l[i].y, "[Vec3].y");
            assert(input.v3l[i].z == example.v3l[i].z, "[Vec3].z");
        }
        assert(input.cl.length == example.cl.length, "[Color].length");
        for (let i = 0; i < input.cl.length; i++)
        {
            assert(input.cl[i].r == example.cl[i].r, "[Color].r");
            assert(input.cl[i].g == example.cl[i].g, "[Color].g");
            assert(input.cl[i].b == example.cl[i].b, "[Color].b");
        }
    });
}


