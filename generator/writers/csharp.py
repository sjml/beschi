import sys

from ..protocol import Protocol, BASE_TYPES
from ..writer import Writer
from .. import LIB_NAME, LIB_VERSION


class CSharpWriter(Writer):
    def __init__(self, p: Protocol):
        super().__init__(protocol=p, tab="    ")

        self.type_mapping["byte"] = "byte"
        self.type_mapping["bool"] = "bool"
        self.type_mapping["uint16"] = "ushort"
        self.type_mapping["int16"] = "short"
        self.type_mapping["uint32"] = "uint"
        self.type_mapping["int32"] = "int"
        self.type_mapping["float"] = "float"
        self.type_mapping["double"] = "double"


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
            if varType == "byte":
                func = "ReadByte"
            elif varType == "bool":
                func = "ReadBoolean"
            elif varType == "uint16":
                func = "ReadUInt16"
            elif varType == "int16":
                func = "ReadInt16"
            elif varType == "uint32":
                func = "ReadUInt32"
            elif varType == "int32":
                func = "ReadInt32"
            elif varType == "float":
                func = "ReadSingle"
            elif varType == "double":
                func = "ReadDouble"
            else:
                raise NotImplementedError("Type %s not deserializable yet." % varType)
            return ["%s%s = br.%s();" % (pref, varName, func)]
        elif varType == "string":
            return [
                "uint %sLength = br.ReadUInt32();" % (label),
                "byte[] %sBuffer = br.ReadBytes((int)%sLength);" % (label, label),
                "%s%s = System.Text.Encoding.UTF8.GetString(%sBuffer);" % (pref, varName, label)
            ]
        elif varType in p.structs.keys():
            return [
                "%s%s = %s.FromBytes(br);" % (pref, varName, varType)
            ]
        elif varType[0] == "[" and varType[-1] == "]":
            interior = varType[1:-1]
            out = [
                "uint %sLength = br.ReadUInt32();" % (varName),
                "%s%s = new %s[%sLength];" % (pref, varName, self.var(interior), varName),
                "for (int i = 0; i < %sLength; i++)" % (varName),
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
            return ["bw.Write(%s%s);" % (pref, varName)]
        elif varType == "string":
            return [
                "byte[] %sBuffer = System.Text.Encoding.UTF8.GetBytes(%s%s);" % (varName, pref, varName),
                "bw.Write((uint)%sBuffer.Length);" % (varName),
                "bw.Write(%sBuffer);" % (varName),
            ]
        elif varType in p.structs.keys():
            return [
                "%s%s.WriteBytes(bw);" % (pref, varName)
            ]
        elif varType[0] == "[" and varType[-1] == "]":
            interior = varType[1:-1]
            out = [
                "bw.Write((uint)%s%s.Length);" % (pref, varName),
                "foreach (%s el in %s%s)" % (self.var(interior), pref, varName),
                "{"
            ]
            out += [self.tab + ser for ser in self.serializer(p, interior, "el", None)]
            out += "}"
            return out
        else:
            raise NotImplementedError("Type %s not serializable yet." % varType)


    def gen_struct(self, p: Protocol, s: tuple[str, list[tuple[str,str]]]):
        if (s[0] in p.messages.keys()):
            self.wl("public class %s : Message" % s[0])
        else:
            self.wl("public class %s" % s[0])
        self.wl("{")
        self.ind += 1

        for varData in s[1]:
            varName, varType = varData
            if varType[0] == "[" and varType[-1] == "]":
                self.wl("public %s[] %s;" % (self.var(varType[1:-1]), varName))
            else:
                self.wl("public %s %s;" % (self.var(varType), varName))

        if (s[0] in p.messages.keys()):
            self.wl()
            self.wl("public override MessageType GetMessageType() { return MessageType.%s; }" % s[0])

        self.wl()
        override = ""
        if (s[0] in p.messages.keys()):
            override = "override "
        self.wl("public %svoid WriteBytes(BinaryWriter bw)" % override)
        self.wl("{")
        self.ind += 1
        for varName, varType in s[1]:
            [self.wl(s) for s in self.serializer(p, varType, varName)]
        self.ind -= 1
        self.wl("}")

        self.wl()
        self.wl("public static %s FromBytes(BinaryReader br)" % s[0])
        self.wl("{")
        self.ind += 1
        self.wl("%s n%s = new %s();" % (s[0], s[0], self.var(s[0])))
        for varName, varType in s[1]:
            [self.wl(s) for s in self.deserializer(p, varType, varName, "n%s" % s[0])]
        self.wl("return n%s;" % s[0])
        self.ind -= 1
        self.wl("}")

        self.ind -= 1
        self.wl("}")
        self.wl()

    def gen_message(self, p: Protocol, m: tuple[str, list[tuple[str,str]]]):
        self.gen_struct(p, m)

    def generate(self, p: Protocol) -> str:
        self.output = ""

        self.wl(f"// This file was automatically generated by {LIB_NAME} v{LIB_VERSION}.")
        self.wl(f"// Do not edit directly.")
        self.wl()
        self.wl("using System;")
        self.wl("using System.IO;")
        self.wl("using System.Text;")
        self.wl()

        if p.namespace:
            self.wl("namespace %s" % p.namespace)
            self.wl("{")
            self.ind += 1

        msgTypes = [mt for mt in p.messages.keys()]

        self.wl("public enum MessageType")
        self.wl("{")
        self.ind += 1
        self.dw(",\n".join([self.ws(k + " = %d" % i) for i, k in enumerate(msgTypes)]))
        self.dw("\n")
        self.ind -= 1
        self.wl("}")
        self.wl()

        self.wl("public abstract class Message {")
        self.ind += 1
        self.wl("abstract public void WriteBytes(BinaryWriter bw);")
        self.wl("abstract public MessageType GetMessageType();")
        self.wl()
        self.wl("public static Message ProcessRawBytes(BinaryReader br)")
        self.wl("{")
        self.ind += 1
        self.wl("byte msgType = br.ReadByte();")
        self.wl("switch (msgType)")
        self.wl("{")
        self.ind += 1
        for mType in msgTypes:
            self.wl("case (byte)MessageType.%s:" % mType)
            self.ind += 1
            self.wl("return %s.FromBytes(br);" % mType)
            self.ind -= 1
        self.wl("default:")
        self.ind += 1
        self.wl("throw new NotImplementedException(\"Can't deserialize unknown message type: \" + msgType.ToString());")
        self.ind -= 1
        self.ind -= 1
        self.wl("}")
        self.ind -= 1
        self.wl("}")
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
