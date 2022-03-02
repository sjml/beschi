import copy
from collections import OrderedDict

from ..protocol import Protocol, BASE_TYPE_SIZES
from ..writer import Writer, TextUtil
from .. import LIB_NAME, LIB_VERSION

LANGUAGE_NAME = "Rust"


class RustWriter(Writer):
    language_name = LANGUAGE_NAME
    default_extension = ".rs"
    in_progress = True

    def __init__(self, p: Protocol):
        p2 = copy.deepcopy(p)
        nstructs = OrderedDict()
        nstructs = OrderedDict()
        for s in p2.structs:
            v = []
            for vdata in p2.structs[s]:
                v.append( (TextUtil.convert_to_lower_snake_case(vdata[0]), vdata[1]) )
            nstructs[s] = v
        p2.structs = nstructs

        nmessages = OrderedDict()
        for m in p2.messages:
            v = []
            for vdata in p2.messages[m]:
                v.append( (TextUtil.convert_to_lower_snake_case(vdata[0]), vdata[1]) )
            nmessages[m] = v
        p2.messages = nmessages

        super().__init__(protocol=p2, tab="    ")

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

    def serializer(self, varname: str, vartype: str, accessor: str):
        if vartype in BASE_TYPE_SIZES.keys():
            if vartype == "byte":
                self.write_line(f"writer.push({accessor}{varname});")
            elif vartype == "bool":
                self.write_line(f"writer.push({accessor}{varname} as u8);")
            else:
                self.write_line(f"writer.extend({accessor}{varname}.to_le_bytes());")
        elif vartype == "string":
            self.write_line(f"writer.extend(({accessor}{varname}.len() as u32).to_le_bytes());")
            self.write_line(f"writer.extend({accessor}{varname}.as_bytes());")
        elif vartype[0] == "[" and vartype[-1] == "]":
            listed_type = vartype[1:-1]
            self.write_line(f"writer.extend(({accessor}{varname}.len() as u32).to_le_bytes());")
            self.write_line(f"for el in {accessor}{varname} {{")
            self.indent_level += 1
            self.serializer("el", listed_type, "")
            self.indent_level -= 1
            self.write_line("}")
        else:
            self.write_line(f"{accessor}{varname}.write_bytes(writer);")


    def deserializer(self, varname: str, vartype: str, accessor: str):
        if vartype in BASE_TYPE_SIZES.keys():
            if vartype == "byte":
                self.write_line(f"let {varname} = reader.take_byte()?;")
            elif vartype == "bool":
                self.write_line(f"let {varname} = reader.take_byte()? > 0;")
            else:
                self.write_line(f"let {varname} = reader.read_{self.type_mapping[vartype]}()?;")
        elif vartype == "string":
            self.write_line(f"let {varname} = reader.read_string()?;")
        elif vartype[0] == "[" and vartype[-1] == "]":
            listed_type = vartype[1:-1]
            self.write_line(f"let {varname}_len = reader.read_u32()?;")
            if listed_type in self.type_mapping.keys():
                self.write_line(f"let mut {varname}: Vec<{self.type_mapping[listed_type]}> = Vec::new();")
            else:
                self.write_line(f"let mut {varname}: Vec<{listed_type}> = Vec::new();")
            self.write_line(f"for _ in 0..{varname}_len {{")
            self.indent_level += 1
            self.deserializer("el", listed_type, "");
            self.write_line(f"{varname}.push(el);")
            self.indent_level -= 1
            self.write_line("}")
        else:
            self.write_line(f"let {varname} = {vartype}::from_bytes(reader)?;")

    def gen_struct(self, sname: str, members: list[tuple[str,str]], is_message: bool = False):
        self.write_line("#[derive(Default)]")
        self.write_line(f"pub struct {sname} {{")
        self.indent_level += 1
        for member_name, member_type in members:
            if member_type[0] == "[" and member_type[-1] == "]":
                listed_type = member_type[1:-1]
                if listed_type in BASE_TYPE_SIZES.keys() or listed_type == "string":
                    self.write_line(f"pub {member_name}: Vec<{self.type_mapping[listed_type]}>,")
                else:
                    self.write_line(f"pub {member_name}: Vec<{listed_type}>,")
            elif member_type in self.type_mapping:
                self.write_line(f"pub {member_name}: {self.type_mapping[member_type]},")
            else:
                self.write_line(f"{member_name}: {member_type},")

        self.indent_level -= 1
        self.write_line("}")

        self.write_line(f"impl {sname} {{")
        self.indent_level += 1
        self.write_line(f"pub fn from_bytes(reader: &mut BufferReader) -> Result<{sname}, {self.protocol.namespace}Error> {{")
        self.indent_level += 1
        for member_name, member_type in members:
            self.deserializer(member_name, member_type, "")

        varnames = [mem[0] for mem in members]
        self.write_line(f"Ok({sname} {{{', '.join(varnames)}}})")
        self.indent_level -= 1
        self.write_line("}")

        self.write_line("pub fn write_bytes(self, writer: &mut Vec<u8>) {")
        self.indent_level += 1
        for member_name, member_type in members:
            self.serializer(member_name, member_type, "self.")
        self.indent_level -= 1
        self.write_line("}")
        self.indent_level -= 1
        self.write_line("}")
        self.write_line()

    def generate(self) -> str:
        self.output = []
        self.write_line(f"// This file was automatically generated by {LIB_NAME} v{LIB_VERSION}.")
        self.write_line( "// <https://github.com/sjml/beschi>")
        self.write_line(f"// Do not edit directly.")
        self.write_line()
        self.add_boilerplate(substitutions=[("Beschi", self.protocol.namespace)])

        for sname, smembers in self.protocol.structs.items():
            self.gen_struct(sname, smembers)
        for mname, mmembers in self.protocol.messages.items():
            self.gen_struct(mname, mmembers)

        self.write_line("pub enum Message {")
        self.indent_level += 1
        for mname in self.protocol.messages.keys():
           self.write_line(f"{mname}({mname}),")
        self.indent_level -= 1
        self.write_line("}")
        self.write_line()

        return "\n".join(self.output)
