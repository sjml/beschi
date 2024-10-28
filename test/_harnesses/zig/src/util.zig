const std = @import("std");

pub const Checker = struct {
    ok: bool = true,

    pub fn softAssert(self: *Checker, condition: bool, label: []const u8) void {
        if (!condition) {
            std.debug.print("FAILED! Zig: {s}\n", .{label});
            self.ok = false;
        }
    }

    pub fn check(self: *Checker) void {
        if (!self.ok) {
            std.debug.print("Failed assertions.\n", .{});
            std.process.exit(1);
        }
    }
};

pub fn makeMutableSlice(comptime data: anytype) []@TypeOf(data[0]) {
    const S = struct {
        var array: [data.len]@TypeOf(data[0]) = data;
    };
    return &S.array;
}
