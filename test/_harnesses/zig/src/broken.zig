const std = @import("std");
const Checker = @import("./util.zig").Checker;

const broken = @import("lib/BrokenMessages.zig");
const TruncatedMessage = broken.TruncatedMessage;
const FullMessage = broken.FullMessage;

const broken_msg = TruncatedMessage{ .x = 1.0, .y = 2.0 };

pub fn main() !void {
    const args = try std.process.argsAlloc(std.heap.page_allocator);
    defer std.process.argsFree(std.heap.page_allocator, args);

    var gpa = std.heap.GeneralPurposeAllocator(.{}){};
    const testAllocator = gpa.allocator();

    var checker = Checker{};

    if (std.mem.eql(u8, args[1], "--generate")) {
        const buffer = try testAllocator.alloc(u8, broken_msg.getSizeInBytes());
        defer testAllocator.free(buffer);

        const written_bytes = broken_msg.writeBytes(0, buffer, false);
        checker.softAssert(written_bytes == 8, "size calculation check");

        var file = try std.fs.cwd().createFile(args[2], .{ .truncate = true });
        defer file.close();

        try file.writeAll(buffer);
    } else if (std.mem.eql(u8, args[1], "--read")) {
        var file = try std.fs.cwd().openFile(args[2], .{});
        defer file.close();

        const buffer = try file.readToEndAlloc(testAllocator, std.math.maxInt(u32));
        defer testAllocator.free(buffer);

        const res = FullMessage.fromBytes(0, buffer);
        checker.softAssert(res == error.EOF, "reading broken message");
    }

    const mem_result = gpa.deinit();
    checker.softAssert(mem_result == .ok, "memory leaks");

    checker.check();
}
