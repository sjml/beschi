const std = @import("std");
const Checker = @import("./util.zig").Checker;
const makeMutableSlice = @import("./util.zig").makeMutableSlice;

const comps = @import("lib/ComprehensiveMessage.zig");

const example = comps.TestingMessage{};

pub fn main() !void {
    const args = try std.process.argsAlloc(std.heap.page_allocator);
    defer std.process.argsFree(std.heap.page_allocator, args);

    var gpa = std.heap.GeneralPurposeAllocator(.{}){};
    const testAllocator = gpa.allocator();

    var checker = Checker{};

    if (std.mem.eql(u8, args[1], "--generate")) {
        var buffer_size: usize = 0;
        buffer_size += example.getSizeInBytes();

        const buffer = try testAllocator.alloc(u8, buffer_size);
        defer testAllocator.free(buffer);

        _ = example.writeBytes(0, buffer, false);

        var file = try std.fs.cwd().createFile(args[2], .{ .truncate = true });
        defer file.close();

        try file.writeAll(buffer);
    } else if (std.mem.eql(u8, args[1], "--read")) {
        var file = try std.fs.cwd().openFile(args[2], .{});
        defer file.close();

        const buffer = try file.readToEndAlloc(testAllocator, std.math.maxInt(u32));
        defer testAllocator.free(buffer);

        const input = (try comps.TestingMessage.fromBytes(testAllocator, 0, buffer)).value;
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
        checker.softAssert(std.mem.eql(u8, input.s, example.s), "string");
        checker.softAssert(input.v2.x == example.v2.x, "Vec2");
        checker.softAssert(input.v2.y == example.v2.y, "Vec2");
        checker.softAssert(input.v3.x == example.v3.x, "Vec3");
        checker.softAssert(input.v3.y == example.v3.y, "Vec3");
        checker.softAssert(input.v3.z == example.v3.z, "Vec3");
        checker.softAssert(input.c.r == example.c.r, "Color");
        checker.softAssert(input.c.g == example.c.g, "Color");
        checker.softAssert(input.c.b == example.c.b, "Color");
        checker.softAssert(input.sl.len == example.sl.len, "[string].length");
        checker.softAssert(input.sl.len == 0, "[string]");
        checker.softAssert(input.v2l.len == example.v2l.len, "[Vec2].length");
        checker.softAssert(input.v2l.len == 0, "[Vec2].length");
        checker.softAssert(input.v3l.len == example.v3l.len, "[Vec3].length");
        checker.softAssert(input.v3l.len == 0, "[Vec3].length");
        checker.softAssert(input.cl.len == example.cl.len, "[Color].length");
        checker.softAssert(input.cl.len == 0, "[Color].length");
        checker.softAssert(input.cx.identifier == example.cx.identifier, "ComplexData.identifier");
        checker.softAssert(std.mem.eql(u8, input.cx.label, example.cx.label), "ComplexData.label");
        checker.softAssert(input.cx.backgroundColor.r == example.cx.backgroundColor.r, "ComplexData.backgroundColor.r");
        checker.softAssert(input.cx.backgroundColor.g == example.cx.backgroundColor.g, "ComplexData.backgroundColor.g");
        checker.softAssert(input.cx.backgroundColor.b == example.cx.backgroundColor.b, "ComplexData.backgroundColor.b");
        checker.softAssert(input.cx.textColor.r == example.cx.textColor.r, "ComplexData.textColor.r");
        checker.softAssert(input.cx.textColor.g == example.cx.textColor.g, "ComplexData.textColor.g");
        checker.softAssert(input.cx.textColor.b == example.cx.textColor.b, "ComplexData.textColor.b");
        checker.softAssert(input.cx.spectrum.len == example.cx.spectrum.len, "ComplexData.spectrum.length");
        checker.softAssert(input.cx.spectrum.len == 0, "ComplesData.spectrum.length");
        checker.softAssert(input.cxl.len == example.cxl.len, "[ComplexData].length");
        checker.softAssert(input.cxl.len == 0, "[ComplexData].length");
    }

    const mem_result = gpa.deinit();
    checker.softAssert(mem_result == .ok, "memory leaks");

    checker.check();
}
