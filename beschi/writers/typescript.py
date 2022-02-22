from ..protocol import Protocol, BASE_TYPE_SIZES, COLLECTION_TYPES
from ..writer import Writer
from .. import LIB_NAME, LIB_VERSION

LANGUAGE_NAME = "TypeScript"


class TypeScriptWriter(Writer):
    language_name = LANGUAGE_NAME
    default_extension = ".ts"

    def __init__(self, p: Protocol):
        super().__init__(protocol=p, tab="  ")

        for var_type in BASE_TYPE_SIZES:
            if var_type == "bool":
                self.type_mapping[var_type] = "boolean"
            elif var_type in ["int64", "uint64"]:
                self.type_mapping[var_type] = "bigint"
            else:
                # <sigh>, JavaScript
                self.type_mapping[var_type] = "number"


    def deserializer(self, var_type: str, var_name: str, parent: str = "this") -> list[str]:
        if parent:
            pref = parent + "."
        else:
            pref = ""
        label = var_name
        if label.endswith("_i]"):
            label = "i_"
        if var_type in BASE_TYPE_SIZES:
            func = None
            pre_wrap = ""
            post_wrap = ""
            off = 0
            if var_type == "uint16":
                func = "getUint16"
                off = 2
            elif var_type == "int16":
                func = "getInt16"
                off = 2
            elif var_type == "uint32":
                func = "getUint32"
                off = 4
            elif var_type == "int32":
                func = "getInt32"
                off = 4
            elif var_type == "uint64":
                func = "getBigUint64"
                off = 8
            elif var_type == "int64":
                func = "getBigInt64"
                off = 8
            elif var_type == "float":
                func = "getFloat32"
                pre_wrap = "Math.fround("
                post_wrap = ")"
                off = 4
            elif var_type == "double":
                func = "getFloat64"
                off = 8

            if func != None:
                return [
                    f"{pref}{var_name} = {pre_wrap}dv.{func}(offset, true){post_wrap};",
                    f"offset += {off};"
                ]

            if var_type == "byte":
                return [
                    f"{pref}{var_name} = dv.getUint8(offset);",
                    "offset += 1;"
                ]
            elif var_type == "bool":
                return [
                    f"const {label}Byte = dv.getUint8(offset);",
                    f"{pref}{var_name} = ({label}Byte > 0);",
                    "offset += 1;"
                ]
            if func == None:
                raise NotImplementedError(f"Type {var_type} not deserializable yet.")
        elif var_type == "string":
            return [
                f"const {label}Length = dv.getUint32(offset, true);",
                "offset += 4;",
                f"const {label}Buffer = new Uint8Array(dv.buffer, offset, {label}Length);",
                f"offset += {label}Length;",
                f"{pref}{var_name} = textDec.decode({label}Buffer);",
            ]
        elif var_type in self.protocol.structs:
            return [
                f"const {label}RetVal = {var_type}.FromBytes(dv, offset);",
                f"{pref}{var_name} = {label}RetVal.val;",
                f"offset = {label}RetVal.offset;",
            ]
        elif var_type[0] == "[" and var_type[-1] == "]":
            interior = var_type[1:-1]
            out = [
                f"const {var_name}Length = dv.getUint32(offset, true);",
                "offset += 4;",
                f"{pref}{var_name} = Array<{self.get_var(interior)}>({var_name}Length);",
                f"for (let {var_name}_i = 0; {var_name}_i < {var_name}Length; {var_name}_i++)",
                "{"
            ]
            out += [
                self.tab + deser for deser in self.deserializer(
                    interior, f"{var_name}[{var_name}_i]", parent
                )
            ]
            out += "}"
            return out
        else:
            raise NotImplementedError(f"Type {var_type} not deserializable yet.")


    def serializer(self, var_type: str, var_name: str, parent: str = "this") -> list[str]:
        if parent:
            pref = parent + "."
        else:
            pref = ""
        if var_type in BASE_TYPE_SIZES:
            func = None
            off = 0
            if var_type == "uint16":
                func = "setUint16"
                off = 2
            if var_type == "int16":
                func = "setInt16"
                off = 2
            if var_type == "uint32":
                func = "setUint32"
                off = 4
            if var_type == "int32":
                func = "setInt32"
                off = 4
            if var_type == "uint64":
                func = "setBigUint64"
                off = 8
            if var_type == "int64":
                func = "setBigInt64"
                off = 8
            if var_type == "float":
                func = "setFloat32"
                off = 4
            if var_type == "double":
                func = "setFloat64"
                off = 8

            if func != None:
                return [
                    f"dv.{func}(offset, {pref}{var_name}, true);",
                    f"offset += {off};"
                ]
            if var_type == "byte":
                return [
                    f"dv.setUint8(offset, {pref}{var_name});",
                    "offset += 1;"
                ]
            if var_type == "bool":
                return [
                    f"dv.setUint8(offset, {pref}{var_name} ? 1 : 0);",
                    "offset += 1;"
                ]
        elif var_type == "string":
            return [
                f"const {var_name}Buffer = textEnc.encode({pref}{var_name});",
                f"const {var_name}Arr = new Uint8Array(dv.buffer);",
                f"dv.setUint32(offset, {var_name}Buffer.byteLength, true);",
                "offset += 4;",
                f"{var_name}Arr.set({var_name}Buffer, offset);",
                f"offset += {var_name}Buffer.byteLength;",
            ]
        elif var_type in self.protocol.structs:
            return [
                f"offset = {pref}{var_name}.WriteBytes(dv, offset);"
            ]
        elif var_type[0] == "[" and var_type[-1] == "]":
            interior = var_type[1:-1]
            out = [
                f"dv.setUint32(offset, {pref}{var_name}.length, true);",
                "offset += 4;",
                f"for (let {var_name}_i = 0; {var_name}_i < {pref}{var_name}.length; {var_name}_i++) {{",
                self.tab + f"let el = {pref}{var_name}[{var_name}_i];",
            ]
            out += [self.tab + ser for ser in self.serializer(interior, "el", None)]
            out += "}"
            return out
        else:
            raise NotImplementedError(f"Type {var_type} not serializable yet.")

    def gen_measurement(self, s: tuple[str, list[tuple[str,str]]], accessor_prefix: str = "") -> tuple[list[str], int]:
        lines: list[str] = []

        accum = 0
        if self.protocol.is_simple(s[0]):
            lines.append(f"return {self.protocol.calculate_size(s[0])};")
        else:
            size_init = "let size: number = 0;"
            lines.append(size_init)

            for var_name, var_type in s[1]:
                if self.protocol.is_simple(var_type):
                    accum += self.protocol.calculate_size(var_type)
                else:
                    if var_type == "string":
                        accum += BASE_TYPE_SIZES["uint32"]
                        lines.append(f"size += textEnc.encode({accessor_prefix}{var_name}).byteLength;")
                    elif var_type == "[string]":
                        accum += BASE_TYPE_SIZES["uint32"]
                        lines.append(f"for (let {var_name}_i=0; {var_name}_i < {accessor_prefix}{var_name}.length; {var_name}_i++) {{")
                        lines.append(f"{self.tab}size += {BASE_TYPE_SIZES['uint32']} + textEnc.encode({accessor_prefix}{var_name}[{var_name}_i]).byteLength;")
                        lines.append("}")
                    elif var_type[0] == "[" and var_type[-1] == "]":
                        listed_var_type = var_type[1:-1]
                        if self.protocol.is_simple(listed_var_type):
                            accum += BASE_TYPE_SIZES["uint32"]
                            lines.append(f"size += {accessor_prefix}{var_name}.length * {self.protocol.calculate_size(listed_var_type)};")
                        else:
                            accum += BASE_TYPE_SIZES["uint32"]
                            lines.append(f"for (let {var_name}_i=0; {var_name}_i < {accessor_prefix}{var_name}.length; {var_name}_i++) {{")
                            clines, caccum = self.gen_measurement((var_type, self.protocol.structs[listed_var_type]), f"{accessor_prefix}{var_name}[{var_name}_i].")
                            if clines[0] == size_init:
                                clines = clines[1:]
                            clines.append(f"size += {caccum};")
                            lines += [f"{self.tab}{l}" for l in clines]
                            lines.append("}")
                    else:
                        clines, caccum = self.gen_measurement((var_type, self.protocol.structs[var_type]), f"{accessor_prefix}{var_name}.")
                        if clines[0] == size_init:
                            clines = clines[1:]
                        lines += clines
                        accum += caccum
        return lines, accum

    def gen_struct(self, s: tuple[str, list[tuple[str,str]]]):
        is_message = False
        if s[0] in self.protocol.messages:
            is_message = True

        if is_message:
            self.write_line(f"export class {s[0]} implements Message {{")
        else:
            self.write_line(f"export class {s[0]} {{")
        self.indent_level += 1

        for var_name, var_type in s[1]:
            if var_type[0] == "[" and var_type[-1] == "]":
                self.write_line(f"{var_name}: {self.get_var(var_type[1:-1])}[] = [];")
            else:
                var_type = self.get_var(var_type)
                default_value = "0"
                if var_type == "bigint":
                    default_value = "0n"
                elif var_type == "boolean":
                    default_value = "false"
                elif var_type == "string":
                    default_value = "\"\""
                elif var_type in self.protocol.structs:
                    default_value = None
                self.write_line(f"{var_name}: {var_type}{f' = {default_value}' if default_value else ''};")
        self.write_line()

        if is_message:
            self.write_line(f"GetMessageType() : MessageType {{ return MessageType.{s[0]}Type; }}")
            self.write_line()
            self.write_line("GetSizeInBytes(): number {")
            self.indent_level += 1
            measure_lines, accumulator = self.gen_measurement(s, "this.")
            [self.write_line(s) for s in measure_lines]
            if accumulator > 0:
                self.write_line(f"size += {accumulator};")
            if len(measure_lines) > 1:
                self.write_line(f"return size;")
            self.indent_level -= 1
            self.write_line("}")
            self.write_line()
            self.write_line("WriteBytes(dv: DataView, tag: boolean, offset: number) : number {")
            self.indent_level += 1
            self.write_line("if (tag) {")
            self.indent_level += 1
            self.write_line(f"dv.setUint8(offset, MessageType.{s[0]}Type);")
            self.write_line("offset += 1;")
            self.indent_level -= 1
            self.write_line("}")
        else:
            self.write_line("WriteBytes(dv: DataView, offset: number) : number {")
            self.indent_level += 1

        for var_name, var_type in s[1]:
            [self.write_line(s) for s in self.serializer(var_type, var_name)]
        self.write_line("return offset;")
        self.indent_level -= 1
        self.write_line("}")
        self.write_line()

        self.write_line(f"static FromBytes(dv: DataView, offset: number): {{val: {s[0]}, offset: number}} {{")
        self.indent_level += 1
        if is_message:
            self.write_line("try {")
            self.indent_level += 1
        self.write_line(f"const n{s[0]} = new {self.get_var(s[0])}();")
        for var_name, var_type in s[1]:
            [self.write_line(s) for s in self.deserializer(var_type, var_name, f"n{s[0]}")]
        self.write_line(f"return {{val: n{s[0]}, offset: offset}};")
        if is_message:
            self.indent_level -= 1
            self.write_line("}")
            self.write_line("catch (RangeError) {")
            self.indent_level += 1
            self.write_line("return {val: null, offset: offset};")
            self.indent_level -= 1
            self.write_line("}")

        self.indent_level -= 1
        self.write_line("}")

        self.indent_level -= 1
        self.write_line("}")
        self.write_line()

    def gen_message(self, m: tuple[str, list[tuple[str,str]]]):
        self.write_line("@staticImplements<MessageStatic>()")
        self.gen_struct(m)

    def generate(self) -> str:
        self.output = []

        self.write_line(f"// This file was automatically generated by {LIB_NAME} v{LIB_VERSION}.")
        self.write_line(f"// Do not edit directly.")
        self.write_line()

        self.write_line("const textDec = new TextDecoder('utf-8');")
        self.write_line("const textEnc = new TextEncoder();")
        self.write_line()

        self.write_line("export interface Message {")
        self.indent_level += 1
        self.write_line("GetMessageType() : MessageType;")
        self.write_line("WriteBytes(dv: DataView, tag: boolean, offset: number) : number;")
        self.write_line("GetSizeInBytes() : number;")
        self.indent_level -= 1
        self.write_line("}")
        self.write_line("export interface MessageStatic {")
        self.indent_level += 1
        self.write_line("new(): Message;")
        self.write_line("FromBytes(dv: DataView, offset: number): {val: Message | null, offset: number};")
        self.indent_level -= 1
        self.write_line("}")
        self.write_line("function staticImplements<T>() {")
        self.indent_level += 1
        self.write_line("return (constructor: T) => {}")
        self.indent_level -= 1
        self.write_line("}")
        self.write_line()

        msg_types = [mt for mt in self.protocol.messages.keys()]

        self.write_line("export enum MessageType {")
        self.indent_level += 1
        [self.write_line(f"{k}Type = {i+1},") for i, k in enumerate(msg_types)]
        self.indent_level -= 1
        self.write_line("}")
        self.write_line()

        self.write_line("export function ProcessRawBytes(dv: DataView, offset: number): {vals: Message[], offset: number} {")
        self.indent_level += 1
        self.write_line("const msgList: Message[] = [];")
        self.write_line("while (offset < dv.byteLength) {")
        self.indent_level += 1
        self.write_line("const msgType: number = dv.getUint8(offset);")
        self.write_line("offset += 1;")
        self.write_line("let msgRet: any = null;")
        self.write_line("switch (msgType) {")
        self.indent_level += 1
        for msg_type in msg_types:
            self.write_line(f"case MessageType.{msg_type}Type:")
            self.indent_level += 1
            self.write_line(f"msgRet = {msg_type}.FromBytes(dv, offset);")
            self.write_line("break;")
            self.indent_level -= 1
        self.write_line("default:")
        self.indent_level += 1
        self.write_line("msgRet = {val: null, offset: offset};")
        self.write_line("break;")
        self.indent_level -= 1
        self.indent_level -= 1
        self.write_line("}")
        self.write_line("offset = msgRet.offset;")
        self.write_line("msgList.push(msgRet.val);")
        self.write_line("if (msgRet.val == null) {")
        self.indent_level += 1
        self.write_line("break;")
        self.indent_level -= 1
        self.write_line("}")
        self.indent_level -= 1
        self.write_line("}")
        self.write_line("return {vals: msgList, offset: offset};")
        self.indent_level -= 1
        self.write_line("}")
        self.write_line()

        for s in self.protocol.structs.items():
            self.gen_struct(s)

        for m in self.protocol.messages.items():
            self.gen_message(m)

        self.write_line()
        assert self.indent_level == 0

        return "\n".join(self.output)
