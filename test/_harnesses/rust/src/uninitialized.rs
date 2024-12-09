// message files will include code that's not necessarily called in each test
#![allow(dead_code)]

use std::fs;

mod comprehensive_message;
use comprehensive_message::*;

mod util;

fn main() {
    let mut checker = util::Checker { ok: true };
    let args = util::arg_parse();

    #[allow(clippy::approx_constant)]
    #[allow(clippy::excessive_precision)]
    let example: TestingMessage = Default::default();

    if args.contains_key("generate") {
        let mut writer: Vec<u8> = Vec::new();
        example.write_bytes(&mut writer, false);

        let filename = args.get("generate").unwrap();
        fs::write(filename, writer).unwrap();
    }
    else if args.contains_key("read") {
        let filename = args.get("read").unwrap();
        let buffer = fs::read(&filename).unwrap();
        let mut reader = BufferReader::from_vec(buffer);
        let input = TestingMessage::from_bytes(&mut reader).unwrap();
        checker.soft_assert(input.b == example.b, "byte");
        checker.soft_assert(input.tf == example.tf, "bool");
        checker.soft_assert(input.i16 == example.i16, "i16");
        checker.soft_assert(input.ui16 == example.ui16, "ui16");
        checker.soft_assert(input.i32 == example.i32, "i32");
        checker.soft_assert(input.ui32 == example.ui32, "ui32");
        checker.soft_assert(input.i64 == example.i64, "i64");
        checker.soft_assert(input.ui64 == example.ui64, "ui64");
        checker.soft_assert(input.f == example.f, "float");
        checker.soft_assert(input.d == example.d, "double");
        checker.soft_assert(input.s == example.s, "string");
        checker.soft_assert(input.v2.x == example.v2.x, "Vec2");
        checker.soft_assert(input.v2.y == example.v2.y, "Vec2");
        checker.soft_assert(input.v3.x == example.v3.x, "Vec3");
        checker.soft_assert(input.v3.y == example.v3.y, "Vec3");
        checker.soft_assert(input.v3.z == example.v3.z, "Vec3");
        checker.soft_assert(input.c.r == example.c.r, "Color");
        checker.soft_assert(input.c.g == example.c.g, "Color");
        checker.soft_assert(input.c.b == example.c.b, "Color");
        checker.soft_assert(input.sl.len() == example.sl.len(), "[string].length");
        for i in 0..input.sl.len() {
            checker.soft_assert(input.sl[i] == example.sl[i], "[string]");
        }
        checker.soft_assert(input.v2l.len() == example.v2l.len(), "[Vec2].length");
        for i in 0..input.v2l.len() {
            checker.soft_assert(input.v2l[i].x == example.v2l[i].x, "[Vec2].x");
            checker.soft_assert(input.v2l[i].y == example.v2l[i].y, "[Vec2].y");
        }
        checker.soft_assert(input.v3l.len() == example.v3l.len(), "[Vec3].length");
        for i in 0..input.v3l.len() {
            checker.soft_assert(input.v3l[i].x == example.v3l[i].x, "[Vec3].x");
            checker.soft_assert(input.v3l[i].y == example.v3l[i].y, "[Vec3].y");
            checker.soft_assert(input.v3l[i].z == example.v3l[i].z, "[Vec3].z");
        }
        checker.soft_assert(input.cl.len() == example.cl.len(), "[Color].length");
        for i in 0..input.cl.len() {
            checker.soft_assert(input.cl[i].r == example.cl[i].r, "[Color].r");
            checker.soft_assert(input.cl[i].g == example.cl[i].g, "[Color].g");
            checker.soft_assert(input.cl[i].b == example.cl[i].b, "[Color].b");
        }
        checker.soft_assert(input.cx.identifier == example.cx.identifier, "ComplexData.identifier");
        checker.soft_assert(input.cx.label == example.cx.label, "ComplexData.label");
        checker.soft_assert(input.cx.background_color.r == example.cx.background_color.r, "ComplexData.backgroundColor.r");
        checker.soft_assert(input.cx.background_color.g == example.cx.background_color.g, "ComplexData.backgroundColor.g");
        checker.soft_assert(input.cx.background_color.b == example.cx.background_color.b, "ComplexData.backgroundColor.b");
        checker.soft_assert(input.cx.text_color.r == example.cx.text_color.r, "ComplexData.textColor.r");
        checker.soft_assert(input.cx.text_color.g == example.cx.text_color.g, "ComplexData.textColor.g");
        checker.soft_assert(input.cx.text_color.b == example.cx.text_color.b, "ComplexData.textColor.b");
        checker.soft_assert(input.cx.spectrum.len() == example.cx.spectrum.len(), "ComplexData.spectrum.length");
        for i in 0..input.cx.spectrum.len() {
            checker.soft_assert(input.cx.spectrum[i].r == example.cx.spectrum[i].r, "ComplexData.spectrum.r");
            checker.soft_assert(input.cx.spectrum[i].g == example.cx.spectrum[i].g, "ComplexData.spectrum.g");
            checker.soft_assert(input.cx.spectrum[i].b == example.cx.spectrum[i].b, "ComplexData.spectrum.b");
        }
        checker.soft_assert(input.cxl.len() == example.cxl.len(), "[ComplexData].length");
        for i in 0..input.cxl.len() {
            checker.soft_assert(input.cxl[i].identifier == example.cxl[i].identifier, "[ComplexData].identifier");
            checker.soft_assert(input.cxl[i].label == example.cxl[i].label, "[ComplexData].label");
            checker.soft_assert(input.cxl[i].background_color.r == example.cxl[i].background_color.r, "[ComplexData].backgroundColor.r");
            checker.soft_assert(input.cxl[i].background_color.g == example.cxl[i].background_color.g, "[ComplexData].backgroundColor.g");
            checker.soft_assert(input.cxl[i].background_color.b == example.cxl[i].background_color.b, "[ComplexData].backgroundColor.b");
            checker.soft_assert(input.cxl[i].text_color.r == example.cxl[i].text_color.r, "[ComplexData].textColor.r");
            checker.soft_assert(input.cxl[i].text_color.g == example.cxl[i].text_color.g, "[ComplexData].textColor.g");
            checker.soft_assert(input.cxl[i].text_color.b == example.cxl[i].text_color.b, "[ComplexData].textColor.b");
            checker.soft_assert(input.cxl[i].spectrum.len() == example.cxl[i].spectrum.len(), "[ComplexData].spectrum.length");
            for j in 0..input.cxl[i].spectrum.len() {
                checker.soft_assert(input.cxl[i].spectrum[j].r == example.cxl[i].spectrum[j].r, "[ComplexData].spectrum.r");
                checker.soft_assert(input.cxl[i].spectrum[j].g == example.cxl[i].spectrum[j].g, "[ComplexData].spectrum.g");
                checker.soft_assert(input.cxl[i].spectrum[j].b == example.cxl[i].spectrum[j].b, "[ComplexData].spectrum.b");
            }
        }
    }

    checker.check();
}
