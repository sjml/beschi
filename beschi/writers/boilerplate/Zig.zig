const DataReaderError = error {
    EOF,
    InvalidData,
};

fn numberTypeIsValid(comptime T: type) bool {
    const validNumericTypes = [_]type{
        bool,
        u8,  i8,
        u16, i16,
        u32, i32,
        u64, i64,
        f32, f64,
    };
    for (validNumericTypes) |vt| {
        if (T == vt) {
            return true;
        }
    }
    return false;
}

const simpleTypes = [_]type{
    {# SIMPLE_TYPES #}
};

const enumTypes = [_]type{
    {# ENUM_TYPES #}
};

fn typeIsSimple(comptime T: type) bool {
    if (comptime numberTypeIsValid(T)) {
        return true;
    }
    for (simpleTypes) |vt| {
        if (T == vt) {
            return true;
        }
    }
    if (typeIsEnum(T)) {
        return true;
    }
    return false;
}

fn typeIsEnum(comptime T: type) bool {
    for (enumTypes) |vt| {
        if (T == vt) {
            return true;
        }
    }
    return false;
}

fn isValidEnum(comptime Te: type, comptime Ti: type, value: Ti) bool {
    inline for (std.meta.fields(Te)) |f| {
        if (value == f.value) {
            return true;
        }
    }
    return false;
}

pub fn readNumber(comptime T: type, offset: usize, buffer: []const u8) !struct { value: T, bytes_read: usize } {
    comptime {
        const actual_type = switch (@typeInfo(T)) {
            .Enum => |enum_info| enum_info.tag_type,
            else => T,
        };

        if (!numberTypeIsValid(actual_type)) {
            @compileError("Invalid number type");
        }
    }

    if (offset + @sizeOf(T) > buffer.len) {
        return DataReaderError.EOF;
    }

    const val: T = switch (T) {
        f32 => @bitCast(std.mem.readInt(u32, buffer[offset..][0..@sizeOf(T)], .little)),
        f64 => @bitCast(std.mem.readInt(u64, buffer[offset..][0..@sizeOf(T)], .little)),
        bool => std.mem.readInt(u8, buffer[offset..][0..@sizeOf(T)], .little) != 0,
        else => enum_conversion: {
            break :enum_conversion switch (@typeInfo(T)) {
                .Enum => |ei| {
                    const raw = std.mem.readInt(ei.tag_type, buffer[offset..][0..@sizeOf(T)], .little);
                    if (!isValidEnum(T, ei.tag_type, raw)) {
                        return DataReaderError.InvalidData;
                    }
                    break :enum_conversion @enumFromInt(raw);
                },
                else => std.mem.readInt(T, buffer[offset..][0..@sizeOf(T)], .little),
            };
        },
    };

    return .{ .value = val, .bytes_read = @sizeOf(T) };
}

pub fn readString(allocator: std.mem.Allocator, offset: usize, buffer: []const u8) !struct { value: []u8, bytes_read: usize } {
    const len_read = try readNumber({# STRING_SIZE_TYPE #}, offset, buffer);
    const len = len_read.value;

    if (offset + @sizeOf({# STRING_SIZE_TYPE #}) + len > buffer.len) {
        return DataReaderError.EOF;
    }

    var str = try allocator.alloc(u8, len);
    for (0..len) |i| {
        str[i] = buffer[offset + len_read.bytes_read + i];
    }
    return .{ .value = str, .bytes_read = @sizeOf({# STRING_SIZE_TYPE #}) + len };
}

pub fn readList(comptime T: type, allocator: std.mem.Allocator, offset: usize, buffer: []const u8) !struct { value: []T, bytes_read: usize } {
    var local_offset = offset;
    const len_read = try readNumber({# LIST_SIZE_TYPE #}, local_offset, buffer);
    const len = len_read.value;
    local_offset += len_read.bytes_read;
    var list = try allocator.alloc(T, len);
    var made_count: {# LIST_SIZE_TYPE #} = 0;

    errdefer {
        for (0..made_count) |i| {
            if (comptime (numberTypeIsValid(T) or typeIsEnum(T))) {
                // no-op; just keeping the same structure as below
            }
            else {
                switch (T) {
                    []u8, []const u8 => {
                        allocator.free(list[i]);
                    },
                    else => {
                        if (comptime typeIsSimple(T)) {
                            // no-op
                        }
                        else {
                            list[i].deinit(allocator);
                        }
                    }
                }
            }
        }
        allocator.free(list);
    }

    for (0..len) |i| {
        if (comptime (numberTypeIsValid(T) or typeIsEnum(T))) {
            const list_read = try readNumber(T, local_offset, buffer);
            list[i] = list_read.value;
            local_offset += list_read.bytes_read;
        } else {
            switch (T) {
                []u8, []const u8 => {
                    const list_read = try readString(allocator, local_offset, buffer);
                    list[i] = list_read.value;
                    local_offset += list_read.bytes_read;
                },
                else => {
                    if (comptime typeIsSimple(T)) {
                        const list_read = try T.fromBytes(local_offset, buffer);
                        list[i] = list_read.value;
                        local_offset += list_read.bytes_read;
                    }
                    else {
                        const list_read = try T.fromBytes(allocator, local_offset, buffer);
                        list[i] = list_read.value;
                        local_offset += list_read.bytes_read;
                    }
                },
            }
        }
        made_count += 1;
    }
    return .{ .value = list, .bytes_read = local_offset - offset };
}

pub fn writeNumber(comptime T: type, offset: usize, buffer: []u8, value: T) usize {
    comptime {
        const actual_type = switch (@typeInfo(T)) {
            .Enum => |enum_info| enum_info.tag_type,
            else => T,
        };

        if (!numberTypeIsValid(actual_type)) {
            @compileError("Invalid number type");
        }
    }

    const slice = buffer[offset..][0..@sizeOf(T)];
    switch (T) {
        f32 => std.mem.writeInt(u32, @constCast(slice), @bitCast(value), .little),
        f64 => std.mem.writeInt(u64, @constCast(slice), @bitCast(value), .little),
        bool => std.mem.writeInt(u8, @constCast(slice), @intFromBool(value), .little),
        else => switch (@typeInfo(T)) {
            .Enum => |ei| std.mem.writeInt(ei.tag_type, @constCast(slice), @intFromEnum(value), .little),
            else => std.mem.writeInt(T, @constCast(slice), value, .little),
        }
    }
    return @sizeOf(T);
}

pub fn writeString(offset: usize, buffer: []u8, value: []const u8) usize {
    _ = writeNumber({# LIST_SIZE_TYPE #}, offset, buffer, @intCast(value.len));
    std.mem.copyForwards(u8, buffer[offset+@sizeOf({# LIST_SIZE_TYPE #})..][0..value.len], value);
    return @sizeOf({# LIST_SIZE_TYPE #}) + value.len;
}

pub fn writeList(comptime T: type, offset: usize, buffer: []u8, value: []T) usize {
    var local_offset = offset;
    local_offset += writeNumber({# LIST_SIZE_TYPE #}, local_offset, buffer, @intCast(value.len));

    for (value) |item| {
        if (comptime (numberTypeIsValid(T) or typeIsEnum(T))) {
            local_offset += writeNumber(T, local_offset, buffer, item);
        }
        else {
            switch(T) {
                []u8, []const u8 => {
                    local_offset += writeString(local_offset, buffer, item);
                },
                else => {
                    local_offset += item.writeBytes(local_offset, buffer);
                }
            }
        }
    }
    return local_offset - offset;
}

pub fn writeBytes(m: *const Message, offset: usize, buffer: []u8, tag: bool) usize {
    switch (m.*) {
        inline else => |inner| return inner.writeBytes(offset, buffer, tag),
    }
}

pub fn getPackedSize(msg_list: []const Message) usize {
    var size: usize = 0;
    for (msg_list) |msg| {
        size += msg.getSizeInBytes();
    }
    size += msg_list.len;
    size += 9;
    return size;
}

pub fn packMessages(msg_list: []const Message, buffer: []u8) void {
    const header_bytes = "BSCI";
    var offset: usize = 0;

    for (header_bytes) |b| {
        offset += writeNumber(u8, offset, buffer, b);
    }
    offset += writeNumber(u32, offset, buffer, @intCast(msg_list.len));

    for (msg_list) |msg| {
        offset += msg.writeBytes(offset, buffer, true);
    }

    offset += writeNumber(u8, offset, buffer, 0);
}

pub fn unpackMessages(allocator: std.mem.Allocator, buffer: []u8) ![]Message {
    var offset: usize = 0;
    if (!std.mem.eql(u8, buffer[0..4], "BSCI")) {
        return DataReaderError.InvalidData;
    }
    offset += 4;
    const msg_count_read = try readNumber(u32, 4, buffer);
    offset += msg_count_read.bytes_read;
    const msg_count = msg_count_read.value;
    if (msg_count == 0) {
        return allocator.alloc(Message, 0);
    }
    const msg_list = try processRawBytes(allocator, buffer[offset..], @intCast(msg_count));
    errdefer allocator.free(msg_list);

    if (msg_list.len == 0) {
        return DataReaderError.InvalidData;
    }
    if (msg_list.len != msg_count) {
        return DataReaderError.InvalidData;
    }
    return msg_list;
}
