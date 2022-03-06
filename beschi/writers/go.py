import argparse

from ..protocol import Protocol, Struct, Variable, NUMERIC_TYPE_SIZES
from ..writer import Writer, TextUtil
from .. import LIB_NAME, LIB_VERSION

LANGUAGE_NAME = "Go"


class GoWriter(Writer):
    language_name = LANGUAGE_NAME
    default_extension = ".go"

    def get_additional_args(parser: argparse.ArgumentParser):
        group = parser.add_argument_group(LANGUAGE_NAME)
        group.add_argument("--go-no-rename", action="store_const", const=True, default=False, help="don't rename data members to Uppercase")

    def __init__(self, p: Protocol, extra_args: dict[str,any] = {}):
        rename = not extra_args["go_no_rename"]

        if rename:
            for _, s in p.structs.items():
                for var in s.members:
                    var.name = TextUtil.capitalize(var.name)
            for _, m in p.messages.items():
                for var in m.members:
                    var.name = TextUtil.capitalize(var.name)

        super().__init__(protocol=p, tab="\t")

        self.embed_protocol = extra_args["embed_protocol"]

        self.type_mapping["byte"] = "byte"
        self.type_mapping["bool"] = "bool"
        self.type_mapping["uint16"] = "uint16"
        self.type_mapping["int16"] = "int16"
        self.type_mapping["uint32"] = "uint32"
        self.type_mapping["int32"] = "int32"
        self.type_mapping["uint64"] = "uint64"
        self.type_mapping["int64"] = "int64"
        self.type_mapping["float"] = "float32"
        self.type_mapping["double"] = "float64"

    def deserializer(self, var: Variable, accessor: str):
        def err_panic():
            self.write_line("if err != nil {")
            self.write_line(f"{self.tab}panic(err)")
            self.write_line("}")

        if var.is_list:
            self.write_line(f"var {var.name}_Len {self.get_native_list_size()}")
            self.write_line(f"err = binary.Read(data, binary.LittleEndian, &{var.name}_Len)")
            err_panic()
            self.write_line(f"{accessor}.{var.name} = make([]{self.type_mapping[var.vartype]}, {var.name}_Len)")
            idx = self.indent_level
            self.write_line(f"for i{idx} := ({self.get_native_list_size()})(0); i{idx} < {var.name}_Len; i{idx}++ {{")
            self.indent_level += 1
            inner = Variable(self.protocol, f"{var.name}[i{idx}]", var.vartype)
            self.deserializer(inner, accessor)
            self.indent_level -= 1
            self.write_line("}")
        elif var.vartype == "string":
            self.write_line(f"err = readString(data, &{accessor}.{var.name})")
            err_panic()
        elif var.is_simple():
            self.write_line(f"err = binary.Read(data, binary.LittleEndian, &{accessor}.{var.name})")
            err_panic()
        else:
            self.write_line(f"{var.vartype}FromBytes(data, &{accessor}.{var.name})")

    def serializer(self, var: Variable, accessor: str):
        if var.is_list:
            self.write_line(f"{var.name}_Len := ({self.get_native_list_size()})(len({accessor}.{var.name}))")
            self.write_line(f"binary.Write(data, binary.LittleEndian, {var.name}_Len)")
            idx = self.indent_level
            self.write_line(f"for i{idx} := ({self.get_native_list_size()})(0); i{idx} < {var.name}_Len; i{idx}++ {{")
            self.indent_level += 1
            inner = Variable(self.protocol, f"{var.name}[i{idx}]", var.vartype)
            self.serializer(inner, accessor)
            self.indent_level -= 1
            self.write_line("}")
        elif var.vartype == "string":
            self.write_line(f"writeString(data, &{accessor}.{var.name})")
        elif var.is_simple():
            self.write_line(f"binary.Write(data, binary.LittleEndian, &{accessor}.{var.name})")
        else:
            self.write_line(f"{accessor}.{var.name}.WriteBytes(data)")

    def gen_measurement(self, st: Struct, accessor: str = "") -> tuple[list[str], int]:
        lines: list[str] = []
        accum = 0

        if st.is_simple():
            lines.append(f"return {self.protocol.get_size_of(st.name)}")
        else:
            size_init = "size := 0"
            lines.append(size_init)

            for var in st.members:
                if var.is_list:
                    accum += NUMERIC_TYPE_SIZES[self.protocol.list_size_type]
                    if var.is_simple(True):
                        lines.append(f"size += len({accessor}{var.name}) * {self.protocol.get_size_of(var.vartype)}")
                    elif var.vartype == "string":
                        lines.append(f"for _, s := range {accessor}{var.name} {{")
                        lines.append(f"{self.tab}size += {NUMERIC_TYPE_SIZES[self.protocol.string_size_type]} + len(s)")
                        lines.append("}")
                    else:
                        lines.append(f"for _, el := range {accessor}{var.name} {{")
                        clines, caccum = self.gen_measurement(self.protocol.structs[var.vartype], f"el.")
                        if clines[0] == size_init:
                            clines = clines[1:]
                        clines.append(f"size += {caccum}")
                        lines += [f"{self.tab}{l}" for l in clines]
                        lines.append("}")
                else:
                    if var.is_simple():
                        accum += self.protocol.get_size_of(var.vartype)
                    elif var.vartype == "string":
                        accum += NUMERIC_TYPE_SIZES[self.protocol.string_size_type]
                        lines.append(f"size += len({accessor}{var.name})")
                    else:
                        clines, caccum = self.gen_measurement(self.protocol.structs[var.vartype], f"{accessor}{var.name}.")
                        if clines[0] == size_init:
                            clines = clines[1:]
                        lines += clines
                        accum += caccum
        return lines, accum

    def gen_struct(self, sname: str, sdata: Struct):
        self.write_line(f"type {sname} struct {{")
        self.indent_level += 1
        for var in sdata.members:
            if var.is_list:
                self.write_line(f"{var.name} []{self.type_mapping[var.vartype]}")
            else:
                self.write_line(f"{var.name} {self.type_mapping[var.vartype]}")
        self.indent_level -= 1
        self.write_line("}")
        self.write_line()

        if sdata.is_message:
            self.write_line(f"func (output {sname}) GetMessageType() MessageType {{")
            self.indent_level += 1
            self.write_line(f"return {sname}Type")
            self.indent_level -= 1
            self.write_line("}")
            self.write_line()

            self.write_line(f"func (output {sname}) GetSizeInBytes() int {{")
            self.indent_level +=1
            measure_lines, accumulator = self.gen_measurement(sdata, "output.")
            [self.write_line(s) for s in measure_lines]
            if accumulator > 0:
                self.write_line(f"size += {accumulator}")
            if len(measure_lines) > 1:
                self.write_line(f"return size")
            self.indent_level -=1
            self.write_line("}")

            self.write_line(f"func {sdata.name}FromBytes (data io.Reader) (msg *{sname}) {{")
            self.indent_level += 1
            self.write_line("defer func() {")
            self.indent_level += 1
            self.write_line("if r := recover(); r != nil {")
            self.indent_level += 1
            self.write_line("msg = nil")
            self.indent_level -= 1
            self.write_line("}")
            self.indent_level -= 1
            self.write_line("}()")
            if len(sdata.members) > 0:
                self.write_line("var err error")
                self.write_line("err = nil")
            self.write_line(f"ret := {sname}{{}}")
            [self.deserializer(mem, "ret") for mem in sdata.members]
            if len(sdata.members) > 0:
                self.write_line("if err != nil {")
                self.indent_level += 1
                self.write_line(f"panic(err)")
                self.indent_level -= 1
                self.write_line("}")
            self.write_line()
            self.write_line("return &ret")
        else:
            self.write_line(f"func {sname}FromBytes (data io.Reader, input *{sname}) {{")
            self.indent_level += 1
            self.write_line("var err error")
            self.write_line("err = nil")
            [self.deserializer(mem, "input") for mem in sdata.members]
            self.write_line("if err != nil {")
            self.indent_level += 1
            self.write_line(f"panic(err)")
            self.indent_level -= 1
            self.write_line("}")
        self.indent_level -= 1
        self.write_line("}")
        self.write_line()

        if sdata.is_message:
            self.write_line(f"func (output {sname}) WriteBytes (data io.Writer, tag bool) {{")
            self.indent_level += 1
            self.write_line("if tag {")
            self.indent_level += 1
            self.write_line(f"binary.Write(data, binary.LittleEndian, {sname}Type)")
            self.indent_level -= 1
            self.write_line("}")
        else:
            self.write_line(f"func (output {sname}) WriteBytes (data io.Writer) {{")
            self.indent_level += 1
        [self.serializer(mem, "output") for mem in sdata.members]
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
        if self.protocol.namespace:
            subs.append(("Beschi", self.protocol.namespace))

        self.add_boilerplate(subs)
        self.write_line()

        self.write_line("type MessageType byte")
        self.write_line("const (")
        self.indent_level += 1
        [self.write_line(f"{msg_name}Type MessageType = {i+1}") for i, msg_name in enumerate(self.protocol.messages)]
        self.indent_level -= 1
        self.write_line(")")
        self.write_line()

        self.write_line("type Message interface {")
        self.indent_level += 1
        self.write_line("GetMessageType() MessageType")
        self.write_line("WriteBytes(data io.Writer, tag bool)")
        self.write_line("GetSizeInBytes() int")
        self.indent_level -= 1
        self.write_line("}")
        self.write_line()

        self.write_line("func ProcessRawBytes (data io.Reader) []Message {")
        self.indent_level += 1
        self.write_line("var msgList []Message")
        self.write_line("var err error")
        self.write_line("for err != io.EOF {")
        self.indent_level += 1
        self.write_line("var msgType MessageType")
        self.write_line("err = binary.Read(data, binary.LittleEndian, &msgType)")
        self.write_line("if err == io.EOF {")
        self.indent_level += 1
        self.write_line("break")
        self.indent_level -= 1
        self.write_line("}")
        self.write_line("switch msgType {")
        for msg_type in self.protocol.messages:
            self.write_line(f"case {msg_type}Type:")
            self.indent_level += 1
            self.write_line(f"msgList = append(msgList, {msg_type}FromBytes(data))")
            self.indent_level -= 1
        self.write_line("default:")
        self.indent_level += 1
        self.write_line("msgList = append(msgList, nil)")
        self.indent_level -= 1
        self.write_line("}")
        self.write_line("if msgList[len(msgList)-1] == nil {")
        self.indent_level += 1
        self.write_line("break")
        self.indent_level -= 1
        self.write_line("}")
        self.indent_level -= 1
        self.write_line("}")
        self.write_line("return msgList")
        self.indent_level -= 1
        self.write_line("}")
        self.write_line()

        for sname, sdata in self.protocol.structs.items():
            self.gen_struct(sname, sdata)

        for mname, mdata in self.protocol.messages.items():
            self.gen_struct(mname, mdata)

        self.write_line()
        assert self.indent_level == 0

        return "\n".join(self.output)
