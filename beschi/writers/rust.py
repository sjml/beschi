import argparse

from ..protocol import Protocol, Struct, Variable, NUMERIC_TYPE_SIZES
from ..writer import Writer, TextUtil
from .. import LIB_NAME, LIB_VERSION

LANGUAGE_NAME = "Rust"


class RustWriter(Writer):
    language_name = LANGUAGE_NAME
    default_extension = ".rs"

    def get_additional_args(parser: argparse.ArgumentParser):
        group = parser.add_argument_group(LANGUAGE_NAME)
        group.add_argument("--rust-no-rename", action="store_const", const=True, default=False, help="don't rename data members to snake_case")

    def __init__(self, p: Protocol, extra_args: dict[str,any] = {}):
        rename = not extra_args["rust_no_rename"]

        if rename:
            for _, s in p.structs.items():
                for var in s.members:
                    var.name = TextUtil.convert_to_lower_snake_case(var.name)
            for _, m in p.messages.items():
                for var in m.members:
                    var.name = TextUtil.convert_to_lower_snake_case(var.name)

        super().__init__(protocol=p, tab="    ")

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
        self.type_mapping["string"] = "String"

    def deserializer(self, var: Variable, accessor: str):
        if var.is_list:
            self.write_line(f"let {var.name}_len = reader.read_{self.get_native_list_size()}()?;")
            if var.vartype in self.type_mapping:
                self.write_line(f"let mut {var.name}: Vec<{self.type_mapping[var.vartype]}> = Vec::new();")
            else:
                self.write_line(f"let mut {var.name}: Vec<{var.vartype}> = Vec::new();")
            self.write_line(f"for _ in 0..{var.name}_len {{")
            self.indent_level += 1
            inner = Variable(self.protocol, "el", var.vartype)
            self.deserializer(inner, "");
            self.write_line(f"{var.name}.push(el);")
            self.indent_level -= 1
            self.write_line("}")
        elif var.vartype in NUMERIC_TYPE_SIZES:
            if var.vartype == "byte":
                self.write_line(f"let {var.name} = reader.take_byte()?;")
            elif var.vartype == "bool":
                self.write_line(f"let {var.name} = reader.take_byte()? > 0;")
            else:
                self.write_line(f"let {var.name} = reader.read_{self.type_mapping[var.vartype]}()?;")
        elif var.vartype == "string":
            self.write_line(f"let {var.name} = reader.read_string()?;")
        else:
            self.write_line(f"let {var.name} = {var.vartype}::from_bytes(reader)?;")

    def serializer(self, var: Variable, accessor: str):
        if var.is_list:
            self.write_line(f"writer.extend(({accessor}{var.name}.len() as {self.get_native_list_size()}).to_le_bytes());")
            self.write_line(f"for el in &{accessor}{var.name} {{")
            self.indent_level += 1
            inner = Variable(self.protocol, "el", var.vartype)
            self.serializer(inner, "")
            self.indent_level -= 1
            self.write_line("}")
        elif var.vartype in NUMERIC_TYPE_SIZES:
            if var.vartype == "byte":
                self.write_line(f"writer.push({accessor}{var.name});")
            elif var.vartype == "bool":
                self.write_line(f"writer.push(if {accessor}{var.name} {{1_u8}} else {{0_u8}});")
            else:
                self.write_line(f"writer.extend({accessor}{var.name}.to_le_bytes());")
        elif var.vartype == "string":
            self.write_line(f"writer.extend(({accessor}{var.name}.len() as {self.get_native_string_size()}).to_le_bytes());")
            self.write_line(f"writer.extend({accessor}{var.name}.as_bytes());")
        else:
            self.write_line(f"{accessor}{var.name}.write_bytes(writer);")

    def gen_measurement(self, st: Struct, accessor: str = "") -> tuple[list[str], int]:
        lines: list[str] = []
        accum = 0

        if st.is_simple():
            lines.append(f"{self.protocol.get_size_of(st.name)}")
        else:
            size_init = "let mut size: u32 = 0;"
            lines.append(size_init)

            for var in st.members:
                if var.is_list:
                    accum += NUMERIC_TYPE_SIZES[self.protocol.list_size_type]
                    if var.is_simple(True):
                        lines.append(f"size += ({accessor}{var.name}.len() as u32) * {self.protocol.get_size_of(var.vartype)};")
                    elif var.vartype == "string":
                        lines.append(f"for s in &{accessor}{var.name} {{")
                        lines.append(f"{self.tab}size += {NUMERIC_TYPE_SIZES[self.protocol.string_size_type]} + (s.len() as u32);")
                        lines.append("}")
                    else:
                        lines.append(f"for el in &{accessor}{var.name} {{")
                        clines, caccum = self.gen_measurement(self.protocol.structs[var.vartype], f"el.")
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
                        lines.append(f"size += {accessor}{var.name}.len() as u32;")
                    else:
                        clines, caccum = self.gen_measurement(self.protocol.structs[var.vartype], f"{accessor}{var.name}.")
                        if clines[0] == size_init:
                            clines = clines[1:]
                        lines += clines
                        accum += caccum
        return lines, accum

    def gen_struct(self, sname: str, sdata: Struct):
        self.write_line("#[derive(Default)]")
        self.write_line(f"pub struct {sname} {{")
        self.indent_level += 1
        for var in sdata.members:
            if var.is_list:
                if var.vartype in self.type_mapping:
                    self.write_line(f"pub {var.name}: Vec<{self.type_mapping[var.vartype]}>,")
                else:
                    self.write_line(f"pub {var.name}: Vec<{var.vartype}>,")
            elif var.vartype in self.type_mapping:
                self.write_line(f"pub {var.name}: {self.type_mapping[var.vartype]},")
            else:
                self.write_line(f"{var.name}: {var.vartype},")
        self.indent_level -= 1
        self.write_line("}")

        self.write_line(f"impl {sname} {{")
        self.indent_level += 1

        self.write_line("pub fn get_size_in_bytes(&self) -> u32 {")
        self.indent_level += 1
        measure_lines, accumulator = self.gen_measurement(sdata, "self.")
        [self.write_line(s) for s in measure_lines]
        if accumulator > 0:
            self.write_line(f"size += {accumulator};")
        if len(measure_lines) > 1:
            self.write_line("size")
        self.indent_level -= 1
        self.write_line("}")

        self.write_line(f"pub fn from_bytes({'_' if len(sdata.members) == 0 else ''}reader: &mut BufferReader) -> Result<{sname}, {self.prefix}Error> {{")
        self.indent_level += 1
        [self.deserializer(mem, "") for mem in sdata.members]
        varnames = [mem.name for mem in sdata.members]
        self.write_line(f"Ok({sname} {{{', '.join(varnames)}}})")
        self.indent_level -= 1
        self.write_line("}")

        if sdata.is_message:
            self.write_line("pub fn write_bytes(&self, writer: &mut Vec<u8>, tag: bool) {")
            self.indent_level += 1
            self.write_line("if tag {")
            self.indent_level += 1
            msg_type_id = list(self.protocol.messages.keys()).index(sname) + 1
            self.write_line(f"writer.push({msg_type_id}_u8);")
            self.indent_level -= 1
            self.write_line("}")
        else:
            self.write_line("pub fn write_bytes(&self, writer: &mut Vec<u8>) {")
            self.indent_level += 1
        [self.serializer(mem, "self.") for mem in sdata.members]
        self.indent_level -= 1
        self.write_line("}")
        self.indent_level -= 1

        self.write_line("}")
        self.write_line()

    def generate(self) -> str:
        self.output = []
        self.write_line(f"// This file was automatically generated by {LIB_NAME} v{LIB_VERSION}")
        self.write_line( "// <https://github.com/sjml/beschi>")
        self.write_line(f"// Do not edit directly.")
        self.write_line()

        if self.embed_protocol:
            self.write_line("/*")
            self.write_line("DATA PROTOCOL")
            self.write_line("-----------------")
            [self.write_line(f"{l}") for l in self.protocol.protocol_string.splitlines()]
            self.write_line("-----------------")
            self.write_line("END DATA PROTOCOL")
            self.write_line("*/")
            self.write_line()
            self.write_line()

        subs = [("{# STRING_SIZE_TYPE #}", self.get_native_string_size())]
        self.prefix = "Beschi"
        if self.protocol.namespace != None:
            subs.append(("Beschi", self.protocol.namespace))
            self.prefix = self.protocol.namespace
        self.add_boilerplate(substitutions=subs)

        self.write_line("pub enum Message {")
        self.indent_level += 1
        for mname in self.protocol.messages:
           self.write_line(f"{mname}({mname}),")
        self.indent_level -= 1
        self.write_line("}")
        self.write_line()

        self.write_line(f"pub fn process_raw_bytes(reader: &mut BufferReader) -> Result<Vec<Message>, {self.prefix}Error> {{")
        self.indent_level += 1
        self.write_line("let mut msg_list: Vec<Message> = Vec::new();")
        self.write_line("while !reader.is_finished() {")
        self.indent_level += 1
        self.write_line("let msg_type = reader.take_byte()?;")
        self.write_line("match msg_type {")
        self.indent_level += 1
        for i, k in enumerate(self.protocol.messages.keys()):
            self.write_line(f"{i+1} => msg_list.push(Message::{k}({k}::from_bytes(reader)?)),")
        self.write_line(f"_ => return Err({self.prefix}Error::InvalidData),")
        self.indent_level -= 1
        self.write_line("}")
        self.indent_level -= 1
        self.write_line("}")
        self.write_line("Ok(msg_list)")
        self.indent_level -= 1
        self.write_line("}")

        for sname, sdata in self.protocol.structs.items():
            self.gen_struct(sname, sdata)

        for mname, mdata in self.protocol.messages.items():
            self.gen_struct(mname, mdata)

        return "\n".join(self.output)
