import argparse

from ..protocol import Protocol, Struct, Variable, Enum, NUMERIC_TYPE_SIZES
from ..writer import Writer, TextUtil
from .. import LIB_NAME, LIB_VERSION

LANGUAGE_NAME = "Go"


class GoWriter(Writer):
    language_name = LANGUAGE_NAME
    default_extension = ".go"

    @classmethod
    def get_additional_args(cls, parser: argparse.ArgumentParser):
        group = parser.add_argument_group(cls.language_name)
        group.add_argument("--go-no-rename", action="store_const", const=True, default=False, help="don't rename data members to Uppercase or namespace to snake_case")

    def __init__(self, p: Protocol, extra_args: dict[str,any] = {}):
        self.rename = not extra_args["go_no_rename"]

        if self.rename:
            for _, e in p.enums.items():
                new_vals: dict[str,int] = {}
                for v, vi in e.values.items():
                    new_vals[TextUtil.capitalize(v)] = vi
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

    def struct_has_enums(self, s: Struct) -> bool:
        for var in s.members:
            if var.vartype in self.protocol.enums:
                return True
            elif var.vartype in self.protocol.structs:
                st = self.protocol.structs[var.vartype]
                if self.struct_has_enums(st):
                    return True
        return False

    def deserializer(self, var: Variable, accessor: str, by_ref: bool, declare_err: bool):
        if var.is_list:
            self.write_line(f"var {var.name}_Len {self.get_native_list_size()}")
            self.write_line(f"if err {':' if declare_err else ''}= binary.Read(data, binary.LittleEndian, &{var.name}_Len); err != nil {{")
            self.indent_level += 1
            self.write_line(f"return {'' if by_ref else 'nil, '}fmt.Errorf(\"could not read {var.name}_Len at offset %d (%w)\", getDataOffset(data), err)")
            self.indent_level -= 1
            self.write_line("}")
            self.write_line(f"{accessor}.{var.name} = make([]{self.type_mapping[var.vartype]}, {var.name}_Len)")
            idx = self.indent_level
            self.write_line(f"for i{idx} := ({self.get_native_list_size()})(0); i{idx} < {var.name}_Len; i{idx}++ {{")
            self.indent_level += 1
            if var.vartype in self.protocol.enums:
                self.write_line(f"var _{var.name} {var.vartype}")
                self.write_line(f"if err {':' if declare_err else ''}= binary.Read(data, binary.LittleEndian, &_{var.name}); err != nil {{")
                self.indent_level += 1
                self.write_line(f"return {'' if by_ref else 'nil, '}fmt.Errorf(\"could not read {accessor}.{var.name} at offset %d (%w)\", getDataOffset(data), err)")
                self.indent_level -= 1
                self.write_line("}")
                self.write_line(f"if !isValid{var.vartype}(_{var.name}) {{")
                self.indent_level += 1
                self.write_line(f"return {'' if by_ref else 'nil, '}fmt.Errorf(\"enum %d out of range for {var.vartype}\", _{var.name})")
                self.indent_level -= 1
                self.write_line("}")
                self.write_line(f"{accessor}.{var.name}[i{idx}] = _{var.name}")
            else:
                inner = Variable(self.protocol, f"{var.name}[i{idx}]", var.vartype)
                self.deserializer(inner, accessor, by_ref, declare_err)
            self.indent_level -= 1
            self.write_line("}")
        elif var.vartype == "string":
            self.write_line(f"if err {':' if declare_err else ''}= readString(data, &{accessor}.{var.name}); err != nil {{")
            self.indent_level += 1
            self.write_line(f"return {'' if by_ref else 'nil, '}fmt.Errorf(\"could not read string at offset %d (%w)\", getDataOffset(data), err)")
            self.indent_level -= 1
            self.write_line("}")
        elif var.vartype in self.protocol.enums:
            self.write_line(f"var _{var.name} {var.vartype}")
            self.write_line(f"if err {':' if declare_err else ''}= binary.Read(data, binary.LittleEndian, &_{var.name}); err != nil {{")
            self.indent_level += 1
            self.write_line(f"return {'' if by_ref else 'nil, '}fmt.Errorf(\"could not read {accessor}.{var.name} at offset %d (%w)\", getDataOffset(data), err)")
            self.indent_level -= 1
            self.write_line("}")
            self.write_line(f"if !isValid{var.vartype}(_{var.name}) {{")
            self.indent_level += 1
            self.write_line(f"return {'' if by_ref else 'nil, '}fmt.Errorf(\"enum %d out of range for {var.vartype}\", _{var.name})")
            self.indent_level -= 1
            self.write_line("}")
            self.write_line(f"{accessor}.{var.name} = _{var.name}")
        elif var.is_simple():
            self.write_line(f"if err {':' if declare_err else ''}= binary.Read(data, binary.LittleEndian, &{accessor}.{var.name}); err != nil {{")
            self.indent_level += 1
            self.write_line(f"return {'' if by_ref else 'nil, '}fmt.Errorf(\"could not read {accessor}.{var.name} at offset %d (%w)\", getDataOffset(data), err)")
            self.indent_level -= 1
            self.write_line("}")
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
        elif var.vartype in self.protocol.enums:
            e = self.protocol.enums[var.vartype]
            self.write_line(f"binary.Write(data, binary.LittleEndian, &{accessor}.{var.name})")
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

    def gen_enum(self, ename: str, edata: Enum):
        longest_entry = max(len(e) for e in edata.values.keys())
        self.write_line(f"type {ename} {self.type_mapping[edata.encoding]}")
        self.write_line()
        self.write_line("const (")
        self.indent_level += 1
        for v, vi in edata.values.items():
            self.write_line(f"{ename}{v:<{longest_entry}} {ename} = {vi}")
        self.indent_level -= 1
        self.write_line(")")
        self.write_line()
        self.write_line(f"func isValid{ename}(value {ename}) bool {{")
        self.indent_level += 1
        self.write_line("switch value {")
        self.write_line(f"case {', '.join([f'{ename}{k}' for k in edata.values.keys()])}:")
        self.indent_level += 1
        self.write_line("return true")
        self.indent_level -= 1
        self.write_line("default:")
        self.indent_level += 1
        self.write_line("return false")
        self.indent_level -= 1
        self.write_line("}")
        self.indent_level -= 1
        self.write_line("}")
        self.write_line()

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

        self.write_line(f"func New{sname}Default() {sname} {{")
        self.indent_level += 1

        if not self.struct_has_enums(sdata):
            self.write_line(f"return {sname}{{}}")
        else:
            self.write_line(f"return {sname}{{")
            self.indent_level += 1
            for var in sdata.members:
                if var.vartype in self.protocol.enums and not var.is_list:
                    e = self.protocol.enums[var.vartype]
                    self.write_line(f"{var.name}: {var.vartype}{e.get_default_pair()[0]},")
                elif var.vartype in self.protocol.structs and not var.is_list:
                    s = self.protocol.structs[var.vartype]
                    if self.struct_has_enums(s):
                        self.write_line(f"{var.name}: New{var.vartype}Default(),")
            self.indent_level -= 1
            self.write_line("}")

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
            self.write_line()

            self.write_line(f"func {sdata.name}FromBytes(data io.Reader) (*{sname}, error) {{")
            self.indent_level += 1
            self.write_line(f"msg := &{sdata.name}{{}}")
            self.write_line()
            first = True
            for mem in sdata.members:
                if first:
                    first = False
                    self.deserializer(mem, "msg", False, True)
                else:
                    self.deserializer(mem, "msg", False, True)
            self.write_line()
            self.write_line("return msg, nil")
        else:
            self.write_line(f"func {sname}FromBytes(data io.Reader, input *{sname}) error {{")
            self.indent_level += 1
            [self.deserializer(mem, "input", True, True) for mem in sdata.members]
            self.write_line("return nil")
        self.indent_level -= 1
        self.write_line("}")
        self.write_line()

        if sdata.is_message:
            self.write_line(f"func (output {sname}) WriteBytes(data io.Writer, tag bool) {{")
            self.indent_level += 1
            self.write_line("if tag {")
            self.indent_level += 1
            self.write_line(f"binary.Write(data, binary.LittleEndian, {sname}Type)")
            self.indent_level -= 1
            self.write_line("}")
        else:
            self.write_line(f"func (output {sname}) WriteBytes(data io.Writer) {{")
            self.indent_level += 1
        [self.serializer(mem, "output") for mem in sdata.members]
        self.indent_level -= 1
        self.write_line("}")
        self.write_line()

    def generate(self) -> str:
        self.output = []

        self.write_line(f"// This file was automatically generated by {LIB_NAME} v{LIB_VERSION}")
        self.write_line( "// <https://github.com/sjml/beschi>")
        self.write_line( "// Do not edit directly.")
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
            if self.rename:
                subs.append(("beschi", TextUtil.convert_to_lower_snake_case(self.protocol.namespace)))

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

        self.write_line("func ProcessRawBytes(data io.Reader, max int) ([]Message, error) {")
        self.indent_level += 1
        self.write_line("var msgList []Message")
        self.write_line("if max == 0 {")
        self.indent_level += 1
        self.write_line("return msgList, nil")
        self.indent_level -= 1
        self.write_line("}")
        self.write_line("var err error")
        self.write_line("for (err != io.EOF) && (max < 0 || len(msgList) < max) {")
        self.indent_level += 1
        self.write_line("var msgType MessageType")
        self.write_line("err = binary.Read(data, binary.LittleEndian, &msgType)")
        self.write_line("if err == io.EOF {")
        self.indent_level += 1
        self.write_line("break")
        self.indent_level -= 1
        self.write_line("}")
        self.write_line("if msgType == 0 {")
        self.indent_level += 1
        self.write_line("return msgList, nil")
        self.indent_level -= 1
        self.write_line("}")
        self.write_line("switch msgType {")
        for msg_type in self.protocol.messages:
            self.write_line(f"case {msg_type}Type:")
            self.indent_level += 1
            self.write_line(f"msg, err := {msg_type}FromBytes(data)")
            self.write_line("if err != nil {")
            self.indent_level += 1
            self.write_line(f"return nil, fmt.Errorf(\"err in {msg_type} read (%w)\", err)")
            self.indent_level -= 1
            self.write_line("}")
            self.write_line(f"msgList = append(msgList, msg)")
            self.indent_level -= 1
        self.write_line("default:")
        self.indent_level += 1
        self.write_line(f"return nil, fmt.Errorf(\"unknown message type: %d\", msgType)")
        self.indent_level -= 1
        self.write_line("}")
        self.indent_level -= 1
        self.write_line("}")
        self.write_line("return msgList, nil")
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
