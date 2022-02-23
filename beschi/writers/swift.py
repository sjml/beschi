from ..protocol import Protocol, BASE_TYPE_SIZES, COLLECTION_TYPES
from ..writer import Writer
from .. import LIB_NAME, LIB_VERSION

LANGUAGE_NAME = "Swift"


class SwiftWriter(Writer):
    language_name = LANGUAGE_NAME
    default_extension = ".swift"
    in_progress = True

    def __init__(self, p: Protocol):
        super().__init__(protocol=p, tab="    ")

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


    def deserializer(self, var_type: str, var_name: str, parent: str = "self") -> list[str]:
        if parent:
            pref = parent + "."
        else:
            pref = ""
        label = var_name
        if label.endswith("_i]"):
            label = "i_"
        if var_type in BASE_TYPE_SIZES or var_type in COLLECTION_TYPES:
            return [
                f"{pref}{var_name} = try dataReader.Get{self.type_mapping[var_type]}()",
            ]
        elif var_type in self.protocol.structs:
            return [
                f"{pref}{var_name} = try {self.type_mapping[var_type]}.FromBytes(dataReader: dataReader)",
            ]
        elif var_type[0] == "[" and var_type[-1] == "]":
            interior = var_type[1:-1]
            out = [
                f"{pref}{var_name} = []",
                f"let {var_name}Length = try dataReader.GetUInt32()",
                f"for _ in 0..<{var_name}Length {{",
            ]
            out += [
                self.tab + deser for deser in self.deserializer(
                    interior, f"let {var_name}_i", ""
                )
            ]
            out += [f"{self.tab}{pref}{var_name}.append({var_name}_i)"]
            out += ["}"]
            return out
        else:
            raise NotImplementedError(f"Type {var_type} not deserializable yet.")

    def serializer(self, var_type: str, var_name: str, parent: str = "self") -> list[str]:
        if parent:
            pref = parent + "."
        else:
            pref = ""
        label = var_name
        if label.endswith("_i]"):
            label = "i_"
        if var_type in BASE_TYPE_SIZES or var_type in COLLECTION_TYPES:
            return [
                f"dataWriter.Write{self.type_mapping[var_type]}({pref}{var_name})",
            ]
        elif var_type in self.protocol.structs:
            return [
                f"{pref}{var_name}.WriteBytes(dataWriter)"
            ]
        elif var_type[0] == "[" and var_type[-1] == "]":
            interior = var_type[1:-1]
            out = [
                f"dataWriter.WriteUInt32(UInt32({pref}{var_name}.count))",
                f"for {label}_el in {var_name} {{",
            ]
            out += [
                self.tab + ser for ser in self.serializer(
                    interior, f"{label}_el", ""
                )
            ]
            out += ["}"]
            return out
        else:
            raise NotImplementedError(f"Type {var_type} not serializable yet.")


    def gen_measurement(self, s: tuple[str, list[tuple[str,str]]], accessor_prefix: str = "") -> tuple[list[str], int]:
        lines: list[str] = []
        return lines

        # accum = 0
        # if self.protocol.is_simple(s[0]):
        #     lines.append(f"return {self.protocol.calculate_size(s[0])};")
        # else:
        #     size_init = "let size: number = 0;"
        #     lines.append(size_init)

        #     for var_name, var_type in s[1]:
        #         if self.protocol.is_simple(var_type):
        #             accum += self.protocol.calculate_size(var_type)
        #         else:
        #             if var_type == "string":
        #                 accum += BASE_TYPE_SIZES["uint32"]
        #                 lines.append(f"size += textEnc.encode({accessor_prefix}{var_name}).byteLength;")
        #             elif var_type == "[string]":
        #                 accum += BASE_TYPE_SIZES["uint32"]
        #                 lines.append(f"for (let {var_name}_i=0; {var_name}_i < {accessor_prefix}{var_name}.length; {var_name}_i++) {{")
        #                 lines.append(f"{self.tab}size += {BASE_TYPE_SIZES['uint32']} + textEnc.encode({accessor_prefix}{var_name}[{var_name}_i]).byteLength;")
        #                 lines.append("}")
        #             elif var_type[0] == "[" and var_type[-1] == "]":
        #                 listed_var_type = var_type[1:-1]
        #                 if self.protocol.is_simple(listed_var_type):
        #                     accum += BASE_TYPE_SIZES["uint32"]
        #                     lines.append(f"size += {accessor_prefix}{var_name}.length * {self.protocol.calculate_size(listed_var_type)};")
        #                 else:
        #                     accum += BASE_TYPE_SIZES["uint32"]
        #                     lines.append(f"for (let {var_name}_i=0; {var_name}_i < {accessor_prefix}{var_name}.length; {var_name}_i++) {{")
        #                     clines, caccum = self.gen_measurement((var_type, self.protocol.structs[listed_var_type]), f"{accessor_prefix}{var_name}[{var_name}_i].")
        #                     if clines[0] == size_init:
        #                         clines = clines[1:]
        #                     clines.append(f"size += {caccum};")
        #                     lines += [f"{self.tab}{l}" for l in clines]
        #                     lines.append("}")
        #             else:
        #                 clines, caccum = self.gen_measurement((var_type, self.protocol.structs[var_type]), f"{accessor_prefix}{var_name}.")
        #                 if clines[0] == size_init:
        #                     clines = clines[1:]
        #                 lines += clines
        #                 accum += caccum
        # return lines, accum

    def gen_struct(self, s: tuple[str, list[tuple[str,str]]]):
        is_message = s[0] in self.protocol.messages

        if is_message:
            if self.protocol.namespace != None:
                self.write_line(f"public struct {s[0]} : {self.protocol.namespace}_Message {{")
            else:
                self.write_line(f"public struct {s[0]} : Message {{")
        else:
            self.write_line(f"public struct {s[0]} {{")
        self.indent_level += 1

        for var_name, var_type in s[1]:
            if var_type[0] == "[" and var_type[-1] == "]":
                self.write_line(f"public var {var_name}: [{self.get_var(var_type[1:-1])}] = []")
            else:
                var_type = self.get_var(var_type)
                default_value = "0"
                if var_type.startswith("Float"):
                    default_value = "0.0"
                elif var_type == "Bool":
                    default_value = "false"
                elif var_type == "String":
                    default_value = "\"\""
                elif var_type in self.protocol.structs:
                    default_value = f"{var_type}()"
                self.write_line(f"public var {var_name}: {var_type}{f' = {default_value}' if default_value else ''}")
        self.write_line()

        self.write_line("public init() {}")
        self.write_line()

        if is_message:
            self.write_line("public func GetMessageType() -> MessageType {")
            self.indent_level += 1
            self.write_line(f"return MessageType.{s[0]}Type")
            self.indent_level -= 1
            self.write_line("}")
            self.write_line()
        #     self.write_line("GetSizeInBytes(): number {")
        #     self.indent_level += 1
        #     measure_lines, accumulator = self.gen_measurement(s, "this.")
        #     [self.write_line(s) for s in measure_lines]
        #     if accumulator > 0:
        #         self.write_line(f"size += {accumulator};")
        #     if len(measure_lines) > 1:
        #         self.write_line(f"return size;")
        #     self.indent_level -= 1
        #     self.write_line("}")
            # self.write_line()
            self.write_line("public func WriteBytes(data: inout Data, tag: Bool) -> Void {")
            self.indent_level += 1
            self.write_line("let dataWriter = DataWriter(withData: &data)")
            self.write_line("if (tag) {")
            self.indent_level += 1
            self.write_line(f"dataWriter.WriteUInt8(MessageType.{s[0]}Type.rawValue)")
            self.indent_level -= 1
            self.write_line("}")
        else:
            self.write_line("func WriteBytes(_ dataWriter: DataWriter) -> Void {")
            self.indent_level += 1

        for var_name, var_type in s[1]:
            [self.write_line(s) for s in self.serializer(var_type, var_name)]
        if is_message:
            self.write_line()
            self.write_line("data = dataWriter.data")
        self.indent_level -= 1
        self.write_line("}")
        self.write_line()

        if is_message:
            self.write_line(f"public static func FromBytes(_ fromData: Data) -> {s[0]}? {{")
            self.indent_level += 1
            self.write_line("let dr = DataReader(fromData: fromData)")
            self.write_line("return FromBytes(dataReader: dr)")
            self.indent_level -= 1
            self.write_line("}")
            self.write_line()
            self.write_line(f"static func FromBytes(dataReader: DataReader) -> {s[0]}? {{")
            self.indent_level += 1
            if len(s[1]) > 0:
                self.write_line("do {")
                self.indent_level += 1
        else:
            self.write_line(f"static func FromBytes(dataReader: DataReader) throws -> {s[0]} {{")
            self.indent_level += 1
        decl = "var"
        if len(s[1]) == 0:
            decl = "let"
        self.write_line(f"{decl} n{s[0]} = {self.get_var(s[0])}()")
        for var_name, var_type in s[1]:
            [self.write_line(s) for s in self.deserializer(var_type, var_name, f"n{s[0]}")]
        self.write_line(f"return n{s[0]}")
        if is_message and len(s[1]) > 0:
            self.indent_level -= 1
            self.write_line("}")
            self.write_line("catch {")
            self.indent_level += 1
            self.write_line("return nil")
            self.indent_level -= 1
            self.write_line("}")

        self.indent_level -= 1
        self.write_line("}")

        self.indent_level -= 1
        self.write_line("}")
        self.write_line()

    def gen_message(self, m: tuple[str, list[tuple[str,str]]]):
        self.gen_struct(m)

    def generate(self) -> str:
        self.output = []

        self.write_line(f"// This file was automatically generated by {LIB_NAME} v{LIB_VERSION}.")
        self.write_line( "// <https://github.com/sjml/beschi>")
        self.write_line(f"// Do not edit directly.")
        self.write_line()
        self.write_line("import Foundation")
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
        self.write_line("// func GetSizeInBytes() -> UInt32")
        self.indent_level -= 1
        self.write_line("}")
        self.write_line()

        if self.protocol.namespace != None:
            self.write_line(f"public /* namespace */ enum {self.protocol.namespace} {{")
            self.indent_level += 1

        self.add_boilerplate()

        msg_types = [mt for mt in self.protocol.messages.keys()]

        self.write_line("public enum MessageType: UInt8 {")
        self.indent_level += 1
        [self.write_line(f"case {k}Type = {i+1}") for i, k in enumerate(msg_types)]
        if len(msg_types) == 0:
            self.write_line("case __NullMessage = 0 /* to keep the compiler happy */")
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
        pref = ""
        if self.protocol.namespace != None:
            pref = f"{self.protocol.namespace}."
        self.write_line(f"let msgTypeByte = try dr.GetUInt8()")
        self.write_line(f"guard let msgType = {pref}MessageType(rawValue: msgTypeByte)")
        self.write_line("else {")
        self.indent_level += 1
        self.write_line("throw DataReader.DataReaderError.InvalidData")
        self.indent_level -= 1
        self.write_line("}")
        self.write_line("switch msgType {")
        self.indent_level += 1
        for msg_type in msg_types:
            self.write_line(f"case {pref}MessageType.{msg_type}Type:")
            self.indent_level += 1
            self.write_line(f"msgList.append({msg_type}.FromBytes(dataReader: dr))")
            self.indent_level -= 1
        if len(msg_types) == 0:
            self.write_line(f"case {pref}MessageType.__NullMessage:")
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

        for s in self.protocol.structs.items():
            self.gen_struct(s)

        for m in self.protocol.messages.items():
            self.gen_message(m)

        if self.protocol.namespace != None:
            self.indent_level -= 1
            self.write_line("}")

        self.write_line()
        assert self.indent_level == 0

        return "\n".join(self.output)
