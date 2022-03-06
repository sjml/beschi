from ..protocol import Protocol, Variable, Struct, NUMERIC_TYPE_SIZES
from ..writer import Writer
from .. import LIB_NAME, LIB_VERSION

LANGUAGE_NAME = "Swift"


class SwiftWriter(Writer):
    language_name = LANGUAGE_NAME
    default_extension = ".swift"

    def __init__(self, p: Protocol, extra_args: dict[str,any] = {}):
        super().__init__(protocol=p, tab="    ")

        self.embed_protocol = extra_args["embed_protocol"]

        self.type_mapping["byte"] = "UInt8"
        self.type_mapping["bool"] = "Bool"
        self.type_mapping["uint16"] = "UInt16"
        self.type_mapping["int16"] = "Int16"
        self.type_mapping["uint32"] = "UInt32"
        self.type_mapping["int32"] = "Int32"
        self.type_mapping["uint64"] = "UInt64"
        self.type_mapping["int64"] = "Int64"
        self.type_mapping["float"] = "Float32"
        self.type_mapping["double"] = "Float64"
        self.type_mapping["string"] = "String"

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

    def deserializer(self, var: Variable, accessor: str):
        if var.is_list:
            self.write_line(f"let {var.name}_Length = try dataReader.Get{self.get_native_list_size()}()")
            self.write_line(f"{accessor}{var.name} = []")
            self.write_line(f"for _ in 0..<{var.name}_Length {{")
            self.indent_level += 1
            inner = Variable(self.protocol, f"let {var.name}_el", var.vartype)
            self.deserializer(inner, "")
            self.write_line(f"{accessor}{var.name}.append({var.name}_el)")
            self.indent_level -= 1
            self.write_line("}")
        elif var.vartype in NUMERIC_TYPE_SIZES or var.vartype == "string":
            self.write_line(f"{accessor}{var.name} = try dataReader.Get{self.type_mapping[var.vartype]}()")
        else:
            self.write_line(f"{accessor}{var.name} = try {var.vartype}.FromBytes(dataReader: dataReader)")

    def serializer(self, var: Variable, accessor: str):
        if var.is_list:
            self.write_line(f"dataWriter.Write{self.get_native_list_size()}({self.get_native_list_size()}({accessor}{var.name}.count))")
            self.write_line(f"for el in {accessor}{var.name} {{")
            self.indent_level += 1
            inner = Variable(self.protocol, "el", var.vartype)
            self.serializer(inner, "")
            self.indent_level -= 1
            self.write_line("}")
        elif var.vartype in NUMERIC_TYPE_SIZES or var.vartype == "string":
            self.write_line(f"dataWriter.Write{self.type_mapping[var.vartype]}({accessor}{var.name})")
        else:
            self.write_line(f"{accessor}{var.name}.WriteBytes(dataWriter)")

    def gen_measurement(self, st: Struct, accessor: str = "") -> tuple[list[str], int]:
        lines: list[str] = []
        accum = 0

        if st.is_simple():
            lines.append(f"return {self.protocol.get_size_of(st.name)};")
        else:
            size_init = "var size = 0"
            lines.append(size_init)

            for var in st.members:
                if var.is_list:
                    accum += NUMERIC_TYPE_SIZES[self.protocol.list_size_type]
                    if var.is_simple(True):
                        lines.append(f"size += {accessor}{var.name}.count * {self.protocol.get_size_of(var.vartype)}")
                    elif var.vartype == "string":
                        lines.append(f"for s in {accessor}{var.name} {{")
                        lines.append(f"{self.tab}size += {NUMERIC_TYPE_SIZES[self.protocol.string_size_type]} + s.data(using: String.Encoding.utf8)!.count")
                        lines.append("}")
                    else:
                        lines.append(f"for {var.name}_el in {accessor}{var.name} {{")
                        clines, caccum = self.gen_measurement(self.protocol.structs[var.vartype], f"{var.name}_el.")
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
                        lines.append(f"size += {accessor}{var.name}.data(using: String.Encoding.utf8)!.count")
                    else:
                        clines, caccum = self.gen_measurement(self.protocol.structs[var.vartype], f"{accessor}{var.name}.")
                        if clines[0] == size_init:
                            clines = clines[1:]
                        lines += clines
                        accum += caccum
        return lines, accum

    def gen_struct(self, sname: str, sdata: Struct):
        if sdata.is_message:
            if self.protocol.namespace != None:
                self.write_line(f"public struct {sname} : {self.protocol.namespace}_Message {{")
            else:
                self.write_line(f"public struct {sname} : Message {{")
        else:
            self.write_line(f"public struct {sname} {{")
        self.indent_level += 1

        for var in sdata.members:
            if var.is_list:
                self.write_line(f"public var {var.name}: [{self.type_mapping[var.vartype]}] = []")
            else:
                default_value = self.base_defaults.get(var.vartype, None)
                if default_value == None:
                    default_value = f"{var.vartype}()"
                self.write_line(f"public var {var.name}: {self.type_mapping[var.vartype]}{f' = {default_value}' if default_value else ''}")
        self.write_line()

        self.write_line("public init() {}")
        self.write_line()

        if sdata.is_message:
            self.write_line("public func GetMessageType() -> MessageType {")
            self.indent_level += 1
            self.write_line(f"return MessageType.{sname}Type")
            self.indent_level -= 1
            self.write_line("}")
            self.write_line()

            self.write_line("public func GetSizeInBytes() -> UInt32 {")
            self.indent_level += 1
            measure_lines, accumulator = self.gen_measurement(sdata, "self.")
            [self.write_line(s) for s in measure_lines]
            if accumulator > 0:
                self.write_line(f"size += {accumulator};")
            if len(measure_lines) > 1:
                self.write_line(f"return UInt32(size)")
            self.indent_level -= 1
            self.write_line("}")
            self.write_line()

            self.write_line(f"public static func FromBytes(_ fromData: Data) -> {sname}? {{")
            self.indent_level += 1
            self.write_line("let dr = DataReader(fromData: fromData)")
            self.write_line("return FromBytes(dataReader: dr)")
            self.indent_level -= 1
            self.write_line("}")
            self.write_line()
            self.write_line(f"static func FromBytes(dataReader: DataReader) -> {sname}? {{")
            self.indent_level += 1
            if len(sdata.members) > 0:
                self.write_line("do {")
                self.indent_level += 1
        else:
            self.write_line(f"static func FromBytes(dataReader: DataReader) throws -> {sname} {{")
            self.indent_level += 1
        decl = "var"
        if len(sdata.members) == 0:
            decl = "let"
        self.write_line(f"{decl} n{sname} = {self.type_mapping[sname]}()")
        [self.deserializer(mem, f"n{sname}.") for mem in sdata.members]
        self.write_line(f"return n{sname}")
        if sdata.is_message and len(sdata.members) > 0:
            self.indent_level -= 1
            self.write_line("}")
            self.write_line("catch {")
            self.indent_level += 1
            self.write_line("return nil")
            self.indent_level -= 1
            self.write_line("}")
        self.indent_level -= 1
        self.write_line("}")

        if sdata.is_message:
            self.write_line("public func WriteBytes(data: inout Data, tag: Bool) -> Void {")
            self.indent_level += 1
            self.write_line("let dataWriter = DataWriter(withData: &data)")
            self.write_line("if (tag) {")
            self.indent_level += 1
            self.write_line(f"dataWriter.WriteUInt8(MessageType.{sname}Type.rawValue)")
            self.indent_level -= 1
            self.write_line("}")
        else:
            self.write_line("func WriteBytes(_ dataWriter: DataWriter) -> Void {")
            self.indent_level += 1
        [self.serializer(mem, "self.") for mem in sdata.members]
        if sdata.is_message:
            self.write_line()
            self.write_line("data = dataWriter.data")
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
        self.write_line("import Foundation")
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

        if self.protocol.namespace != None:
            self.write_line(f"public protocol {self.protocol.namespace}_Message {{")
            self.indent_level += 1
            self.write_line(f"func GetMessageType() -> {self.protocol.namespace}.MessageType")
        else:
            self.write_line("public protocol Message {")
            self.indent_level += 1
            self.write_line(f"func GetMessageType() -> MessageType")
        self.write_line("func WriteBytes(data: inout Data, tag: Bool) -> Void")
        self.write_line("func GetSizeInBytes() -> UInt32")
        self.indent_level -= 1
        self.write_line("}")
        self.write_line()

        if self.protocol.namespace != None:
            self.write_line(f"public /* namespace */ enum {self.protocol.namespace} {{")
            self.indent_level += 1

        self.add_boilerplate(substitutions=[
            ("{# STRING_SIZE_TYPE #}", self.get_native_string_size())
        ])

        self.write_line("public enum MessageType: UInt8 {")
        self.indent_level += 1
        if len(self.protocol.messages) == 0:
            self.write_line("case __NullMessage = 0 /* to keep the compiler happy */")
        [self.write_line(f"case {k}Type = {i+1}") for i, k in enumerate(self.protocol.messages)]
        self.indent_level -= 1
        self.write_line("}")
        self.write_line()

        if self.protocol.namespace != None:
            self.write_line(f"public static func ProcessRawBytes(_ data: Data) -> [{self.protocol.namespace}_Message?] {{")
            self.indent_level += 1
            self.write_line(f"var msgList: [{self.protocol.namespace}_Message?] = []")
        else:
            self.write_line(f"public func ProcessRawBytes(_ data: Data) -> [Message?] {{")
            self.indent_level += 1
            self.write_line("var msgList: [Message?] = []")
        self.write_line("let dr = DataReader(fromData: data)")
        self.write_line("while !dr.IsFinished() {")
        self.indent_level += 1
        self.write_line("do {")
        self.indent_level += 1
        accessor = ""
        if self.protocol.namespace != None:
            accessor = f"{self.protocol.namespace}."
        self.write_line(f"let msgTypeByte = try dr.GetUInt8()")
        self.write_line(f"guard let msgType = {accessor}MessageType(rawValue: msgTypeByte)")
        self.write_line("else {")
        self.indent_level += 1
        self.write_line("throw DataReader.DataReaderError.InvalidData")
        self.indent_level -= 1
        self.write_line("}")
        self.write_line("switch msgType {")
        self.indent_level += 1
        for msg_type in self.protocol.messages:
            self.write_line(f"case {accessor}MessageType.{msg_type}Type:")
            self.indent_level += 1
            self.write_line(f"msgList.append({msg_type}.FromBytes(dataReader: dr))")
            self.indent_level -= 1
        if len(self.protocol.messages) == 0:
            self.write_line(f"case {accessor}MessageType.__NullMessage:")
            self.indent_level += 1
            self.write_line(f"break")
            self.indent_level -= 1
        self.indent_level -= 1
        self.write_line("}")
        self.indent_level -= 1
        self.write_line("}")
        self.write_line("catch {")
        self.indent_level += 1
        self.write_line("msgList.append(nil)")
        self.indent_level -= 1
        self.write_line("}")
        self.write_line("if msgList.last! == nil {")
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

        if self.protocol.namespace != None:
            self.indent_level -= 1
            self.write_line("}")

        self.write_line()
        assert self.indent_level == 0

        return "\n".join(self.output)
