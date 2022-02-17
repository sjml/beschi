import sys

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
        if label.endswith("[i]"):
            label = "i"
        if var_type in BASE_TYPE_SIZES:
            func = None
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
                off = 4
            elif var_type == "double":
                func = "getFloat64"
                off = 8

            if func != None:
                return [
                    "%s%s = dv.%s(offset, true);" % (pref, var_name, func),
                    "offset += %d;" % off
                ]

            if var_type == "byte":
                return [
                    "%s%s = dv.getUint8(offset);" % (pref, var_name),
                    "offset += 1;"
                ]
            elif var_type == "bool":
                return [
                    "const %sByte = dv.getUint8(offset);" % (label),
                    "%s%s = (%sByte > 0);" % (pref, var_name, label),
                    "offset += 1;"
                ]
            if func == None:
                raise NotImplementedError("Type %s not deserializable yet." % var_type)
        elif var_type == "string":
            return [
                "const %sLength = dv.getUint32(offset, true);" % (label),
                "offset += 4;",
                "const %sBuffer = new Uint8Array(dv.buffer, offset, %sLength);" % (label, label),
                "offset += %sLength;" % (label),
                "%s%s = textDec.decode(%sBuffer);" % (pref, var_name, label),
            ]
        elif var_type in self.protocol.structs:
            return [
                "const %sRetVal = %s.FromBytes(dv, offset);" % (label, var_type),
                "%s%s = %sRetVal.val;" % (pref, var_name, label),
                "offset = %sRetVal.offset;" % (label)
            ]
        elif var_type[0] == "[" and var_type[-1] == "]":
            interior = var_type[1:-1]
            out = [
                "const %sLength = dv.getUint32(offset, true);" % (var_name),
                "offset += 4;",
                "%s%s = Array<%s>(%sLength);" % (pref, var_name, self.get_var(interior), var_name),
                "for (let i = 0; i < %sLength; i++)" % (var_name),
                "{"
            ]
            out += [
                self.tab + deser for deser in self.deserializer(
                    interior, "%s[i]" % (var_name), parent
                )
            ]
            out += "}"
            return out
        else:
            raise NotImplementedError("Type %s not deserializable yet." % var_type)


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
                    "dv.%s(offset, %s%s, true);" % (func, pref, var_name),
                    "offset += %d;" % off
                ]
            if var_type == "byte":
                return [
                    "dv.setUint8(offset, %s%s);" % (pref, var_name),
                    "offset += 1;"
                ]
            if var_type == "bool":
                return [
                    "dv.setUint8(offset, %s%s ? 1 : 0);" % (pref, var_name),
                    "offset += 1;"
                ]
        elif var_type == "string":
            return [
                "const %sBuffer = textEnc.encode(%s%s);" % (var_name, pref, var_name),
                "const %sArr = new Uint8Array(dv.buffer);" % (var_name),
                "dv.setUint32(offset, %sBuffer.byteLength, true);" % (var_name),
                "offset += 4;",
                "%sArr.set(%sBuffer, offset);" % (var_name, var_name),
                "offset += %sBuffer.byteLength;" % (var_name)
            ]
        elif var_type in self.protocol.structs:
            return [
                "offset = %s%s.WriteBytes(dv, offset);" % (pref, var_name)
            ]
        elif var_type[0] == "[" and var_type[-1] == "]":
            interior = var_type[1:-1]
            out = [
                "dv.setUint32(offset, %s%s.length, true);" % (pref, var_name),
                "offset += 4;",
                "for (let i = 0; i < %s%s.length; i++) {" % (pref, var_name),
                self.tab + "let el = %s%s[i];" % (pref, var_name)
            ]
            out += [self.tab + ser for ser in self.serializer(interior, "el", None)]
            out += "}"
            return out
        else:
            raise NotImplementedError("Type %s not serializable yet." % var_type)


    def gen_struct(self, s: tuple[str, list[tuple[str,str]]]):
        is_message = False
        if s[0] in self.protocol.messages:
            is_message = True

        if is_message:
            self.write_line("export class %s implements Message {" % s[0])
        else:
            self.write_line("export class %s {" % s[0])
        self.indent_level += 1

        for var_name, var_type in s[1]:
            if var_type[0] == "[" and var_type[-1] == "]":
                self.write_line("%s: %s[] = [];" % (var_name, self.get_var(var_type[1:-1])))
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
            self.write_line("GetMessageType() : MessageType {")
            self.indent_level += 1
            self.write_line("return MessageType.%s;" % s[0])
            self.indent_level -=1
            self.write_line("}")
            self.write_line()

        self.write_line("WriteBytes(dv: DataView, offset: number) : number {")
        self.indent_level += 1
        for var_name, var_type in s[1]:
            [self.write_line(s) for s in self.serializer(var_type, var_name)]
        self.write_line("return offset;")
        self.indent_level -= 1
        self.write_line("}")
        self.write_line()

        self.write_line("static FromBytes(dv: DataView, offset: number): {val: %s, offset: number} {" % s[0])
        self.indent_level += 1
        self.write_line("const n%s = new %s();" % (s[0], self.get_var(s[0])))
        for var_name, var_type in s[1]:
            [self.write_line(s) for s in self.deserializer(var_type, var_name, "n%s" % s[0])]
        self.write_line("return {val: n%s, offset: offset};" % s[0])
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
        self.write_line("WriteBytes(dv: DataView, offset: number) : number;")
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
        [self.write_line(k + " = %d," % (i+1)) for i, k in enumerate(msg_types)]
        self.indent_level -= 1
        self.write_line("}")
        self.write_line()

        self.write_line("export function ProcessRawBytes(dv: DataView, offset: number): {val: Message | null, offset: number} {")
        self.indent_level += 1
        self.write_line("const msgType: number = dv.getUint8(offset);")
        self.write_line("offset += 1;")
        self.write_line("switch (msgType) {")
        self.indent_level += 1
        for msg_type in msg_types:
            self.write_line("case MessageType.%s:" % msg_type)
            self.indent_level += 1
            self.write_line("return %s.FromBytes(dv, offset);" % msg_type)
            self.indent_level -= 1
        self.write_line("default:")
        self.indent_level += 1
        self.write_line("return {val: null, offset: offset};")
        self.indent_level -= 1
        self.indent_level -= 1
        self.write_line("}")
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
