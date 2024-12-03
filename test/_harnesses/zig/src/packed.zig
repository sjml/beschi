const std = @import("std");
const Checker = @import("./util.zig").Checker;

const small = @import("lib/SmallMessages.zig");

const msg_list = [_]small.Message{
    small.Message{ .IntMessage = small.IntMessage{} },
    small.Message{ .FloatMessage = small.FloatMessage{} },
    small.Message{ .FloatMessage = small.FloatMessage{} },
    small.Message{ .FloatMessage = small.FloatMessage{} },
    small.Message{ .IntMessage = small.IntMessage{} },
    small.Message{ .EmptyMessage = small.EmptyMessage{} },
    small.Message{ .LongMessage = small.LongMessage{} },
    small.Message{ .LongMessage = small.LongMessage{} },
    small.Message{ .LongMessage = small.LongMessage{} },
    small.Message{ .IntMessage = small.IntMessage{} },
};

pub fn main() !void {
    const args = try std.process.argsAlloc(std.heap.page_allocator);
    defer std.process.argsFree(std.heap.page_allocator, args);

    var gpa = std.heap.GeneralPurposeAllocator(.{}){};
    const testAllocator = gpa.allocator();

    var checker = Checker{};

    if (std.mem.eql(u8, args[1], "--generate")) {
        const buffer_size = small.getPackedSize(&msg_list);
        const buffer = try testAllocator.alloc(u8, buffer_size);
        defer testAllocator.free(buffer);

        small.packMessages(&msg_list, buffer);

        var file = try std.fs.cwd().createFile(args[2], .{ .truncate = true });
        defer file.close();

        try file.writeAll(buffer);
    } else if (std.mem.eql(u8, args[1], "--read")) {
        var file = try std.fs.cwd().openFile(args[2], .{});
        defer file.close();

        const buffer = try file.readToEndAlloc(testAllocator, std.math.maxInt(u32));
        defer testAllocator.free(buffer);

        const unpacked = try small.unpackMessages(testAllocator, buffer);
        defer testAllocator.free(unpacked);

        checker.softAssert(unpacked.len == 10, "packed count");

        switch (msg_list[0]) {
            .IntMessage => {},
            else => checker.softAssert(false, "packed[0]"),
        }
        switch (msg_list[1]) {
            .FloatMessage => {},
            else => checker.softAssert(false, "packed[1]"),
        }
        switch (msg_list[2]) {
            .FloatMessage => {},
            else => checker.softAssert(false, "packed[2]"),
        }
        switch (msg_list[3]) {
            .FloatMessage => {},
            else => checker.softAssert(false, "packed[3]"),
        }
        switch (msg_list[4]) {
            .IntMessage => {},
            else => checker.softAssert(false, "packed[4]"),
        }
        switch (msg_list[5]) {
            .EmptyMessage => {},
            else => checker.softAssert(false, "packed[5]"),
        }
        switch (msg_list[6]) {
            .LongMessage => {},
            else => checker.softAssert(false, "packed[6]"),
        }
        switch (msg_list[7]) {
            .LongMessage => {},
            else => checker.softAssert(false, "packed[7]"),
        }
        switch (msg_list[8]) {
            .LongMessage => {},
            else => checker.softAssert(false, "packed[8]"),
        }
        switch (msg_list[9]) {
            .IntMessage => {},
            else => checker.softAssert(false, "packed[9]"),
        }
    }

    const mem_result = gpa.deinit();
    checker.softAssert(mem_result == .ok, "memory leaks");

    checker.check();
}
