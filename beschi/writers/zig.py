import argparse

from ..protocol import Protocol, Struct, Variable, NUMERIC_TYPE_SIZES
from ..writer import Writer
from .. import LIB_NAME, LIB_VERSION

LANGUAGE_NAME = "Zig"


class ZigWriter(Writer):
    language_name = LANGUAGE_NAME
    default_extension = ".zig"
    in_progress = True

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
        }

    def deserializer(self, var: Variable, accessor: str, parent_is_simple: bool, simple_offset: int):
        if parent_is_simple: # also means that *var* is simple because recursion!
            if var.vartype in NUMERIC_TYPE_SIZES.keys():
                self.write_line(f"const {accessor}_{var.name} = readNumber({self.type_mapping[var.vartype]}, offset + {simple_offset}, buffer).value;")
            else:
                self.write_line(f"const {accessor}_{var.name}_read = {var.vartype}.fromBytes({simple_offset}, buffer);")
                self.write_line(f"const {accessor}_{var.name} = {accessor}_{var.name}_read.value;")
        else:
            if var.is_list:
                self.write_line(f"const {accessor}_{var.name}_read = try readList({self.type_mapping[var.vartype]}, allocator, local_offset, buffer);")
                self.write_line(f"const {accessor}_{var.name} = {accessor}_{var.name}_read.value;")
                self.write_line(f"local_offset += {accessor}_{var.name}_read.bytes_read;")
            elif var.vartype in NUMERIC_TYPE_SIZES.keys():
                self.write_line(f"const {accessor}_{var.name}_read = readNumber({self.type_mapping[var.vartype]}, local_offset, buffer);")
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
            if var.vartype in NUMERIC_TYPE_SIZES.keys():
                self.write_line(f"_ = writeNumber({self.type_mapping[var.vartype]}, offset + {simple_offset}, buffer, {accessor}{var.name});")
        else:
            if var.is_list:
                self.write_line(f"local_offset += writeList({self.type_mapping[var.vartype]}, local_offset, buffer, {accessor}{var.name});")
            elif var.vartype in NUMERIC_TYPE_SIZES.keys():
                self.write_line(f"local_offset += writeNumber({self.type_mapping[var.vartype]}, local_offset, buffer, {accessor}{var.name});")
            elif var.vartype == "string":
                self.write_line(f"local_offset += writeString(local_offset, buffer, {accessor}{var.name});")
            else:
                self.write_line(f"local_offset += {accessor}{var.name}.writeBytes(local_offset, buffer);")




    def gen_measurement(self, st: Struct, accessor: str = "") -> tuple[list[str], int]:
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
                    lines.append(f"for ({accessor}{var.name}) |el| {{")
                    clines, caccum = self.gen_measurement(self.protocol.structs[var.vartype], "el.")
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
                    clines, caccum = self.gen_measurement(self.protocol.structs[var.vartype], f"{accessor}{var.name}.")
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

    def gen_struct(self, sname: str, sdata: Struct):
        self.write_line(f"pub const {sname} = struct {{")
        self.indent_level += 1
        for var in sdata.members:
            if var.is_list:
                self.write_line(f"{var.name}: []{self.type_mapping[var.vartype]},")
            else:
                default_value = self.base_defaults.get(var.vartype)
                if default_value == None:
                    if var.is_simple():
                        default_value = f"{var.vartype}{{}}"
                    else:
                        default_value = None
                if default_value != None:
                    self.write_line(f"{var.name}: {self.type_mapping[var.vartype]} = {default_value},")
                else:
                    self.write_line(f"{var.name}: {self.type_mapping[var.vartype]},")
        self.write_line()

        self.write_line(f"pub fn getSizeInBytes(self: *const {sname}) usize {{")
        self.indent_level += 1
        if sdata.is_simple():
            self.write_line("_ = self;")
            self.write_line(f"return {self.protocol.get_size_of(sname)};")
        else:
            measure_lines, accumulator = self.gen_measurement(sdata, "self.")
            [self.write_line(s) for s in measure_lines]
            if accumulator > 0:
                self.write_line(f"size += {accumulator};")
            self.write_line("return size;")
        self.indent_level -= 1
        self.write_line("}")
        self.write_line()

        self.write_line(f"pub fn fromBytes({'' if sdata.is_simple() else 'allocator: std.mem.Allocator, '}offset: usize, buffer: []u8) !struct {{ value: {sname}, bytes_read: usize }} {{")
        self.indent_level += 1
        simple_offset = -1
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
        if sdata.is_simple():
            simple_offset = 0
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
            self.serializer(mem, "self.", sdata.is_simple(), simple_offset)
            if sdata.is_simple():
                simple_offset += self.protocol.get_size_of(mem.vartype)
        if sdata.is_simple():
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

        self.write_line( "fn _typeIsSimple(comptime T: type) bool {")
        self.write_line( "    if (comptime _numberTypeIsValid(T)) {")
        self.write_line( "        return true;")
        self.write_line( "    }")
        self.write_line( "    const simpleTypes = [_]type{")
        simple_structs  = [sname for sname, sdata in self.protocol.structs.items()  if sdata.is_simple()]
        simple_messages = [mname for mname, mdata in self.protocol.messages.items() if mdata.is_simple()]
        if len(simple_structs):
            self.write_line(f"        {', '.join(simple_structs )},")
        if len(simple_messages):
            self.write_line(f"        {', '.join(simple_messages)},")
        self.write_line( "    };")
        self.write_line( "    for (simpleTypes) |vt| {")
        self.write_line( "        if (T == vt) {")
        self.write_line( "            return true;")
        self.write_line( "        }")
        self.write_line( "    }")
        self.write_line( "    return false;")
        self.write_line( "}")
        self.write_line()

        subs = [
            ("{# STRING_SIZE_TYPE #}", self.get_native_string_size()),
            ("{# LIST_SIZE_TYPE #}"  , self.get_native_list_size()),
        ]
        self.add_boilerplate(subs)
        self.write_line()

        for sname, sdata in self.protocol.structs.items():
            self.gen_struct(sname, sdata)

        for mname, mdata in self.protocol.messages.items():
            self.gen_struct(mname, mdata)


        self.write_line()
        assert self.indent_level == 0

        return "\n".join(self.output)
