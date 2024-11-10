import argparse

from ..protocol import Protocol, Struct, Variable, Enum, NUMERIC_TYPE_SIZES
from ..writer import Writer
from .. import LIB_NAME, LIB_VERSION

LANGUAGE_NAME = "Zig"


class ZigWriter(Writer):
    language_name = LANGUAGE_NAME
    default_extension = ".zig"

    def __init__(self, p: Protocol, extra_args: dict[str,any] = {}):
        super().__init__(protocol=p)

        self.embed_protocol = extra_args["embed_protocol"]

        self.type_mapping["byte"] = "u8"
        self.type_mapping["bool"] = "bool"
        self.type_mapping["uint16"] = "u16"
        self.type_mapping["int16"] = "i16"
        self.type_mapping["uint32"] = "u32"
        self.type_mapping["int32"] = "i32"
        self.type_mapping["uint64"] = "u64"
        self.type_mapping["int64"] = "i64"
        self.type_mapping["float"] = "f32"
        self.type_mapping["double"] = "f64"
        self.type_mapping["string"] = "[]const u8"

        self.base_defaults: dict[str,str] = {
            "byte": "0",
            "bool": "false",
            "uint16": "0",
            "int16": "0",
            "uint32": "0",
            "int32": "0",
            "uint64": "0",
            "int64": "0",
            "float": "0.0",
            "double": "0.0",
            "string": '""',
        }

    def deserializer(self, var: Variable, accessor: str, parent_is_simple: bool, simple_offset: int):
        if parent_is_simple: # also means that *var* is simple because recursion!
            if var.vartype in NUMERIC_TYPE_SIZES:
                self.write_line(f"const {accessor}_{var.name} = (try readNumber({self.type_mapping[var.vartype]}, offset + {simple_offset}, buffer)).value;")
            elif var.vartype in self.protocol.enums:
                e = self.protocol.enums[var.vartype]
                self.write_line(f"const {accessor}_{var.name}_check = (try readNumber({self.type_mapping[e.encoding]}, offset + {simple_offset}, buffer)).value;")
                self.write_line(f"")
            else:
                self.write_line(f"const {accessor}_{var.name}_read = {var.vartype}.fromBytes({simple_offset}, buffer);")
                self.write_line(f"const {accessor}_{var.name} = {accessor}_{var.name}_read.value;")
        else:
            if var.is_list:
                self.write_line(f"const {accessor}_{var.name}_read = try readList({self.type_mapping[var.vartype]}, allocator, local_offset, buffer);")
                self.write_line(f"const {accessor}_{var.name} = {accessor}_{var.name}_read.value;")
                self.write_line(f"local_offset += {accessor}_{var.name}_read.bytes_read;")
            elif var.vartype in NUMERIC_TYPE_SIZES or var.vartype in self.protocol.enums:
                self.write_line(f"const {accessor}_{var.name}_read = try readNumber({self.type_mapping[var.vartype]}, local_offset, buffer);")
                self.write_line(f"const {accessor}_{var.name} = {accessor}_{var.name}_read.value;")
                self.write_line(f"local_offset += {accessor}_{var.name}_read.bytes_read;")
            elif var.vartype == "string":
                self.write_line(f"const {accessor}_{var.name}_read = try readString(allocator, local_offset, buffer);")
                self.write_line(f"const {accessor}_{var.name} = {accessor}_{var.name}_read.value;")
                self.write_line(f"local_offset += {accessor}_{var.name}_read.bytes_read;")
            else:
                self.write_line(f"const {accessor}_{var.name}_read = try {var.vartype}.fromBytes({'' if var.is_simple() else 'allocator, '}local_offset, buffer);")
                self.write_line(f"const {accessor}_{var.name} = {accessor}_{var.name}_read.value;")
                self.write_line(f"local_offset += {accessor}_{var.name}_read.bytes_read;")

            self.write_line()

    def serializer(self, var: Variable, accessor: str, parent_is_simple: bool, simple_offset: int):
        if parent_is_simple:
            if var.vartype in NUMERIC_TYPE_SIZES:
                self.write_line(f"_ = writeNumber({self.type_mapping[var.vartype]}, offset + {simple_offset}, buffer, {accessor}{var.name});")
        else:
            if var.is_list:
                self.write_line(f"local_offset += writeList({self.type_mapping[var.vartype]}, local_offset, buffer, {accessor}{var.name});")
            elif var.vartype in NUMERIC_TYPE_SIZES or var.vartype in self.protocol.enums:
                self.write_line(f"local_offset += writeNumber({self.type_mapping[var.vartype]}, local_offset, buffer, {accessor}{var.name});")
            elif var.vartype == "string":
                self.write_line(f"local_offset += writeString(local_offset, buffer, {accessor}{var.name});")
            else:
                self.write_line(f"local_offset += {accessor}{var.name}.writeBytes(local_offset, buffer);")




    def gen_measurement(self, st: Struct, accessor: str, depth: int) -> tuple[list[str], int]:
        lines: list[str] = []
        accum = 0

        if st.is_simple():
            lines.append(f"return {self.protocol.get_size_of(st.name)};")
            return lines, accum

        size_init = "var size: usize = 0;"
        lines.append(size_init)

        for var in st.members:
            if var.is_list:
                accum += NUMERIC_TYPE_SIZES[self.protocol.list_size_type]
                if var.is_simple(True):
                    lines.append(f"size += {accessor}{var.name}.len * {self.protocol.get_size_of(var.vartype)};")
                elif var.vartype == "string":
                    lines.append(f"for ({accessor}{var.name}) |s| {{")
                    lines.append(f"{self.tab}size += {NUMERIC_TYPE_SIZES[self.protocol.string_size_type]} + s.len;")
                    lines.append("}")
                else:
                    lines.append(f"for ({accessor}{var.name}) |el{depth}| {{")
                    clines, caccum = self.gen_measurement(self.protocol.structs[var.vartype], f"el{depth}.", depth + 1)
                    if clines[0] == size_init:
                        clines = clines[1:]
                    clines.append(f"size += {caccum};")
                    lines += [f"{self.tab}{l}" for l in clines]
                    lines.append("}")
            else:
                if var.is_simple():
                    accum += self.protocol.get_size_of(var.vartype)
                elif var.vartype == "string":
                    accum += NUMERIC_TYPE_SIZES[self.protocol.string_size_type]
                    lines.append(f"size += {accessor}{var.name}.len;")
                else:
                    clines, caccum = self.gen_measurement(self.protocol.structs[var.vartype], f"{accessor}{var.name}.", depth + 1)
                    if clines[0] == size_init:
                        clines = clines[1:]
                    lines += clines
                    accum += caccum
        return lines, accum

    def destructor(self, var: Variable, accessor: str):
        if var.is_simple():
            return
        elif var.is_list:
            if not var.is_simple(True):
                idx = self.indent_level
                self.write_line(f"for ({accessor}{var.name}) |{'*' if not var.vartype == 'string' else ''}item{idx}| {{")
                self.indent_level += 1
                inner = Variable(self.protocol, f"item{idx}", var.vartype)
                self.destructor(inner, "")
                self.indent_level -= 1
                self.write_line("}")
            self.write_line(f"allocator.free({accessor}{var.name});")
        elif var.vartype == "string":
            self.write_line(f"allocator.free({accessor}{var.name});")
        else:
            self.write_line(f"{accessor}{var.name}.deinit(allocator);")

    def gen_enum(self, ename: str, edata: Enum):
        self.write_line(f"pub const {ename} = enum({self.type_mapping[edata.encoding]}) {{")
        self.indent_level += 1
        for v, vi in edata.values.items():
            self.write_line(f"{v} = {vi},")
        self.indent_level -= 1
        self.write_line("};")
        self.write_line()

    def gen_struct(self, sname: str, sdata: Struct):
        self.write_line(f"pub const {sname} = struct {{")
        self.indent_level += 1
        for var in sdata.members:
            if var.is_list:
                self.write_line(f"{var.name}: []{self.type_mapping[var.vartype]} = &.{{}},")
            else:
                default_value = self.base_defaults.get(var.vartype)
                if default_value == None:
                    if var.vartype in self.protocol.enums:
                        e = self.protocol.enums[var.vartype]
                        default_value = f"{e.name}.{e.get_default_pair()[0]}"
                    else:
                        default_value = f"{var.vartype}{{}}"
                self.write_line(f"{var.name}: {self.type_mapping[var.vartype]} = {default_value},")
        self.write_line()

        self.write_line(f"pub fn getSizeInBytes(self: *const {sname}) usize {{")
        self.indent_level += 1
        if sdata.is_simple():
            self.write_line("_ = self;")
            self.write_line(f"return {self.protocol.get_size_of(sname)};")
        else:
            measure_lines, accumulator = self.gen_measurement(sdata, "self.", 0)
            [self.write_line(s) for s in measure_lines]
            if accumulator > 0:
                self.write_line(f"size += {accumulator};")
            self.write_line("return size;")
        self.indent_level -= 1
        self.write_line("}")
        self.write_line()

        self.write_line(f"pub fn fromBytes({'' if sdata.is_simple() else 'allocator: std.mem.Allocator, '}offset: usize, buffer: []const u8) !struct {{ value: {sname}, bytes_read: usize }} {{")
        self.indent_level += 1
        simple_offset = -1
        if len(sdata.members) == 0:
            self.write_line("_ = offset;")
            self.write_line("_ = buffer;")
        if sdata.is_simple():
            simple_offset = 0
        else:
            self.write_line("var local_offset = offset;")
            self.write_line()
        for mem in sdata.members:
            self.deserializer(mem, sname, sdata.is_simple(), simple_offset)
            if sdata.is_simple():
                simple_offset += self.protocol.get_size_of(mem.vartype)
        self.write_line(f"return .{{ .value = {sname}{{")
        self.indent_level += 1
        for var in sdata.members:
            self.write_line(f".{var.name} = {sname}_{var.name},")
        self.indent_level -= 1
        if sdata.is_simple():
            self.write_line(f"}}, .bytes_read = {self.protocol.get_size_of(sdata.name)} }};")
        else:
            self.write_line(f"}}, .bytes_read = local_offset - offset }};")
        self.indent_level -= 1
        self.write_line("}")
        self.write_line()

        if sdata.is_message:
            self.write_line(f"pub fn writeBytes(self: *const {sname}, offset: usize, buffer: []u8, tag: bool) usize {{")
            self.indent_level += 1
        else:
            self.write_line(f"pub fn writeBytes(self: *const {sname}, offset: usize, buffer: []u8) usize {{")
            self.indent_level += 1
        simple_offset = -1
        if len(sdata.members) == 0:
            self.write_line("_ = self;")
            if not sdata.is_message:
                self.write_line("_ = offset;")
        if sdata.is_simple():
            simple_offset = 0
            if sdata.is_message:
                self.write_line("var local_offset = offset;")
                self.write_line()
                self.write_line("if (tag) {")
                self.indent_level += 1
                msg_type_id = list(self.protocol.messages.keys()).index(sname) + 1
                self.write_line(f"local_offset += writeNumber(u8, local_offset, buffer, {msg_type_id});")
                self.indent_level -= 1
                self.write_line("}")
                simple_offset += 1
        else:
            self.write_line("var local_offset = offset;")
            if sdata.is_message:
                self.write_line("if (tag) {")
                self.indent_level += 1
                msg_type_id = list(self.protocol.messages.keys()).index(sname) + 1
                self.write_line(f"local_offset += writeNumber(u8, local_offset, buffer, {msg_type_id});")
                self.indent_level -= 1
                self.write_line("}")
            self.write_line()
        for mem in sdata.members:
            self.serializer(mem, "self.", sdata.is_simple() and not sdata.is_message, simple_offset)
            if sdata.is_simple():
                simple_offset += self.protocol.get_size_of(mem.vartype)
        if sdata.is_simple() and not sdata.is_message:
            self.write_line(f"return {simple_offset};")
        else:
            self.write_line()
            self.write_line(f"return local_offset - offset;")

        self.indent_level -= 1
        self.write_line("}")

        if not sdata.is_simple():
            self.write_line()
            self.write_line(f"pub fn deinit(self: *{sname}, allocator: std.mem.Allocator) void {{")
            self.indent_level += 1
            [self.destructor(mem, "self.") for mem in sdata.members]
            self.indent_level -= 1
            self.write_line("}")

        self.indent_level -= 1
        self.write_line("};")
        self.write_line()



    def generate(self) -> str:
        self.output = []

        self.write_line(f"// This file was automatically generated by {LIB_NAME} v{LIB_VERSION}")
        self.write_line( "// <https://github.com/sjml/beschi>")
        self.write_line(f"// Do not edit directly.")
        self.write_line()

        if self.embed_protocol:
            self.write_line("// DATA PROTOCOL")
            self.write_line("// -----------------")
            [self.write_line(f"// {l}") for l in self.protocol.protocol_string.splitlines()]
            self.write_line("// -----------------")
            self.write_line("// END DATA PROTOCOL")
            self.write_line()
            self.write_line()

        self.write_line("const std = @import(\"std\");")
        self.write_line()

        simple_structs  = [sname for sname, sdata in self.protocol.structs.items()  if sdata.is_simple()]
        simple_messages = [mname for mname, mdata in self.protocol.messages.items() if mdata.is_simple()]
        simpletons = simple_structs + simple_messages
        enum_types = [e.name for e in self.protocol.enums.values()]

        subs = [
            ("{# STRING_SIZE_TYPE #}", self.get_native_string_size()),
            ("{# LIST_SIZE_TYPE #}"  , self.get_native_list_size()),
            ("{# SIMPLE_TYPES #}", f"{', '.join(simpletons)}{',' if len(simpletons) > 0 else ''}"),
            ("{# ENUM_TYPES #}", f"{', '.join(enum_types)}{',' if len(enum_types) > 0 else ''}"),
        ]
        self.add_boilerplate(subs)
        self.write_line()

        self.write_line("pub const MessageType = enum(u8) {")
        self.indent_level += 1
        for mname in self.protocol.messages:
            self.write_line(f"{mname},")
        self.indent_level -= 1
        self.write_line("};")
        self.write_line()
        self.write_line("pub const Message = union(MessageType) {")
        self.indent_level += 1
        for mname in self.protocol.messages:
            self.write_line(f"{mname}: {mname},")
        self.indent_level -= 1
        self.write_line("};")
        self.write_line()

        self.write_line("pub fn processRawBytes(allocator: std.mem.Allocator, buffer: []const u8) ![]Message {")
        self.indent_level += 1
        self.write_line("var msg_list = std.ArrayList(Message).init(allocator);")
        self.write_line("defer msg_list.deinit();")
        self.write_line();
        self.write_line("var local_offset: usize = 0;")
        self.write_line("while (local_offset < buffer.len) {")
        self.indent_level += 1
        self.write_line("const msg_type_byte = (try readNumber(u8, local_offset, buffer)).value;")
        self.write_line("local_offset += 1;")
        self.write_line("if (msg_type_byte == 0) {")
        self.indent_level += 1
        self.write_line("return msg_list.toOwnedSlice();")
        self.indent_level -= 1
        self.write_line("}")
        self.write_line("const msg_type: MessageType = std.meta.intToEnum(MessageType, msg_type_byte - 1) catch return DataReaderError.InvalidData;")
        self.write_line("switch(msg_type) {")
        self.indent_level += 1
        for mname, mdata in self.protocol.messages.items():
            self.write_line(f".{mname} => {{")
            self.indent_level += 1
            if mdata.is_simple():
                self.write_line(f"const msg_read = try {mname}.fromBytes(local_offset, buffer);")
            else:
                self.write_line(f"const msg_read = try {mname}.fromBytes(allocator, local_offset, buffer);")
            self.write_line("local_offset += msg_read.bytes_read;")
            self.write_line(f"try msg_list.append(Message{{ .{mname} = msg_read.value }});")
            self.indent_level -= 1
            self.write_line("},")
        self.indent_level -= 1
        self.write_line("}")
        self.indent_level -= 1
        self.write_line("}")
        self.write_line("return msg_list.toOwnedSlice();")
        self.indent_level -= 1
        self.write_line("}")
        self.write_line()

        for ename, edata in self.protocol.enums.items():
            self.gen_enum(ename, edata)

        for sname, sdata in self.protocol.structs.items():
            self.gen_struct(sname, sdata)

        for mname, mdata in self.protocol.messages.items():
            self.gen_struct(mname, mdata)


        self.write_line()
        assert self.indent_level == 0

        return "\n".join(self.output)
