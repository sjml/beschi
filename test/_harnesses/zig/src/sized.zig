const std = @import("std");
const Checker = @import("./util.zig").Checker;
const makeMutableSlice = @import("./util.zig").makeMutableSlice;

const sized = @import("lib/SizedMessage.zig");

const short_list = sized.TextContainer{
    .label = "list that fits in a byte",
    .collection = makeMutableSlice([_][]const u8{
        "Lorem",      "ipsum",     "dolor",        "sit",      "amet",      "consectetur",
        "adipiscing", "elit",      "sed",          "do",       "eiusmod",   "tempor",
        "incididunt", "ut",        "labore",       "et",       "dolore",    "magna",
        "aliqua",     "Ut",        "enim",         "ad",       "minim",     "veniam",
        "quis",       "nostrud",   "exercitation", "ullamco",  "laboris",   "nisi",
        "ut",         "aliquip",   "ex",           "ea",       "commodo",   "consequat",
        "Duis",       "aute",      "irure",        "dolor",    "in",        "reprehenderit",
        "in",         "voluptate", "velit",        "esse",     "cillum",    "dolore",
        "eu",         "fugiat",    "nulla",        "pariatur", "Excepteur", "sint",
        "occaecat",   "cupidatat", "non",          "proident", "sunt",      "in",
        "culpa",      "qui",       "officia",      "deserunt", "mollit",    "anim",
        "id",         "est",       "laborum",
    }),
};

pub fn main() !void {
    const args = try std.process.argsAlloc(std.heap.page_allocator);
    defer std.process.argsFree(std.heap.page_allocator, args);

    var gpa = std.heap.GeneralPurposeAllocator(.{}){};
    const testAllocator = gpa.allocator();

    var checker = Checker{};

    if (std.mem.eql(u8, args[1], "--generate")) {
        var buffer_size: usize = 0;
        buffer_size += short_list.getSizeInBytes();
        checker.softAssert(buffer_size == 464, "short list size calculation check");

        const buffer = try testAllocator.alloc(u8, buffer_size);
        defer testAllocator.free(buffer);

        const written = short_list.writeBytes(0, buffer, false);
        checker.softAssert(written == buffer_size, "written bytes check");

        var file = try std.fs.cwd().createFile(args[2], .{ .truncate = true });
        defer file.close();

        try file.writeAll(buffer);
    } else if (std.mem.eql(u8, args[1], "--read")) {
        var file = try std.fs.cwd().openFile(args[2], .{});
        defer file.close();

        const buffer = try file.readToEndAlloc(testAllocator, std.math.maxInt(u32));
        defer testAllocator.free(buffer);

        var input = (try sized.TextContainer.fromBytes(testAllocator, 0, buffer)).value;
        defer input.deinit(testAllocator);

        checker.softAssert(std.mem.eql(u8, input.label, short_list.label), "readback label comparison");
        checker.softAssert(input.collection.len == short_list.collection.len, "readback list length");
        for (0..input.collection.len) |i| {
            checker.softAssert(std.mem.eql(u8, input.collection[i], short_list.collection[i]), "short list comparison");
        }
    }

    const mem_result = gpa.deinit();
    checker.softAssert(mem_result == .ok, "memory leaks");

    checker.check();
}
