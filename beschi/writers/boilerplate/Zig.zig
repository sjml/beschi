fn _numberTypeIsValid(comptime T: type) bool {
    const validNumericTypes = [_]type{
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

pub fn readNumber(comptime T: type, offset: usize, buffer: []u8) struct { value: T, bytes_read: usize } {
    comptime {
        if (!_numberTypeIsValid(T)) {
            @compileError("Invalid number type");
        }
    }

    switch (T) {
        f32 => return .{ .value = @bitCast(std.mem.readInt(u32, buffer[offset..][0..@sizeOf(T)], .little)), .bytes_read = @sizeOf(T) },
        f64 => return .{ .value = @bitCast(std.mem.readInt(u64, buffer[offset..][0..@sizeOf(T)], .little)), .bytes_read = @sizeOf(T) },
        else => return .{ .value = std.mem.readInt(T, buffer[offset..][0..@sizeOf(T)], .little), .bytes_read = @sizeOf(T) },
    }
}

pub fn readString(allocator: std.mem.Allocator, offset: usize, buffer: []u8) !struct { value: []u8, bytes_read: usize } {
    const len_read = readNumber({# STRING_SIZE_TYPE #}, offset, buffer);
    const len = len_read.value;
    var str = try allocator.alloc(u8, len);
    for (0..len) |i| {
        str[i] = buffer[offset + len_read.bytes_read + i];
    }
    return .{ .value = str, .bytes_read = @sizeOf({# STRING_SIZE_TYPE #}) + len };
}

pub fn readList(comptime T: type, allocator: std.mem.Allocator, offset: usize, buffer: []u8) !struct { value: []T, bytes_read: usize } {
    var local_offset = offset;
    const len_read = readNumber({# LIST_SIZE_TYPE #}, local_offset, buffer);
    const len = len_read.value;
    local_offset += len_read.bytes_read;
    var list = try allocator.alloc(T, len);

    for (0..len) |i| {
        if (comptime _numberTypeIsValid(T)) {
            const list_read = readNumber(T, local_offset, buffer);
            list[i] = list_read.value;
            local_offset += list_read.bytes_read;
        } else {
            switch (T) {
                []u8 => {
                    const list_read = try readString(allocator, local_offset, buffer);
                    list[i] = list_read.value;
                    local_offset += list_read.bytes_read;
                },
                else => {
                    if (comptime _typeIsSimple(T)) {
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
    }
    return .{ .value = list, .bytes_read = local_offset - offset };
}
