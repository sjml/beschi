// message files will include code that's not necessarily called in each test
#![allow(dead_code)]

use std::fs;

// in a real program you would want this file to have an appropriate name
//   but for testing I'd rather not deal with it having a different name
//   than all the other files.
#[allow(non_snake_case)]
mod ComprehensiveMessage;
use ComprehensiveMessage::*;

mod util;

fn main() {
    let mut checker = util::Checker { ok: true };
    let args = util::arg_parse();

    #[allow(clippy::approx_constant)]
    #[allow(clippy::excessive_precision)]
    let example = TestingMessage {
        b: 250,
        tf: true,
        i16: -32000,
        ui16: 65000,
        i32: -2000000000,
        ui32: 4000000000,
        i64: -9000000000000000000,
        ui64: 18000000000000000000,
        f: 3.1415927410125732421875,
        d: 2.718281828459045090795598298427648842334747314453125,
        ee: Enumerated::Beta,
        es: Specified::Negative,
        s: "Lorem ipsum dolor sit amet, consectetur adipiscing elit.".to_string(),
        v2: Vec2 {x: 256.512, y: 1024.768},
        v3: Vec3 {x: 128.64, y: 2048.4096, z: 16.32},
        c: Color {r: 255, g: 128, b: 0},
        il: vec![-1000, 500, 0, 750, 2000],
        el: vec![
            Specified::Negative,
            Specified::Negative,
            Specified::Positive,
            Specified::Zero,
            Specified::Positive,
            Specified::Zero
        ],
        sl: vec![
            "Lorem ipsum dolor sit amet, consectetur adipiscing elit.".to_string(),
            "Quisque est eros, placerat ut libero ut, pellentesque tincidunt sem.".to_string(),
            "Vivamus pellentesque turpis aliquet pretium tincidunt.".to_string(),
            "Nulla facilisi.".to_string(),
            "🐼❤️✝️".to_string(),
            "用ねぼ雪入文モ段足リフケ報通ンさーを応細めい気川ヤセ車不古6治ニフサコ悩段をご青止ぽっ期年ト量報驚テルユ役1家埋詰軟きぎ。".to_string(),
            "لآخر نشجب ونستنكر هؤلاء الرجال المفتونون بنشوة اللحظة الهائمون في رغبات".to_string(),
        ],
        v2l: vec![
            Vec2 {x: 10.0, y: 15.0},
            Vec2 {x: 20.0, y: 25.0},
            Vec2 {x: 30.0, y: 35.0},
            Vec2 {x: 40.0, y: 45.0},
        ],
        v3l: vec![
            Vec3 {x: 10.0, y: 15.0, z: 17.5},
            Vec3 {x: 20.0, y: 25.0, z: 27.5},
            Vec3 {x: 30.0, y: 35.0, z: 37.5},
            Vec3 {x: 40.0, y: 45.0, z: 47.5},
        ],
        cl: vec![
            Color {r: 255, g: 0, b: 0},
            Color {r: 0, g: 255, b: 0},
            Color {r: 0, g: 0, b: 255},
        ],
        cx: ComplexData {
            identifier: 127,
            label: "ComplexDataObject".to_string(),
            background_color: Color {r: 255, g: 0, b: 0},
            text_color: Color {r: 0, g: 255, b: 0},
            spectrum: vec![
                Color {r: 0, g: 0, b: 255},
                Color {r: 0, g: 255, b: 0},
                Color {r: 255, g: 0, b: 0},
            ],
            ranges: vec![
                Specified::Negative,
                Specified::Positive,
            ],
        },
        cxl: vec![
            ComplexData {
                identifier: 255,
                label: "Complex1".to_string(),
                background_color: Color {r: 0, g: 0, b: 255},
                text_color: Color {r: 255, g: 0, b: 0},
                spectrum: vec![
                    Color {r: 0, g: 0, b: 255},
                    Color {r: 0, g: 255, b: 0},
                    Color {r: 255, g: 0, b: 0},
                    Color {r: 0, g: 255, b: 0},
                    Color {r: 0, g: 0, b: 255},
                ],
                ranges: vec![
                    Specified::Zero,
                    Specified::Positive,
                ],
            },
            ComplexData {
                identifier: 63,
                label: "Complex2".to_string(),
                background_color: Color {r: 255, g: 0, b: 0},
                text_color: Color {r: 0, g: 0, b: 255},
                spectrum: vec![
                    Color {r: 255, g: 0, b: 0},
                    Color {r: 0, g: 255, b: 0},
                    Color {r: 0, g: 0, b: 255},
                    Color {r: 0, g: 255, b: 0},
                    Color {r: 255, g: 0, b: 0},
                ],
                ranges: vec![
                    Specified::Negative,
                    Specified::Zero,
                ],
            },
        ]
    };

    if args.contains_key("generate") {
        let mut writer: Vec<u8> = Vec::new();
        example.write_bytes(&mut writer, false);
        checker.soft_assert(writer.len() == 956, "size calculation check");

        let filename = args.get("generate").unwrap();
        fs::write(filename, writer).unwrap();
    }
    else if args.contains_key("read") {
        let filename = args.get("read").unwrap();
        let buffer = fs::read(&filename).unwrap();
        let mut reader = BufferReader::new(buffer);
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
        checker.soft_assert(input.ee == example.ee, "enumerated");
        checker.soft_assert(input.es == example.es, "specified");
        checker.soft_assert(input.s == example.s, "string");
        checker.soft_assert(input.v2.x == example.v2.x, "Vec2");
        checker.soft_assert(input.v2.y == example.v2.y, "Vec2");
        checker.soft_assert(input.v3.x == example.v3.x, "Vec3");
        checker.soft_assert(input.v3.y == example.v3.y, "Vec3");
        checker.soft_assert(input.v3.z == example.v3.z, "Vec3");
        checker.soft_assert(input.c.r == example.c.r, "Color");
        checker.soft_assert(input.c.g == example.c.g, "Color");
        checker.soft_assert(input.c.b == example.c.b, "Color");
        checker.soft_assert(input.il.len() == example.il.len(), "[int16].length");
        for i in 0..input.il.len() {
            checker.soft_assert(input.il[i] == example.il[i], "[int16]");
        }
        checker.soft_assert(input.el.len() == example.el.len(), "[Specified].length");
        for i in 0..input.el.len() {
            checker.soft_assert(input.el[i] == example.el[i], "[Specified]");
        }
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
        checker.soft_assert(input.cx.ranges.len() == example.cx.ranges.len(), "ComplexData.ranges.length");
        for i in 0..input.cx.ranges.len() {
            checker.soft_assert(input.cx.ranges[i] == example.cx.ranges[i], "ComplexData.ranges");
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
            checker.soft_assert(input.cxl[i].ranges.len() == example.cxl[i].ranges.len(), "[ComplexData].ranges.length");
            for j in 0..input.cxl[i].ranges.len() {
                checker.soft_assert(input.cxl[i].ranges[j] == example.cxl[i].ranges[j], "[ComplexData].ranges");
            }
        }
    }

    checker.check();
}
