const std = @import("std");
const Checker = @import("./util.zig").Checker;
const makeMutableSlice = @import("./util.zig").makeMutableSlice;

const comprehensive = @import("lib/ComprehensiveMessage.zig");
const TestingMessage = comprehensive.TestingMessage;
const Vec2 = comprehensive.Vec2;
const Vec3 = comprehensive.Vec3;
const Color = comprehensive.Color;
const Enumerated = comprehensive.Enumerated;
const Specified = comprehensive.Specified;
const ComplexData = comprehensive.ComplexData;

// zig fmt: off
const example = TestingMessage{
    .b = 250,
    .tf = true,
    .i16 = -32000,
    .ui16 = 65000,
    .i32 = -2000000000,
    .ui32 = 4000000000,
    .i64 = -9000000000000000000,
    .ui64 = 18000000000000000000,
    .f = 3.1415927410125732421875,
    .d = 2.718281828459045090795598298427648842334747314453125,
    .ee = Enumerated.B,
    .es = Specified.Negative,
    .s = "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
    .v2 = Vec2{
        .x = 256.512,
        .y = 1024.768,
    },
    .v3 = Vec3{
        .x = 128.64,
        .y = 2048.4096,
        .z = 16.32,
    },
    .c = Color{ .r = 255, .g = 128, .b = 0 },
    .il = makeMutableSlice([_]i16{ -1000, 500, 0, 750, 2000 }),
    .el = makeMutableSlice([_]Specified{
        Specified.Negative,
        Specified.Negative,
        Specified.Positive,
        Specified.Zero,
        Specified.Positive,
        Specified.Zero,
    }),
    .sl = makeMutableSlice([_][]const u8{
        "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
        "Quisque est eros, placerat ut libero ut, pellentesque tincidunt sem.",
        "Vivamus pellentesque turpis aliquet pretium tincidunt.",
        "Nulla facilisi.",
        "🐼❤️✝️",
        "用ねぼ雪入文モ段足リフケ報通ンさーを応細めい気川ヤセ車不古6治ニフサコ悩段をご青止ぽっ期年ト量報驚テルユ役1家埋詰軟きぎ。",
        "لآخر نشجب ونستنكر هؤلاء الرجال المفتونون بنشوة اللحظة الهائمون في رغبات",
    }),
    .v2l = makeMutableSlice([_]Vec2{
        Vec2{ .x = 10.0, .y = 15.0 },
        Vec2{ .x = 20.0, .y = 25.0 },
        Vec2{ .x = 30.0, .y = 35.0 },
        Vec2{ .x = 40.0, .y = 45.0 },
    }),
    .v3l = makeMutableSlice([_]Vec3{
        Vec3{ .x = 10.0, .y = 15.0, .z = 17.5 },
        Vec3{ .x = 20.0, .y = 25.0, .z = 27.5 },
        Vec3{ .x = 30.0, .y = 35.0, .z = 37.5 },
        Vec3{ .x = 40.0, .y = 45.0, .z = 47.5 },
    }),
    .cl = makeMutableSlice([_]Color{
        Color{ .r = 255, .g = 0, .b = 0 },
        Color{ .r = 0, .g = 255, .b = 0 },
        Color{ .r = 0, .g = 0, .b = 255 },
    }),
    .cx = ComplexData{
        .identifier = 127,
        .label = "ComplexDataObject",
        .backgroundColor = Color{ .r = 255, .g = 0, .b = 0 },
        .textColor = Color{ .r = 0, .g = 255, .b = 0 },
        .spectrum = makeMutableSlice([_]Color{
            Color{ .r = 0, .g = 0, .b = 255 },
            Color{ .r = 0, .g = 255, .b = 0 },
            Color{ .r = 255, .g = 0, .b = 0 },
        })
    },
    .cxl = makeMutableSlice([_]ComplexData{
        ComplexData{
            .identifier = 255,
            .label = "Complex1",
            .backgroundColor = Color{ .r = 0, .g = 0, .b = 255 },
            .textColor = Color{ .r = 255, .g = 0, .b = 0 },
            .spectrum = makeMutableSlice([_]Color{
                Color{ .r = 0, .g = 0, .b = 255 },
                Color{ .r = 0, .g = 255, .b = 0 },
                Color{ .r = 255, .g = 0, .b = 0 },
                Color{ .r = 0, .g = 255, .b = 0 },
                Color{ .r = 0, .g = 0, .b = 255 },
            })
        },
        ComplexData{
            .identifier = 63,
            .label = "Complex2",
            .backgroundColor = Color{ .r = 255, .g = 0, .b = 0 },
            .textColor = Color{ .r = 0, .g = 0, .b = 255 },
            .spectrum = makeMutableSlice([_]Color{
                Color{ .r = 255, .g = 0, .b = 0 },
                Color{ .r = 0, .g = 255, .b = 0 },
                Color{ .r = 0, .g = 0, .b = 255 },
                Color{ .r = 0, .g = 255, .b = 0 },
                Color{ .r = 255, .g = 0, .b = 0 },
            })
        }
    })
};
// zig fmt: on

pub fn main() !void {
    const args = try std.process.argsAlloc(std.heap.page_allocator);
    defer std.process.argsFree(std.heap.page_allocator, args);

    var gpa = std.heap.GeneralPurposeAllocator(.{}){};
    const testAllocator = gpa.allocator();

    var checker = Checker{};

    if (std.mem.eql(u8, args[1], "--generate")) {
        const buffer = try testAllocator.alloc(u8, example.getSizeInBytes());
        defer testAllocator.free(buffer);

        const written_bytes = example.writeBytes(0, buffer, false);
        checker.softAssert(written_bytes == 932, "size calculation check");

        var file = try std.fs.cwd().createFile(args[2], .{ .truncate = true });
        defer file.close();

        try file.writeAll(buffer);
    } else if (std.mem.eql(u8, args[1], "--read")) {
        var file = try std.fs.cwd().openFile(args[2], .{});
        defer file.close();

        const buffer = try file.readToEndAlloc(testAllocator, std.math.maxInt(u32));
        defer testAllocator.free(buffer);

        const input_read = try TestingMessage.fromBytes(testAllocator, 0, buffer);
        checker.softAssert(input_read.bytes_read == 932, "size read check");
        var input = input_read.value;
        defer input.deinit(testAllocator);
        checker.softAssert(input.b == example.b, "byte");
        checker.softAssert(input.tf == example.tf, "bool");
        checker.softAssert(input.i16 == example.i16, "i16");
        checker.softAssert(input.ui16 == example.ui16, "ui16");
        checker.softAssert(input.i32 == example.i32, "i32");
        checker.softAssert(input.ui32 == example.ui32, "ui32");
        checker.softAssert(input.i64 == example.i64, "i64");
        checker.softAssert(input.ui64 == example.ui64, "ui64");
        checker.softAssert(input.f == example.f, "float");
        checker.softAssert(input.d == example.d, "double");
        checker.softAssert(input.ee == example.ee, "enumerated");
        checker.softAssert(input.es == example.es, "specified");
        checker.softAssert(std.mem.eql(u8, input.s, example.s), "string");
        checker.softAssert(input.v2.x == example.v2.x, "Vec2");
        checker.softAssert(input.v2.y == example.v2.y, "Vec2");
        checker.softAssert(input.v3.x == example.v3.x, "Vec3");
        checker.softAssert(input.v3.y == example.v3.y, "Vec3");
        checker.softAssert(input.v3.z == example.v3.z, "Vec3");
        checker.softAssert(input.c.r == example.c.r, "Color");
        checker.softAssert(input.c.g == example.c.g, "Color");
        checker.softAssert(input.c.b == example.c.b, "Color");
        checker.softAssert(input.il.len == example.il.len, "[int16].length");
        for (0..input.il.len) |i| {
            checker.softAssert(input.il[i] == example.il[i], "[int16]");
        }
        checker.softAssert(input.el.len == example.el.len, "[Specified].length");
        for (0..input.el.len) |i| {
            checker.softAssert(input.el[i] == example.el[i], "[Specified]");
        }
        checker.softAssert(input.sl.len == example.sl.len, "[string].length");
        for (0..input.sl.len) |i| {
            checker.softAssert(std.mem.eql(u8, input.sl[i], example.sl[i]), "[string]");
        }
        checker.softAssert(input.v2l.len == example.v2l.len, "[Vec2].length");
        for (0..input.v2l.len) |i| {
            checker.softAssert(input.v2l[i].x == example.v2l[i].x, "[Vec2].x");
            checker.softAssert(input.v2l[i].y == example.v2l[i].y, "[Vec2].y");
        }
        checker.softAssert(input.v3l.len == example.v3l.len, "[Vec3].length");
        for (0..input.v3l.len) |i| {
            checker.softAssert(input.v3l[i].x == example.v3l[i].x, "[Vec3].x");
            checker.softAssert(input.v3l[i].y == example.v3l[i].y, "[Vec3].y");
            checker.softAssert(input.v3l[i].z == example.v3l[i].z, "[Vec3].z");
        }
        checker.softAssert(input.cl.len == example.cl.len, "[Color].length");
        for (0..input.cl.len) |i| {
            checker.softAssert(input.cl[i].r == example.cl[i].r, "[Color].r");
            checker.softAssert(input.cl[i].g == example.cl[i].g, "[Color].g");
            checker.softAssert(input.cl[i].b == example.cl[i].b, "[Color].b");
        }
        checker.softAssert(input.cx.identifier == example.cx.identifier, "ComplexData.identifier");
        checker.softAssert(std.mem.eql(u8, input.cx.label, example.cx.label), "ComplexData.label");
        checker.softAssert(input.cx.backgroundColor.r == example.cx.backgroundColor.r, "ComplexData.backgroundColor.r");
        checker.softAssert(input.cx.backgroundColor.g == example.cx.backgroundColor.g, "ComplexData.backgroundColor.g");
        checker.softAssert(input.cx.backgroundColor.b == example.cx.backgroundColor.b, "ComplexData.backgroundColor.b");
        checker.softAssert(input.cx.textColor.r == example.cx.textColor.r, "ComplexData.textColor.r");
        checker.softAssert(input.cx.textColor.g == example.cx.textColor.g, "ComplexData.textColor.g");
        checker.softAssert(input.cx.textColor.b == example.cx.textColor.b, "ComplexData.textColor.b");
        checker.softAssert(input.cx.spectrum.len == example.cx.spectrum.len, "ComplexData.spectrum.length");
        for (0..input.cx.spectrum.len) |i| {
            checker.softAssert(input.cx.spectrum[i].r == example.cx.spectrum[i].r, "ComplexData.spectrum.r");
            checker.softAssert(input.cx.spectrum[i].g == example.cx.spectrum[i].g, "ComplexData.spectrum.g");
            checker.softAssert(input.cx.spectrum[i].b == example.cx.spectrum[i].b, "ComplexData.spectrum.b");
        }
        checker.softAssert(input.cxl.len == example.cxl.len, "[ComplexData].length");
        for (0..input.cxl.len) |i| {
            checker.softAssert(input.cxl[i].identifier == example.cxl[i].identifier, "[ComplexData].identifier");
            checker.softAssert(std.mem.eql(u8, input.cxl[i].label, example.cxl[i].label), "[ComplexData].label");
            checker.softAssert(input.cxl[i].backgroundColor.r == example.cxl[i].backgroundColor.r, "[ComplexData].backgroundColor.r");
            checker.softAssert(input.cxl[i].backgroundColor.g == example.cxl[i].backgroundColor.g, "[ComplexData].backgroundColor.g");
            checker.softAssert(input.cxl[i].backgroundColor.b == example.cxl[i].backgroundColor.b, "[ComplexData].backgroundColor.b");
            checker.softAssert(input.cxl[i].textColor.r == example.cxl[i].textColor.r, "[ComplexData].textColor.r");
            checker.softAssert(input.cxl[i].textColor.g == example.cxl[i].textColor.g, "[ComplexData].textColor.g");
            checker.softAssert(input.cxl[i].textColor.b == example.cxl[i].textColor.b, "[ComplexData].textColor.b");
            checker.softAssert(input.cxl[i].spectrum.len == example.cxl[i].spectrum.len, "[ComplexData].spectrum.length");
            for (0..input.cxl[i].spectrum.len) |j| {
                checker.softAssert(input.cxl[i].spectrum[j].r == example.cxl[i].spectrum[j].r, "[ComplexData].spectrum.r");
                checker.softAssert(input.cxl[i].spectrum[j].g == example.cxl[i].spectrum[j].g, "[ComplexData].spectrum.g");
                checker.softAssert(input.cxl[i].spectrum[j].b == example.cxl[i].spectrum[j].b, "[ComplexData].spectrum.b");
            }
        }
    }

    const mem_result = gpa.deinit();
    checker.softAssert(mem_result == .ok, "memory leaks");

    checker.check();
}
