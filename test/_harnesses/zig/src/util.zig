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
