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

        buffer[4] = 15;

        var file = try std.fs.cwd().createFile(args[2], .{ .truncate = true });
        defer file.close();

        try file.writeAll(buffer);
    } else if (std.mem.eql(u8, args[1], "--read")) {
        var file = try std.fs.cwd().openFile(args[2], .{});
        defer file.close();

        const buffer = try file.readToEndAlloc(testAllocator, std.math.maxInt(u32));
        defer testAllocator.free(buffer);

        if (small.unpackMessages(testAllocator, buffer)) |_| {
            checker.softAssert(false, "broken unpack");
        } else |err| {
            checker.softAssert(err == error.InvalidData, "broken unpack error");
        }
    }

    const mem_result = gpa.deinit();
    checker.softAssert(mem_result == .ok, "memory leaks");

    checker.check();
}
