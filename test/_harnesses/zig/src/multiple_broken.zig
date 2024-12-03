const std = @import("std");
const Checker = @import("./util.zig").Checker;

const broken = @import("lib/BrokenMessages.zig");

const trunc = broken.TruncatedMessage{ .x = 1.0, .y = 2.0 };
const full = broken.FullMessage{ .x = 1.0, .y = 2.0, .z = 3.0 };

pub fn main() !void {
    const args = try std.process.argsAlloc(std.heap.page_allocator);
    defer std.process.argsFree(std.heap.page_allocator, args);

    var gpa = std.heap.GeneralPurposeAllocator(.{}){};
    const testAllocator = gpa.allocator();

    var checker = Checker{};

    if (std.mem.eql(u8, args[1], "--generate")) {
        var buffer_size: usize = 0;

        buffer_size += full.getSizeInBytes() * 6;
        buffer_size += trunc.getSizeInBytes();
        buffer_size += 7;

        const buffer = try testAllocator.alloc(u8, buffer_size);
        defer testAllocator.free(buffer);

        var local_offset: usize = 0;
        local_offset += full.writeBytes(local_offset, buffer, true);
        local_offset += full.writeBytes(local_offset, buffer, true);
        local_offset += full.writeBytes(local_offset, buffer, true);

        // write a truncated message tagged as a full one
        buffer[local_offset] = 1;
        local_offset += 1;
        local_offset += trunc.writeBytes(local_offset, buffer, false);

        local_offset += full.writeBytes(local_offset, buffer, true);
        local_offset += full.writeBytes(local_offset, buffer, true);
        local_offset += full.writeBytes(local_offset, buffer, true);

        var file = try std.fs.cwd().createFile(args[2], .{ .truncate = true });
        defer file.close();

        try file.writeAll(buffer);
    } else if (std.mem.eql(u8, args[1], "--read")) {
        var file = try std.fs.cwd().openFile(args[2], .{});
        defer file.close();

        const buffer = try file.readToEndAlloc(testAllocator, std.math.maxInt(u32));
        defer testAllocator.free(buffer);

        const msg_list = broken.processRawBytes(testAllocator, buffer, -1);
        checker.softAssert(msg_list == error.InvalidData, "read broken stream length");
    }

    const mem_result = gpa.deinit();
    checker.softAssert(mem_result == .ok, "memory leaks");

    checker.check();
}
