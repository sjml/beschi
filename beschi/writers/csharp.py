from ..protocol import Protocol, Struct, Variable, NUMERIC_TYPE_SIZES
from ..writer import Writer, TextUtil
from .. import LIB_NAME, LIB_VERSION

LANGUAGE_NAME = "CSharp"


class CSharpWriter(Writer):
    language_name = LANGUAGE_NAME
    default_extension = ".cs"

    def __init__(self, p: Protocol, extra_args: dict[str,any] = {}):
        super().__init__(protocol=p, tab="    ")

        self.embed_protocol = extra_args["embed_protocol"]

        self.type_mapping["byte"] = "byte"
        self.type_mapping["bool"] = "bool"
        self.type_mapping["uint16"] = "ushort"
        self.type_mapping["int16"] = "short"
        self.type_mapping["uint32"] = "uint"
        self.type_mapping["int32"] = "int"
        self.type_mapping["uint64"] = "ulong"
        self.type_mapping["int64"] = "long"
        self.type_mapping["float"] = "float"
        self.type_mapping["double"] = "double"

        self.base_deserializers: dict[str,str] = {
            "byte": "ReadByte",
            "bool": "ReadBoolean",
            "uint16": "ReadUInt16",
            "int16": "ReadInt16",
            "uint32": "ReadUInt32",
            "int32": "ReadInt32",
            "uint64": "ReadUInt64",
            "int64": "ReadInt64",
            "float": "ReadSingle",
            "double": "ReadDouble",
        }

    def deserializer(self, var: Variable, accessor: str):
        var_clean = TextUtil.replace(var.name, [("[", "_"), ("]", "_"), (" ", "_")])
        if var.is_list:
            self.write_line(f"{self.get_native_list_size()} {var_clean}_Length = br.{self.base_deserializers[self.protocol.list_size_type]}();")
            self.write_line(f"{accessor}{var.name} = new List<{self.type_mapping[var.vartype]}>();")
            idx = self.indent_level
            self.write_line(f"for (int i{idx} = 0; i{idx} < {var_clean}_Length; i{idx}++)")
            self.write_line("{")
            self.indent_level += 1
            inner = Variable(self.protocol, f"{self.type_mapping[var.vartype]} el", var.vartype)
            self.deserializer(inner, "")
            self.write_line(f"{accessor}{var.name}.Add(el);")
            self.indent_level -= 1
            self.write_line("}")
        elif var.vartype == "string":
            self.write_line(f"{self.get_native_string_size()} {var_clean}_Length = br.{self.base_deserializers[self.protocol.string_size_type]}();")
            self.write_line(f"byte[] {var_clean}_Buffer = br.ReadBytes((int){var_clean}_Length);")
            self.write_line(f"{accessor}{var.name} = System.Text.Encoding.UTF8.GetString({var_clean}_Buffer);")
        elif var.vartype in self.base_deserializers:
            self.write_line(f"{accessor}{var.name} = br.{self.base_deserializers[var.vartype]}();")
        else:
            self.write_line(f"{accessor}{var.name} = {var.vartype}.FromBytes(br);")

    def serializer(self, var: Variable, accessor: str):
        if var.is_list:
            self.write_line(f"bw.Write(({self.get_native_list_size()}){accessor}{var.name}.Count);")
            self.write_line(f"foreach ({self.type_mapping[var.vartype]} el in {accessor}{var.name})")
            self.write_line("{")
            self.indent_level += 1
            inner = Variable(self.protocol, "el", var.vartype)
            self.serializer(inner, "")
            self.indent_level -= 1
            self.write_line("}")
        elif var.vartype == "string":
            self.write_line(f"byte[] {var.name}_Buffer = System.Text.Encoding.UTF8.GetBytes({accessor}{var.name});")
            self.write_line(f"bw.Write(({self.get_native_string_size()}){var.name}_Buffer.Length);")
            self.write_line(f"bw.Write({var.name}_Buffer);")
        elif var.vartype in NUMERIC_TYPE_SIZES:
            self.write_line(f"bw.Write({accessor}{var.name});")
        else:
            self.write_line(f"{accessor}{var.name}.WriteBytes(bw);")

    def gen_measurement(self, st: Struct, accessor: str = "") -> tuple[list[str], int]:
        lines: list[str] = []
        accum = 0

        if st.is_simple():
            lines.append(f"return {self.protocol.get_size_of(st.name)};")
        else:
            size_init = "int size = 0;"
            lines.append(size_init)

            for var in st.members:
                if var.is_list:
                    accum += NUMERIC_TYPE_SIZES[self.protocol.list_size_type]
                    if var.is_simple(True):
                        lines.append(f"size += {accessor}{var.name}.Count * {self.protocol.get_size_of(var.vartype)};")
                    elif var.vartype == "string":
                        lines.append(f"foreach (string s in {accessor}{var.name})")
                        lines.append("{")
                        lines.append(f"{self.tab}size += {NUMERIC_TYPE_SIZES[self.protocol.string_size_type]} + System.Text.Encoding.UTF8.GetBytes(s).Length;")
                        lines.append("}")
                    else:
                        idx = self.indent_level
                        lines.append(f"foreach ({self.type_mapping[var.vartype]} el{idx} in {accessor}{var.name})")
                        lines.append("{")
                        self.indent_level += 1
                        clines, caccum = self.gen_measurement(self.protocol.structs[var.vartype], f"el{idx}.")
                        if clines[0] == size_init:
                            clines = clines[1:]
                        clines.append(f"size += {caccum};")
                        lines += [f"{self.tab}{l}" for l in clines]
                        self.indent_level -= 1
                        lines.append("}")
                else:
                    if var.is_simple():
                        accum += self.protocol.get_size_of(var.vartype)
                    elif var.vartype == "string":
                        accum += NUMERIC_TYPE_SIZES[self.protocol.string_size_type]
                        lines.append(f"size += {accessor}{var.name}.Length;")
                    else:
                        clines, caccum = self.gen_measurement(self.protocol.structs[var.vartype], f"{accessor}{var.name}.")
                        if clines[0] == size_init:
                            clines = clines[1:]
                        lines += clines
                        accum += caccum
        return lines, accum

    def gen_struct(self, sname: str, sdata: Struct):
        if sdata.is_message:
            self.write_line(f"public class {sname} : Message")
        else:
            self.write_line(f"public class {sname}")
        self.write_line("{")
        self.indent_level += 1

        for var in sdata.members:
            if var.is_list:
                self.write_line(f"public List<{self.type_mapping[var.vartype]}> {var.name} = new List<{self.type_mapping[var.vartype]}>();")
            else:
                default = None
                if var.vartype == "string":
                    default = '""'
                elif var.vartype in self.protocol.structs:
                    default = f"new {var.vartype}()"
                self.write_line(f"public {self.type_mapping[var.vartype]} {var.name}{f' = {default}' if default else ''};")

        if sdata.is_message:
            self.write_line()
            self.write_line(f"public override MessageType GetMessageType() {{ return MessageType.{sname}Type; }}")
            self.write_line()
            self.write_line("public override int GetSizeInBytes()")
            self.write_line("{")
            self.indent_level +=1
            measure_lines, accumulator = self.gen_measurement(sdata, "this.")
            [self.write_line(s) for s in measure_lines]
            if accumulator > 0:
                self.write_line(f"size += {accumulator};")
            if len(measure_lines) > 1:
                self.write_line(f"return size;")
            self.indent_level -=1
            self.write_line("}")
        self.write_line()

        self.write_line(f"public static {sname} FromBytes(BinaryReader br)")
        self.write_line("{")
        self.indent_level += 1
        if sdata.is_message:
            self.write_line("try")
            self.write_line("{")
            self.indent_level += 1
        self.write_line(f"{sname} n{sname} = new {sname}();")
        [self.deserializer(mem, f"n{sname}.") for mem in sdata.members]
        self.write_line(f"return n{sname};")
        if sdata.is_message:
            self.indent_level -= 1
            self.write_line("}")
            self.write_line("catch (System.IO.EndOfStreamException)")
            self.write_line("{")
            self.indent_level += 1
            self.write_line("return null;")
            self.indent_level -= 1
            self.write_line("}")
        self.indent_level -= 1
        self.write_line("}")

        if sdata.is_message:
            self.write_line(f"public override void WriteBytes(BinaryWriter bw, bool tag)")
            self.write_line("{")
            self.indent_level += 1
            self.write_line("if (tag)")
            self.write_line("{")
            self.indent_level += 1
            self.write_line(f"bw.Write((byte)MessageType.{sname}Type);")
            self.indent_level -= 1
            self.write_line("}")
        else:
            self.write_line(f"public void WriteBytes(BinaryWriter bw)")
            self.write_line("{")
            self.indent_level += 1
        [self.serializer(mem, "this.") for mem in sdata.members]
        self.indent_level -= 1
        self.write_line("}")
        self.write_line()

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

        self.write_line("using System;")
        self.write_line("using System.IO;")
        self.write_line("using System.Text;")
        self.write_line("using System.Collections.Generic;")
        self.write_line()

        if self.protocol.namespace:
            self.write_line(f"namespace {self.protocol.namespace}")
            self.write_line("{")
            self.indent_level += 1

        self.write_line("public enum MessageType")
        self.write_line("{")
        self.indent_level += 1
        [self.write_line(f"{k}Type = {i+1},") for i, k in enumerate(self.protocol.messages)]
        self.indent_level -= 1
        self.write_line("}")
        self.write_line()

        self.write_line("public abstract class Message {")
        self.indent_level += 1
        self.write_line("abstract public MessageType GetMessageType();")
        self.write_line("abstract public void WriteBytes(BinaryWriter bw, bool tag);")
        self.write_line("abstract public int GetSizeInBytes();")
        self.write_line()

        self.write_line("public static Message[] ProcessRawBytes(BinaryReader br)")
        self.write_line("{")
        self.indent_level += 1
        self.write_line("List<Message> msgList = new List<Message>();")
        self.write_line("while (br.BaseStream.Position < br.BaseStream.Length)")
        self.write_line("{")
        self.indent_level += 1
        self.write_line("byte msgType = br.ReadByte();")
        self.write_line("switch (msgType)")
        self.write_line("{")
        self.indent_level += 1
        for msg_type in self.protocol.messages:
            self.write_line(f"case (byte)MessageType.{msg_type}Type:")
            self.indent_level += 1
            self.write_line(f"msgList.Add({msg_type}.FromBytes(br));")
            self.write_line("break;")
            self.indent_level -= 1
        self.write_line("default:")
        self.indent_level += 1
        self.write_line("msgList.Add(null);")
        self.write_line("break;")
        self.indent_level -= 1
        self.indent_level -= 1
        self.write_line("}")
        self.write_line("if (msgList[msgList.Count-1] == null) {")
        self.indent_level += 1
        self.write_line("break;")
        self.indent_level -= 1
        self.write_line("}")
        self.indent_level -= 1
        self.write_line("}")
        self.write_line("return msgList.ToArray();")
        self.indent_level -= 1
        self.write_line("}")
        self.indent_level -= 1
        self.write_line("}")
        self.write_line()

        for sname, sdata in self.protocol.structs.items():
            self.gen_struct(sname, sdata)

        for mname, mdata in self.protocol.messages.items():
            self.gen_struct(mname, mdata)

        if self.protocol.namespace:
            self.indent_level -= 1
            self.write_line("}")

        self.write_line()
        assert self.indent_level == 0

        return "\n".join(self.output)
