import * as minimist from "minimist";

import { getDataView, writeBuffer } from "./fileUtil";

import * as ComprehensiveMessage from '../../../out/generated/typescript/ComprehensiveMessage';

const example = new ComprehensiveMessage.TestingMessage();
example.b = 250;
example.tf = true;
example.i16 = -32000;
example.ui16 = 65000;
example.i32 = -2000000000;
example.ui32 = 4000000000;
example.i64 = -9000000000000000000n;
example.ui64 = 18000000000000000000n;
example.f = 3.1415927410125732421875;
example.d = 2.718281828459045090795598298427648842334747314453125;
example.s = "Lorem ipsum dolor sit amet, consectetur adipiscing elit.";
example.v2 = new ComprehensiveMessage.Vec2();
example.v2.x = 256.512;
example.v2.y = 1024.768;
example.v3 = new ComprehensiveMessage.Vec3();
example.v3.x = 128.64;
example.v3.y = 2048.4096;
example.v3.z = 16.32;
example.c = new ComprehensiveMessage.Color();
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
const v21 = new ComprehensiveMessage.Vec2();
v21.x = 10.0;
v21.y = 15.0;
const v22 = new ComprehensiveMessage.Vec2();
v22.x = 20.0;
v22.y = 25.0;
const v23 = new ComprehensiveMessage.Vec2();
v23.x = 30.0;
v23.y = 35.0;
const v24 = new ComprehensiveMessage.Vec2();
v24.x = 40.0;
v24.y = 45.0;
example.v2l = [
    v21, v22, v23, v24
];
const v31 = new ComprehensiveMessage.Vec3();
v31.x = 10.0;
v31.y = 15.0;
v31.z = 17.5;
const v32 = new ComprehensiveMessage.Vec3();
v32.x = 20.0;
v32.y = 25.0;
v32.z = 27.5;
const v33 = new ComprehensiveMessage.Vec3();
v33.x = 30.0;
v33.y = 35.0;
v33.z = 37.5;
const v34 = new ComprehensiveMessage.Vec3();
v34.x = 40.0;
v34.y = 45.0;
v34.z = 47.5;
example.v3l = [
    v31, v32, v33, v34
];
const c1 = new ComprehensiveMessage.Color();
c1.r = 255;
c1.g = 0;
c1.b = 0;
const c2 = new ComprehensiveMessage.Color();
c2.r = 0;
c2.g = 255;
c2.b = 0;
const c3 = new ComprehensiveMessage.Color();
c3.r = 0;
c3.g = 0;
c3.b = 255;
example.cl = [
    c1, c2, c3
];
example.complex = new ComprehensiveMessage.ComplexData();
example.complex.identifier = 127;
example.complex.label = "ComplexDataObject";
example.complex.backgroundColor = c1;
example.complex.textColor = c2;
example.complex.spectrum = [c3, c2, c1];

function softAssert(condition: boolean, label: string) {
    if (!condition) {
        console.error("FAILED! TypeScript: " + label);
    }
}

const args = minimist(process.argv.slice(2));

if (args["generate"]) {
    const data = new ArrayBuffer(1024);
    const dv = new DataView(data);
    const offset = example.WriteBytes(dv, 0);

    writeBuffer(Buffer.from(data, 0, offset), args["generate"]);
}
else if (args["read"]) {
    const dv = getDataView(args["read"]);
    const input = ComprehensiveMessage.TestingMessage.FromBytes(dv, 0).val;

    softAssert(input.b == example.b, "byte");
    softAssert(input.tf == example.tf, "bool");
    softAssert(input.i16 == example.i16, "i16");
    softAssert(input.ui16 == example.ui16, "ui16");
    softAssert(input.i32 == example.i32, "i32");
    softAssert(input.ui32 == example.ui32, "ui32");
    softAssert(input.i64 == example.i64, "i64");
    softAssert(input.ui64 == example.ui64, "ui64");
    softAssert(Math.fround(input.f) == Math.fround(example.f), "float");
    softAssert(input.d == example.d, "double");
    softAssert(input.s == example.s, "string");
    softAssert(Math.fround(input.v2.x) == Math.fround(example.v2.x), "Vec2.x");
    softAssert(Math.fround(input.v2.y) == Math.fround(example.v2.y), "Vec2.y");
    softAssert(Math.fround(input.v3.x) == Math.fround(example.v3.x), "Vec3.x");
    softAssert(Math.fround(input.v3.y) == Math.fround(example.v3.y), "Vec3.y");
    softAssert(Math.fround(input.v3.z) == Math.fround(example.v3.z), "Vec3.z");
    softAssert(Math.fround(input.c.r) == Math.fround(example.c.r), "Color.r");
    softAssert(Math.fround(input.c.g) == Math.fround(example.c.g), "Color.g");
    softAssert(Math.fround(input.c.b) == Math.fround(example.c.b), "Color.b");
    softAssert(input.sl.length == example.sl.length, "[string].length");
    for (let i = 0; i < input.sl.length; i++)
    {
        softAssert(input.sl[i] == example.sl[i], "[string]");
    }
    softAssert(input.v2l.length == example.v2l.length, "[Vec2].length");
    for (let i = 0; i < input.v2l.length; i++)
    {
        softAssert(input.v2l[i].x == example.v2l[i].x, "[Vec2].x");
        softAssert(input.v2l[i].y == example.v2l[i].y, "[Vec2].y");
    }
    softAssert(input.v3l.length == example.v3l.length, "[Vec3].length");
    for (let i = 0; i < input.v3l.length; i++)
    {
        softAssert(input.v3l[i].x == example.v3l[i].x, "[Vec3].x");
        softAssert(input.v3l[i].y == example.v3l[i].y, "[Vec3].y");
        softAssert(input.v3l[i].z == example.v3l[i].z, "[Vec3].z");
    }
    softAssert(input.cl.length == example.cl.length, "[Color].length");
    for (let i = 0; i < input.cl.length; i++)
    {
        softAssert(input.cl[i].r == example.cl[i].r, "[Color].r");
        softAssert(input.cl[i].g == example.cl[i].g, "[Color].g");
        softAssert(input.cl[i].b == example.cl[i].b, "[Color].b");
    }
    softAssert(input.complex.identifier == example.complex.identifier, "ComplexData.identifier");
    softAssert(input.complex.label == example.complex.label, "ComplexData.label");
    softAssert(Math.fround(input.complex.backgroundColor.r) == Math.fround(example.complex.backgroundColor.r), "ComplexData.backgroundColor.r");
    softAssert(Math.fround(input.complex.backgroundColor.g) == Math.fround(example.complex.backgroundColor.g), "ComplexData.backgroundColor.g");
    softAssert(Math.fround(input.complex.backgroundColor.b) == Math.fround(example.complex.backgroundColor.b), "ComplexData.backgroundColor.b");
    softAssert(Math.fround(input.complex.textColor.r) == Math.fround(example.complex.textColor.r), "ComplexData.textColor.r");
    softAssert(Math.fround(input.complex.textColor.g) == Math.fround(example.complex.textColor.g), "ComplexData.textColor.g");
    softAssert(Math.fround(input.complex.textColor.b) == Math.fround(example.complex.textColor.b), "ComplexData.textColor.b");
    softAssert(input.complex.spectrum.length == example.complex.spectrum.length, "ComplexData.spectrum.length");
    for (let i = 0; i < input.complex.spectrum.length; i++)
    {
        softAssert(input.complex.spectrum[i].r == example.complex.spectrum[i].r, "ComplexData.spectrum.r");
        softAssert(input.complex.spectrum[i].g == example.complex.spectrum[i].g, "ComplexData.spectrum.g");
        softAssert(input.complex.spectrum[i].b == example.complex.spectrum[i].b, "ComplexData.spectrum.b");
    }
}


