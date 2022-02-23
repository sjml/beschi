import Foundation

import GeneratedMessages

var example = TestingMessage()
example.b = 250
example.tf = true
example.i16 = -32000
example.ui16 = 65000
example.i32 = -2000000000
example.ui32 = 4000000000
example.i64 = -9000000000000000000
example.ui64 = 18000000000000000000
example.f = 3.1415927410125732421875
example.d = 2.718281828459045090795598298427648842334747314453125
example.s = "Lorem ipsum dolor sit amet, consectetur adipiscing elit."
example.v2 = Vec2()
example.v2.x = 256.512
example.v2.y = 1024.768
example.v3 = Vec3()
example.v3.x = 128.64
example.v3.y = 2048.4096
example.v3.z = 16.32
example.c = Color()
example.c.r = 255
example.c.g = 128
example.c.b = 0
example.sl = [
    "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
    "Quisque est eros, placerat ut libero ut, pellentesque tincidunt sem.",
    "Vivamus pellentesque turpis aliquet pretium tincidunt.",
    "Nulla facilisi.",
    "🐼❤️✝️",
    "用ねぼ雪入文モ段足リフケ報通ンさーを応細めい気川ヤセ車不古6治ニフサコ悩段をご青止ぽっ期年ト量報驚テルユ役1家埋詰軟きぎ。",
    "لآخر نشجب ونستنكر هؤلاء الرجال المفتونون بنشوة اللحظة الهائمون في رغبات",
]
var v21 = Vec2()
v21.x = 10.0
v21.y = 15.0
var v22 = Vec2()
v22.x = 20.0
v22.y = 25.0
var v23 = Vec2()
v23.x = 30.0
v23.y = 35.0
var v24 = Vec2()
v24.x = 40.0
v24.y = 45.0
example.v2l = [
    v21, v22, v23, v24,
]
var v31 = Vec3()
v31.x = 10.0
v31.y = 15.0
v31.z = 17.5
var v32 = Vec3()
v32.x = 20.0
v32.y = 25.0
v32.z = 27.5
var v33 = Vec3()
v33.x = 30.0
v33.y = 35.0
v33.z = 37.5
var v34 = Vec3()
v34.x = 40.0
v34.y = 45.0
v34.z = 47.5
example.v3l = [
    v31, v32, v33, v34
]
var c1 = Color()
c1.r = 255
c1.g = 0
c1.b = 0
var c2 = Color()
c2.r = 0
c2.g = 255
c2.b = 0
var c3 = Color()
c3.r = 0
c3.g = 0
c3.b = 255
example.cl = [
    c1, c2, c3
]
example.cx = ComplexData()
example.cx.identifier = 127
example.cx.label = "ComplexDataObject"
example.cx.backgroundColor = c1
example.cx.textColor = c2
example.cx.spectrum = [
    c3, c2, c1
]
var cx1 = ComplexData()
cx1.identifier = 255
cx1.label = "Complex1"
cx1.backgroundColor = c3
cx1.textColor = c1
cx1.spectrum = [c3, c2, c1, c2, c3]
var cx2 = ComplexData()
cx2.identifier = 63
cx2.label = "Complex2"
cx2.backgroundColor = c1
cx2.textColor = c3
cx2.spectrum = [c1, c2, c3, c2, c1]
example.cxl = [cx1, cx2]

var OK: Bool = true
func softAssert(_ condition: Bool, _ label: String) {
    if (!condition) {
        "FAILED! Swift: \(label)\n".data(using: .utf8).map(FileHandle.standardError.write)
        OK = false
    }
}

var parsed: [String: String] = [:]
var currentKeyword: String? = nil
for arg in CommandLine.arguments[1...] {
    if arg.starts(with: "--") {
        currentKeyword = String(arg[arg.index(arg.startIndex, offsetBy: 2)...])
        continue
    }
    if (currentKeyword != nil) {
        parsed[currentKeyword!] = arg
        currentKeyword = nil
        continue
    }
    parsed[arg] = ""
}

if parsed["generate"] != nil {
    let outPath = URL(fileURLWithPath: parsed["generate"]!)
    let outDir = outPath.deletingLastPathComponent()
    try FileManager.default.createDirectory(at: outDir, withIntermediateDirectories: true)

    var data = Data()
    example.WriteBytes(data: &data, tag: false)

    try data.write(to: outPath)
}
else if parsed["read"] != nil {
    let data = try Data(contentsOf: URL(fileURLWithPath: parsed["read"]!))
    let inputOpt = TestingMessage.FromBytes(data)
    softAssert(inputOpt != nil, "parsing test message")

    let input = inputOpt!
    softAssert(input.b == example.b, "byte");
    softAssert(input.tf == example.tf, "bool")
    softAssert(input.i16 == example.i16, "i16")
    softAssert(input.ui16 == example.ui16, "ui16")
    softAssert(input.i32 == example.i32, "i32")
    softAssert(input.ui32 == example.ui32, "ui32")
    softAssert(input.i64 == example.i64, "i64")
    softAssert(input.ui64 == example.ui64, "ui64")
    softAssert(input.f == example.f, "float")
    softAssert(input.d == example.d, "double")
    softAssert(input.s == example.s, "string")
    softAssert(input.v2.x == example.v2.x, "Vec2")
    softAssert(input.v2.y == example.v2.y, "Vec2")
    softAssert(input.v3.x == example.v3.x, "Vec3")
    softAssert(input.v3.y == example.v3.y, "Vec3")
    softAssert(input.v3.z == example.v3.z, "Vec3")
    softAssert(input.c.r == example.c.r, "Color")
    softAssert(input.c.g == example.c.g, "Color")
    softAssert(input.c.b == example.c.b, "Color")
    softAssert(input.sl.count == example.sl.count, "[string].length")
    for i in 0..<input.sl.count {
        softAssert(input.sl[i] == example.sl[i], "[string]")
    }
    softAssert(input.v2l.count == example.v2l.count, "[Vec2].length")
    for i in 0..<input.v2l.count {
        softAssert(input.v2l[i].x == example.v2l[i].x, "[Vec2].x")
        softAssert(input.v2l[i].y == example.v2l[i].y, "[Vec2].y")
    }
    softAssert(input.v3l.count == example.v3l.count, "[Vec3].length")
    for i in 0..<input.v3l.count {
        softAssert(input.v3l[i].x == example.v3l[i].x, "[Vec3].x")
        softAssert(input.v3l[i].y == example.v3l[i].y, "[Vec3].y")
        softAssert(input.v3l[i].z == example.v3l[i].z, "[Vec3].z")
    }
    softAssert(input.cl.count == example.cl.count, "[Color].length")
    for i in 0..<input.cl.count {
        softAssert(input.cl[i].r == example.cl[i].r, "[Color].r")
        softAssert(input.cl[i].g == example.cl[i].g, "[Color].g")
        softAssert(input.cl[i].b == example.cl[i].b, "[Color].b")
    }
    softAssert(input.cx.identifier == example.cx.identifier, "ComplexData.identifier")
    softAssert(input.cx.label == example.cx.label, "ComplexData.label")
    softAssert(input.cx.backgroundColor.r == example.cx.backgroundColor.r, "ComplexData.backgroundColor.r")
    softAssert(input.cx.backgroundColor.g == example.cx.backgroundColor.g, "ComplexData.backgroundColor.g")
    softAssert(input.cx.backgroundColor.b == example.cx.backgroundColor.b, "ComplexData.backgroundColor.b")
    softAssert(input.cx.textColor.r == example.cx.textColor.r, "ComplexData.textColor.r")
    softAssert(input.cx.textColor.g == example.cx.textColor.g, "ComplexData.textColor.g")
    softAssert(input.cx.textColor.b == example.cx.textColor.b, "ComplexData.textColor.b")
    softAssert(input.cx.spectrum.count == example.cx.spectrum.count, "ComplexData.spectrum.length")
    for i in 0..<input.cx.spectrum.count {
        softAssert(input.cx.spectrum[i].r == example.cx.spectrum[i].r, "ComplexData.spectrum.r")
        softAssert(input.cx.spectrum[i].g == example.cx.spectrum[i].g, "ComplexData.spectrum.g")
        softAssert(input.cx.spectrum[i].b == example.cx.spectrum[i].b, "ComplexData.spectrum.b")
    }
}
