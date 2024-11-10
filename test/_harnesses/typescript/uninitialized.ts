import { getDataView, writeBuffer, runTest } from "./util";

import * as ComprehensiveMessage from '../../../out/generated/typescript/ComprehensiveMessage';

const example = new ComprehensiveMessage.TestingMessage();


function generate(filePath: string, softAssert: (condition: boolean, label: string) => void) {
    const data = new ArrayBuffer(example.getSizeInBytes());
    const da = new ComprehensiveMessage.DataAccess(data);
    example.writeBytes(da, false);

    writeBuffer(Buffer.from(data, 0, da.currentOffset), filePath);
}

function read(filePath: string, softAssert: (condition: boolean, label: string) => void) {
    const dv = getDataView(filePath);
    const input = ComprehensiveMessage.TestingMessage.fromBytes(dv);
    softAssert(input != null, "parsing test message");

    softAssert(input.b == example.b, "byte");
    softAssert(input.tf == example.tf, "bool");
    softAssert(input.i16 == example.i16, "i16");
    softAssert(input.ui16 == example.ui16, "ui16");
    softAssert(input.i32 == example.i32, "i32");
    softAssert(input.ui32 == example.ui32, "ui32");
    softAssert(input.i64 == example.i64, "i64");
    softAssert(input.ui64 == example.ui64, "ui64");
    softAssert(input.f == Math.fround(example.f), "float");
    softAssert(input.d == example.d, "double");
    softAssert(input.s == example.s, "string");
    softAssert(input.v2.x == Math.fround(example.v2.x), "Vec2.x");
    softAssert(input.v2.y == Math.fround(example.v2.y), "Vec2.y");
    softAssert(input.v3.x == Math.fround(example.v3.x), "Vec3.x");
    softAssert(input.v3.y == Math.fround(example.v3.y), "Vec3.y");
    softAssert(input.v3.z == Math.fround(example.v3.z), "Vec3.z");
    softAssert(input.c.r == Math.fround(example.c.r), "Color.r");
    softAssert(input.c.g == Math.fround(example.c.g), "Color.g");
    softAssert(input.c.b == Math.fround(example.c.b), "Color.b");
    softAssert(input.sl.length == example.sl.length, "[string].length");
    for (let i = 0; i < input.sl.length; i++) {
        softAssert(input.sl[i] == example.sl[i], "[string]");
    }
    softAssert(input.v2l.length == example.v2l.length, "[Vec2].length");
    for (let i = 0; i < input.v2l.length; i++) {
        softAssert(input.v2l[i].x == example.v2l[i].x, "[Vec2].x");
        softAssert(input.v2l[i].y == example.v2l[i].y, "[Vec2].y");
    }
    softAssert(input.v3l.length == example.v3l.length, "[Vec3].length");
    for (let i = 0; i < input.v3l.length; i++) {
        softAssert(input.v3l[i].x == example.v3l[i].x, "[Vec3].x");
        softAssert(input.v3l[i].y == example.v3l[i].y, "[Vec3].y");
        softAssert(input.v3l[i].z == example.v3l[i].z, "[Vec3].z");
    }
    softAssert(input.cl.length == example.cl.length, "[Color].length");
    for (let i = 0; i < input.cl.length; i++) {
        softAssert(input.cl[i].r == example.cl[i].r, "[Color].r");
        softAssert(input.cl[i].g == example.cl[i].g, "[Color].g");
        softAssert(input.cl[i].b == example.cl[i].b, "[Color].b");
    }
    softAssert(input.cx.identifier == example.cx.identifier, "ComplexData.identifier");
    softAssert(input.cx.label == example.cx.label, "ComplexData.label");
    softAssert(input.cx.backgroundColor.r == Math.fround(example.cx.backgroundColor.r), "ComplexData.backgroundColor.r");
    softAssert(input.cx.backgroundColor.g == Math.fround(example.cx.backgroundColor.g), "ComplexData.backgroundColor.g");
    softAssert(input.cx.backgroundColor.b == Math.fround(example.cx.backgroundColor.b), "ComplexData.backgroundColor.b");
    softAssert(input.cx.textColor.r == Math.fround(example.cx.textColor.r), "ComplexData.textColor.r");
    softAssert(input.cx.textColor.g == Math.fround(example.cx.textColor.g), "ComplexData.textColor.g");
    softAssert(input.cx.textColor.b == Math.fround(example.cx.textColor.b), "ComplexData.textColor.b");
    softAssert(input.cx.spectrum.length == example.cx.spectrum.length, "ComplexData.spectrum.length");
    for (let i = 0; i < input.cx.spectrum.length; i++) {
        softAssert(input.cx.spectrum[i].r == Math.fround(example.cx.spectrum[i].r), "ComplexData.spectrum.r");
        softAssert(input.cx.spectrum[i].g == Math.fround(example.cx.spectrum[i].g), "ComplexData.spectrum.g");
        softAssert(input.cx.spectrum[i].b == Math.fround(example.cx.spectrum[i].b), "ComplexData.spectrum.b");
    }
    softAssert(input.cxl.length == example.cxl.length, "[ComplexData].length");
    for (let i=0; i < input.cxl.length; i++) {
        softAssert(input.cxl[i].identifier == example.cxl[i].identifier, "[ComplexData].identifier");
        softAssert(input.cxl[i].label == example.cxl[i].label, "[ComplexData].label");
        softAssert(input.cxl[i].backgroundColor.r == example.cxl[i].backgroundColor.r, "[ComplexData].backgroundColor.r");
        softAssert(input.cxl[i].backgroundColor.g == example.cxl[i].backgroundColor.g, "[ComplexData].backgroundColor.g");
        softAssert(input.cxl[i].backgroundColor.b == example.cxl[i].backgroundColor.b, "[ComplexData].backgroundColor.b");
        softAssert(input.cxl[i].textColor.r == example.cxl[i].textColor.r, "[ComplexData].textColor.r");
        softAssert(input.cxl[i].textColor.g == example.cxl[i].textColor.g, "[ComplexData].textColor.g");
        softAssert(input.cxl[i].textColor.b == example.cxl[i].textColor.b, "[ComplexData].textColor.b");
        softAssert(input.cxl[i].spectrum.length == example.cxl[i].spectrum.length, "[ComplexData].spectrum.length");
        for (let j = 0; j < input.cxl[i].spectrum.length; j++) {
            softAssert(input.cxl[i].spectrum[j].r == example.cxl[i].spectrum[j].r, "[ComplexData].spectrum.r");
            softAssert(input.cxl[i].spectrum[j].g == example.cxl[i].spectrum[j].g, "[ComplexData].spectrum.g");
            softAssert(input.cxl[i].spectrum[j].b == example.cxl[i].spectrum[j].b, "[ComplexData].spectrum.b");
        }
    }
}

runTest(generate, read);


