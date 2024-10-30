const std = @import("std");
const Checker = @import("./util.zig").Checker;

const small = @import("lib/SmallMessages.zig");

const empty_msg = small.EmptyMessage{};
const byte_msg = small.ByteMessage{ .byteMember = 242 };
const int_msg_a = small.IntMessage{ .intMember = -42 };
const int_msg_b = small.IntMessage{ .intMember = 2048 };
const float_msg = small.FloatMessage{ .floatMember = 1234.5678 };
const long_msg = small.LongMessage{ .intMember = 2147483647 + 10 };

pub fn main() !void {
    const args = try std.process.argsAlloc(std.heap.page_allocator);
    defer std.process.argsFree(std.heap.page_allocator, args);

    var gpa = std.heap.GeneralPurposeAllocator(.{}){};
    const testAllocator = gpa.allocator();

    var checker = Checker{};

    if (std.mem.eql(u8, args[1], "--generate")) {
        var buffer_size: usize = 0;
        buffer_size += byte_msg.getSizeInBytes();
        buffer_size += int_msg_a.getSizeInBytes() * 3;
        buffer_size += int_msg_b.getSizeInBytes() * 4;
        buffer_size += empty_msg.getSizeInBytes() * 2;
        buffer_size += long_msg.getSizeInBytes();
        buffer_size += float_msg.getSizeInBytes();
        buffer_size += 12;

        const buffer = try testAllocator.alloc(u8, buffer_size);
        defer testAllocator.free(buffer);

        var local_offset: usize = 0;
        local_offset += byte_msg.writeBytes(local_offset, buffer, true);
        local_offset += int_msg_a.writeBytes(local_offset, buffer, true);
        local_offset += int_msg_b.writeBytes(local_offset, buffer, true);
        local_offset += empty_msg.writeBytes(local_offset, buffer, true);
        local_offset += long_msg.writeBytes(local_offset, buffer, true);
        local_offset += float_msg.writeBytes(local_offset, buffer, true);
        local_offset += int_msg_a.writeBytes(local_offset, buffer, true);
        local_offset += int_msg_b.writeBytes(local_offset, buffer, true);
        local_offset += int_msg_b.writeBytes(local_offset, buffer, true);
        local_offset += int_msg_b.writeBytes(local_offset, buffer, true);
        local_offset += int_msg_a.writeBytes(local_offset, buffer, true);
        local_offset += empty_msg.writeBytes(local_offset, buffer, true);

        var file = try std.fs.cwd().createFile(args[2], .{ .truncate = true });
        defer file.close();

        try file.writeAll(buffer);
    } else if (std.mem.eql(u8, args[1], "--read")) {
        var file = try std.fs.cwd().openFile(args[2], .{});
        defer file.close();

        const original_buffer = try file.readToEndAlloc(testAllocator, std.math.maxInt(u32));
        defer testAllocator.free(original_buffer);

        const buffer = try testAllocator.alloc(u8, original_buffer.len + 25);
        defer testAllocator.free(buffer);

        std.mem.copyForwards(u8, buffer[0..original_buffer.len], original_buffer);
        for (buffer[original_buffer.len..]) |*b| {
            b.* = 0;
        }

        const msg_list = try small.processRawBytes(testAllocator, buffer);
        defer testAllocator.free(msg_list);
        checker.softAssert(msg_list.len == 12, "reading multiple messages");

        switch (msg_list[0]) {
            .ByteMessage => |bm| checker.softAssert(bm.byteMember == byte_msg.byteMember, "msg 0 content"),
            else => checker.softAssert(false, "msg 0 type"),
        }
        switch (msg_list[1]) {
            .IntMessage => |im| checker.softAssert(im.intMember == int_msg_a.intMember, "msg 1 content"),
            else => checker.softAssert(false, "msg 1 type"),
        }
        switch (msg_list[2]) {
            .IntMessage => |im| checker.softAssert(im.intMember == int_msg_b.intMember, "msg 2 content"),
            else => checker.softAssert(false, "msg 2 type"),
        }
        switch (msg_list[3]) {
            .EmptyMessage => |_| {},
            else => checker.softAssert(false, "msg 3 type"),
        }
        switch (msg_list[4]) {
            .LongMessage => |lm| checker.softAssert(lm.intMember == long_msg.intMember, "msg 4 content"),
            else => checker.softAssert(false, "msg 4 type"),
        }
        switch (msg_list[5]) {
            .FloatMessage => |fm| checker.softAssert(fm.floatMember == float_msg.floatMember, "msg 5 content"),
            else => checker.softAssert(false, "msg 5 type"),
        }
        switch (msg_list[6]) {
            .IntMessage => |im| checker.softAssert(im.intMember == int_msg_a.intMember, "msg 6 content"),
            else => checker.softAssert(false, "msg 6 type"),
        }
        switch (msg_list[7]) {
            .IntMessage => |im| checker.softAssert(im.intMember == int_msg_b.intMember, "msg 7 content"),
            else => checker.softAssert(false, "msg 7 type"),
        }
        switch (msg_list[8]) {
            .IntMessage => |im| checker.softAssert(im.intMember == int_msg_b.intMember, "msg 8 content"),
            else => checker.softAssert(false, "msg 8 type"),
        }
        switch (msg_list[9]) {
            .IntMessage => |im| checker.softAssert(im.intMember == int_msg_b.intMember, "msg 9 content"),
            else => checker.softAssert(false, "msg 9 type"),
        }
        switch (msg_list[10]) {
            .IntMessage => |im| checker.softAssert(im.intMember == int_msg_a.intMember, "msg 10 content"),
            else => checker.softAssert(false, "msg 10 type"),
        }
        switch (msg_list[11]) {
            .EmptyMessage => |_| {},
            else => checker.softAssert(false, "msg 11 type"),
        }
    }

    const mem_result = gpa.deinit();
    checker.softAssert(mem_result == .ok, "memory leaks");

    checker.check();
}
