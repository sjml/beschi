import sys

from ..protocol import BASE_TYPES, Protocol
from ..writer import Writer
from .. import LIB_NAME, LIB_VERSION


class TypeScriptWriter(Writer):
    def __init__(self, p: Protocol):
        super().__init__(protocol=p, tab="  ")

        for var_type in BASE_TYPES:
            if var_type == "bool":
                self.type_mapping[var_type] = "boolean"
            else:
                # <sigh>, JavaScript
                self.type_mapping[var_type] = "number"


    def deserializer(self, p: Protocol, varType: str, varName: str, parent: str = "this") -> list[str]:
        if parent:
            pref = parent + "."
        else:
            pref = ""
        label = varName
        if label.endswith("[i]"):
            label = "i"
        if varType in p.baseTypes.keys():
            func = None
            off = 0
            if varType == "uint16":
                func = "getUint16"
                off = 2
            elif varType == "int16":
                func = "getInt16"
                off = 2
            elif varType == "uint32":
                func = "getUint32"
                off = 4
            elif varType == "int32":
                func = "getInt32"
                off = 4
            elif varType == "float":
                func = "getFloat32"
                off = 4
            elif varType == "double":
                func = "getFloat64"
                off = 8

            if func != None:
                return [
                    "%s%s = dv.%s(offset, true);" % (pref, varName, func),
                    "offset += %d;" % off
                ]

            if varType == "byte":
                return [
                    "%s%s = dv.getUint8(offset);" % (pref, varName),
                    "offset += 1;"
                ]
            elif varType == "bool":
                return [
                    "const %sByte = dv.getUint8(offset);" % (label),
                    "%s%s = (%sByte > 0);" % (pref, varName, label),
                    "offset += 1;"
                ]
            if func == None:
                raise NotImplementedError("Type %s not deserializable yet." % varType)
        elif varType == "string":
            return [
                "const %sLength = dv.getUint32(offset, true);" % (label),
                "offset += 4;",
                "const %sBuffer = new Uint8Array(dv.buffer, offset, %sLength);" % (label, label),
                "offset += %sLength;" % (label),
                "%s%s = textDec.decode(%sBuffer);" % (pref, varName, label),
            ]
        elif varType in p.structs.keys():
            return [
                "const %sRetVal = %s.FromBytes(dv, offset);" % (label, varType),
                "%s%s = %sRetVal.val;" % (pref, varName, label),
                "offset = %sRetVal.offset;" % (label)
            ]
        elif varType[0] == "[" and varType[-1] == "]":
            interior = varType[1:-1]
            out = [
                "const %sLength = dv.getUint32(offset, true);" % (varName),
                "offset += 4;",
                "%s%s = Array<%s>(%sLength);" % (pref, varName, self.var(interior), varName),
                "for (let i = 0; i < %sLength; i++)" % (varName),
                "{"
            ]
            out += [
                self.tab + deser for deser in self.deserializer(
                    p, interior, "%s[i]" % (varName), parent
                )
            ]
            out += "}"
            return out
        else:
            raise NotImplementedError("Type %s not deserializable yet." % varType)


    def serializer(self, p: Protocol, varType: str, varName: str, parent: str = "this") -> list[str]:
        if parent:
            pref = parent + "."
        else:
            pref = ""
        if varType in p.baseTypes.keys():
            func = None
            off = 0
            if varType == "uint16":
                func = "setUint16"
                off = 2
            if varType == "int16":
                func = "setInt16"
                off = 2
            if varType == "uint32":
                func = "setUint32"
                off = 4
            if varType == "int32":
                func = "setInt32"
                off = 4
            if varType == "float":
                func = "setFloat32"
                off = 4
            if varType == "double":
                func = "setFloat64"
                off = 8

            if func != None:
                return [
                    "dv.%s(offset, %s%s, true);" % (func, pref, varName),
                    "offset += %d;" % off
                ]
            if varType == "byte":
                return [
                    "dv.setUint8(offset, %s%s);" % (pref, varName),
                    "offset += 1;"
                ]
            if varType == "bool":
                return [
                    "dv.setUint8(offset, %s%s ? 1 : 0);" % (pref, varName),
                    "offset += 1;"
                ]
        elif varType == "string":
            return [
                "const %sBuffer = textEnc.encode(%s%s);" % (varName, pref, varName),
                "const %sArr = new Uint8Array(dv.buffer);" % (varName),
                "dv.setUint32(offset, %sBuffer.byteLength, true);" % (varName),
                "offset += 4;",
                "%sArr.set(%sBuffer, offset);" % (varName, varName),
                "offset += %sBuffer.byteLength;" % (varName)
            ]
        elif varType in p.structs.keys():
            return [
                "offset = %s%s.WriteBytes(dv, offset);" % (pref, varName)
            ]
        elif varType[0] == "[" and varType[-1] == "]":
            interior = varType[1:-1]
            out = [
                "dv.setUint32(offset, %s%s.length, true);" % (pref, varName),
                "offset += 4;",
                "for (let i = 0; i < %s%s.length; i++) {" % (pref, varName),
                self.tab + "let el = %s%s[i];" % (pref, varName)
            ]
            out += [self.tab + ser for ser in self.serializer(p, interior, "el", None)]
            out += "}"
            return out
        else:
            raise NotImplementedError("Type %s not serializable yet." % varType)


    def gen_struct(self, p: Protocol, s: tuple[str, list[tuple[str,str]]]):
        isMessage = False
        if s[0] in p.messages.keys():
            isMessage = True

        if isMessage:
            self.wl("export class %s implements Message {" % s[0])
        else:
            self.wl("export class %s {" % s[0])
        self.ind += 1

        for varData in s[1]:
            varName, varType = varData
            if varType[0] == "[" and varType[-1] == "]":
                self.wl("%s: %s[];" % (varName, self.var(varType[1:-1])))
            else:
                self.wl("%s: %s;" % (varName, self.var(varType)))
        self.wl()

        if isMessage:
            self.wl("GetType() : MessageType {")
            self.ind += 1
            self.wl("return MessageType.%s;" % s[0])
            self.ind -=1
            self.wl("}")
            self.wl()

        self.wl("WriteBytes(dv: DataView, offset: number) : number {")
        self.ind += 1
        for varName, varType in s[1]:
            [self.wl(s) for s in self.serializer(p, varType, varName)]
        self.wl("return offset;")
        self.ind -= 1
        self.wl("}")
        self.wl()

        self.wl("static FromBytes(dv: DataView, offset: number): {val: %s, offset: number} {" % s[0])
        self.ind += 1
        self.wl("const n%s = new %s();" % (s[0], self.var(s[0])))
        for varName, varType in s[1]:
            [self.wl(s) for s in self.deserializer(p, varType, varName, "n%s" % s[0])]
        self.wl("return {val: n%s, offset: offset};" % s[0])
        self.ind -= 1
        self.wl("}")

        self.ind -= 1
        self.wl("}")
        self.wl()

    def gen_message(self, p: Protocol, m: tuple[str, list[tuple[str,str]]]):
        self.wl("@staticImplements<MessageStatic>()")
        self.gen_struct(p, m)

    def generate(self, p: Protocol) -> str:
        self.output = ""

        self.wl(f"// This file was automatically generated by {LIB_NAME} v{LIB_VERSION}.")
        self.wl(f"// Do not edit directly.")
        self.wl()

        if p.namespace:
            self.wl("export namespace %s" % p.namespace)
            self.wl("{")
            self.ind += 1

        self.wl("const textDec = new TextDecoder('utf-8');")
        self.wl("const textEnc = new TextEncoder();")
        self.wl()

        self.wl("export interface Message {")
        self.ind += 1
        self.wl("GetType() : MessageType;")
        self.wl("WriteBytes(dv: DataView, offset: number) : number;")
        self.ind -= 1
        self.wl("}")
        self.wl("export interface MessageStatic {")
        self.ind += 1
        self.wl("new(): Message;")
        self.wl("FromBytes(dv: DataView, offset: number): {val: Message, offset: number};")
        self.ind -= 1
        self.wl("}")
        self.wl("function staticImplements<T>() {")
        self.ind += 1
        self.wl("return (constructor: T) => {}")
        self.ind -= 1
        self.wl("}")
        self.wl()

        msgTypes = [mt for mt in p.messages.keys()]

        self.wl("export enum MessageType")
        self.wl("{")
        self.ind += 1
        self.dw(",\n".join([self.ws(k + " = %d" % i) for i, k in enumerate(msgTypes)]))
        self.dw("\n")
        self.ind -= 1
        self.wl("}")
        self.wl()

        for s in p.structs.items():
            self.gen_struct(p, s)

        for m in p.messages.items():
            self.gen_message(p, m)

        if p.namespace:
            self.ind -= 1
            self.wl("}")

        self.wl()
        assert self.ind == 0
        return self.output
