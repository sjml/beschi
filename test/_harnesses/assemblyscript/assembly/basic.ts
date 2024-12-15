import * as harness from "./_harness";
export * from "./_harness";

import * as ComprehensiveMessage from '../../../../out/generated/assemblyscript/ComprehensiveMessage';

const example = new ComprehensiveMessage.TestingMessage();
example.b = 250;
example.tf = true;
example.i16 = -32000;
example.ui16 = 65000;
example.i32 = -2000000000;
example.ui32 = 4000000000;
example.i64 = -9000000000000000000;
example.ui64 = 18000000000000000000;
example.f = 3.1415927410125732421875;
example.d = 2.718281828459045090795598298427648842334747314453125;
example.ee = ComprehensiveMessage.Enumerated.Beta;
example.es = ComprehensiveMessage.Specified.Negative;
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
example.il = [-1000, 500, 0, 750, 2000];
example.el = [
    ComprehensiveMessage.Specified.Negative,
    ComprehensiveMessage.Specified.Negative,
    ComprehensiveMessage.Specified.Positive,
    ComprehensiveMessage.Specified.Zero,
    ComprehensiveMessage.Specified.Positive,
    ComprehensiveMessage.Specified.Zero
],
example.sl = [
    "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
    "Quisque est eros, placerat ut libero ut, pellentesque tincidunt sem.",
    "Vivamus pellentesque turpis aliquet pretium tincidunt.",
    "Nulla facilisi.",
    "🐼❤️✝️",
    "用ねぼ雪入文モ段足リフケ報通ンさーを応細めい気川ヤセ車不古6治ニフサコ悩段をご青止ぽっ期年ト量報驚テルユ役1家埋詰軟きぎ。",
    "لآخر نشجب ونستنكر هؤلاء الرجال المفتونون بنشوة اللحظة الهائمون في رغبات",
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
example.cx = new ComprehensiveMessage.ComplexData();
example.cx.identifier = 127;
example.cx.label = "ComplexDataObject";
example.cx.backgroundColor = c1;
example.cx.textColor = c2;
example.cx.spectrum = [c3, c2, c1];
example.cx.ranges = [
    ComprehensiveMessage.Specified.Negative,
    ComprehensiveMessage.Specified.Positive,
];
const cx1 = new ComprehensiveMessage.ComplexData();
cx1.identifier = 255;
cx1.label = "Complex1";
cx1.backgroundColor = c3;
cx1.textColor = c1;
cx1.spectrum = [c3, c2, c1, c2, c3];
cx1.ranges = [
    ComprehensiveMessage.Specified.Zero,
    ComprehensiveMessage.Specified.Positive,
];
const cx2 = new ComprehensiveMessage.ComplexData();
cx2.identifier = 63;
cx2.label = "Complex2";
cx2.backgroundColor = c1;
cx2.textColor = c3;
cx2.spectrum = [c1, c2, c3, c2, c1];
cx2.ranges = [
    ComprehensiveMessage.Specified.Negative,
    ComprehensiveMessage.Specified.Zero,
];
example.cxl = [cx1, cx2];

export function generate(): usize {
    const byteLen = example.getSizeInBytes();
    harness.allocate(byteLen);
    const dv = harness.getDataView();
    example.writeBytes(dv, false);

    harness.softAssert(byteLen == 956, "size calculation check");

    return harness.getDataPtr();
}

export function read(): void {
    const dv = harness.getDataView();
    const input = ComprehensiveMessage.TestingMessage.fromBytes(dv)!;

    harness.softAssert(input.b == example.b, "byte");
    harness.softAssert(input.tf == example.tf, "bool");
    harness.softAssert(input.i16 == example.i16, "i16");
    harness.softAssert(input.ui16 == example.ui16, "ui16");
    harness.softAssert(input.i32 == example.i32, "i32");
    harness.softAssert(input.ui32 == example.ui32, "ui32");
    harness.softAssert(input.i64 == example.i64, "i64");
    harness.softAssert(input.ui64 == example.ui64, "ui64");
    harness.softAssert(input.f == Math.fround(example.f), "float");
    harness.softAssert(input.d == example.d, "double");
    harness.softAssert(input.ee == example.ee, "enumerated");
    harness.softAssert(input.es == example.es, "specified");
    harness.softAssert(input.s == example.s, "string");
    harness.softAssert(input.v2.x == Math.fround(example.v2.x), "Vec2.x");
    harness.softAssert(input.v2.y == Math.fround(example.v2.y), "Vec2.y");
    harness.softAssert(input.v3.x == Math.fround(example.v3.x), "Vec3.x");
    harness.softAssert(input.v3.y == Math.fround(example.v3.y), "Vec3.y");
    harness.softAssert(input.v3.z == Math.fround(example.v3.z), "Vec3.z");
    harness.softAssert(input.c.r == Math.fround(example.c.r), "Color.r");
    harness.softAssert(input.c.g == Math.fround(example.c.g), "Color.g");
    harness.softAssert(input.c.b == Math.fround(example.c.b), "Color.b");
    harness.softAssert(input.il.length == example.il.length, "[int16].length");
    for (let i = 0; i < input.il.length; i++) {
        harness.softAssert(input.il[i] == example.il[i], "[int16]");
    }
    harness.softAssert(input.el.length == example.el.length, "[Specified].length");
    for (let i = 0; i < input.el.length; i++) {
        harness.softAssert(input.el[i] == example.el[i], "[Specified]");
    }
    harness.softAssert(input.sl.length == example.sl.length, "[string].length");
    for (let i = 0; i < input.sl.length; i++) {
        harness.softAssert(input.sl[i] == example.sl[i], "[string]");
    }
    harness.softAssert(input.v2l.length == example.v2l.length, "[Vec2].length");
    for (let i = 0; i < input.v2l.length; i++) {
        harness.softAssert(input.v2l[i].x == example.v2l[i].x, "[Vec2].x");
        harness.softAssert(input.v2l[i].y == example.v2l[i].y, "[Vec2].y");
    }
    harness.softAssert(input.v3l.length == example.v3l.length, "[Vec3].length");
    for (let i = 0; i < input.v3l.length; i++) {
        harness.softAssert(input.v3l[i].x == example.v3l[i].x, "[Vec3].x");
        harness.softAssert(input.v3l[i].y == example.v3l[i].y, "[Vec3].y");
        harness.softAssert(input.v3l[i].z == example.v3l[i].z, "[Vec3].z");
    }
    harness.softAssert(input.cl.length == example.cl.length, "[Color].length");
    for (let i = 0; i < input.cl.length; i++) {
        harness.softAssert(input.cl[i].r == example.cl[i].r, "[Color].r");
        harness.softAssert(input.cl[i].g == example.cl[i].g, "[Color].g");
        harness.softAssert(input.cl[i].b == example.cl[i].b, "[Color].b");
    }
    harness.softAssert(input.cx.identifier == example.cx.identifier, "ComplexData.identifier");
    harness.softAssert(input.cx.label == example.cx.label, "ComplexData.label");
    harness.softAssert(input.cx.backgroundColor.r == Math.fround(example.cx.backgroundColor.r), "ComplexData.backgroundColor.r");
    harness.softAssert(input.cx.backgroundColor.g == Math.fround(example.cx.backgroundColor.g), "ComplexData.backgroundColor.g");
    harness.softAssert(input.cx.backgroundColor.b == Math.fround(example.cx.backgroundColor.b), "ComplexData.backgroundColor.b");
    harness.softAssert(input.cx.textColor.r == Math.fround(example.cx.textColor.r), "ComplexData.textColor.r");
    harness.softAssert(input.cx.textColor.g == Math.fround(example.cx.textColor.g), "ComplexData.textColor.g");
    harness.softAssert(input.cx.textColor.b == Math.fround(example.cx.textColor.b), "ComplexData.textColor.b");
    harness.softAssert(input.cx.spectrum.length == example.cx.spectrum.length, "ComplexData.spectrum.length");
    for (let i = 0; i < input.cx.spectrum.length; i++) {
        harness.softAssert(input.cx.spectrum[i].r == Math.fround(example.cx.spectrum[i].r), "ComplexData.spectrum.r");
        harness.softAssert(input.cx.spectrum[i].g == Math.fround(example.cx.spectrum[i].g), "ComplexData.spectrum.g");
        harness.softAssert(input.cx.spectrum[i].b == Math.fround(example.cx.spectrum[i].b), "ComplexData.spectrum.b");
    }
    harness.softAssert(input.cx.ranges.length == example.cx.ranges.length, "ComplexData.ranges.length");
    for (let i = 0; i < input.cx.ranges.length; i++) {
        harness.softAssert(input.cx.ranges[i] == Math.fround(example.cx.ranges[i]), "ComplexData.spectrum");
    }
    harness.softAssert(input.cxl.length == example.cxl.length, "[ComplexData].length");
    for (let i=0; i < input.cxl.length; i++) {
        harness.softAssert(input.cxl[i].identifier == example.cxl[i].identifier, "[ComplexData].identifier");
        harness.softAssert(input.cxl[i].label == example.cxl[i].label, "[ComplexData].label");
        harness.softAssert(input.cxl[i].backgroundColor.r == example.cxl[i].backgroundColor.r, "[ComplexData].backgroundColor.r");
        harness.softAssert(input.cxl[i].backgroundColor.g == example.cxl[i].backgroundColor.g, "[ComplexData].backgroundColor.g");
        harness.softAssert(input.cxl[i].backgroundColor.b == example.cxl[i].backgroundColor.b, "[ComplexData].backgroundColor.b");
        harness.softAssert(input.cxl[i].textColor.r == example.cxl[i].textColor.r, "[ComplexData].textColor.r");
        harness.softAssert(input.cxl[i].textColor.g == example.cxl[i].textColor.g, "[ComplexData].textColor.g");
        harness.softAssert(input.cxl[i].textColor.b == example.cxl[i].textColor.b, "[ComplexData].textColor.b");
        harness.softAssert(input.cxl[i].spectrum.length == example.cxl[i].spectrum.length, "[ComplexData].spectrum.length");
        for (let j = 0; j < input.cxl[i].spectrum.length; j++) {
            harness.softAssert(input.cxl[i].spectrum[j].r == example.cxl[i].spectrum[j].r, "[ComplexData].spectrum.r");
            harness.softAssert(input.cxl[i].spectrum[j].g == example.cxl[i].spectrum[j].g, "[ComplexData].spectrum.g");
            harness.softAssert(input.cxl[i].spectrum[j].b == example.cxl[i].spectrum[j].b, "[ComplexData].spectrum.b");
        }
        harness.softAssert(input.cxl[i].ranges.length == example.cxl[i].ranges.length, "[ComplexData].ranges.length");
        for (let j = 0; j < input.cxl[i].ranges.length; j++) {
            harness.softAssert(input.cxl[i].ranges[j] == example.cxl[i].ranges[j], "[ComplexData].ranges");
        }
    }
}
