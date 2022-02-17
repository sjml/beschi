import sys

from ..protocol import Protocol, BASE_TYPES, COLLECTION_TYPES
from ..writer import Writer
from .. import LIB_NAME, LIB_VERSION

LANGUAGE_NAME = "CSharp"


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


    def deserializer(self, var_type: str, var_name: str, parent: str = "this") -> list[str]:
        if parent:
            pref = parent + "."
        else:
            pref = ""
        label = var_name
        if label.endswith("[i]"):
            label = "i"
        if var_type in BASE_TYPES:
            func = None
            if var_type == "byte":
                func = "ReadByte"
            elif var_type == "bool":
                func = "ReadBoolean"
            elif var_type == "uint16":
                func = "ReadUInt16"
            elif var_type == "int16":
                func = "ReadInt16"
            elif var_type == "uint32":
                func = "ReadUInt32"
            elif var_type == "int32":
                func = "ReadInt32"
            elif var_type == "float":
                func = "ReadSingle"
            elif var_type == "double":
                func = "ReadDouble"
            else:
                raise NotImplementedError("Type %s not deserializable yet." % var_type)
            return ["%s%s = br.%s();" % (pref, var_name, func)]
        elif var_type == "string":
            return [
                "uint %sLength = br.ReadUInt32();" % (label),
                "byte[] %sBuffer = br.ReadBytes((int)%sLength);" % (label, label),
                "%s%s = System.Text.Encoding.UTF8.GetString(%sBuffer);" % (pref, var_name, label)
            ]
        elif var_type in self.protocol.structs:
            return [
                "%s%s = %s.FromBytes(br);" % (pref, var_name, var_type)
            ]
        elif var_type[0] == "[" and var_type[-1] == "]":
            interior = var_type[1:-1]
            out = [
                "uint %sLength = br.ReadUInt32();" % (var_name),
                "%s%s = new %s[%sLength];" % (pref, var_name, self.get_var(interior), var_name),
                "for (int i = 0; i < %sLength; i++)" % (var_name),
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
        if var_type in BASE_TYPES:
            return ["bw.Write(%s%s);" % (pref, var_name)]
        elif var_type == "string":
            return [
                "byte[] %sBuffer = System.Text.Encoding.UTF8.GetBytes(%s%s);" % (var_name, pref, var_name),
                "bw.Write((uint)%sBuffer.Length);" % (var_name),
                "bw.Write(%sBuffer);" % (var_name),
            ]
        elif var_type in self.protocol.structs:
            return [
                "%s%s.WriteBytes(bw);" % (pref, var_name)
            ]
        elif var_type[0] == "[" and var_type[-1] == "]":
            interior = var_type[1:-1]
            out = [
                "bw.Write((uint)%s%s.Length);" % (pref, var_name),
                "foreach (%s el in %s%s)" % (self.get_var(interior), pref, var_name),
                "{"
            ]
            out += [self.tab + ser for ser in self.serializer(interior, "el", None)]
            out += "}"
            return out
        else:
            raise NotImplementedError("Type %s not serializable yet." % var_type)


    def gen_struct(self, s: tuple[str, list[tuple[str,str]]]):
        if (s[0] in self.protocol.messages):
            self.write_line("public class %s : Message" % s[0])
        else:
            self.write_line("public class %s" % s[0])
        self.write_line("{")
        self.indent_level += 1

        for var_name, var_type in s[1]:
            if var_type[0] == "[" and var_type[-1] == "]":
                self.write_line("public %s[] %s;" % (self.get_var(var_type[1:-1]), var_name))
            else:
                self.write_line("public %s %s;" % (self.get_var(var_type), var_name))

        if (s[0] in self.protocol.messages):
            self.write_line()
            self.write_line("public override MessageType GetMessageType() { return MessageType.%s; }" % s[0])

        self.write_line()
        override = ""
        if (s[0] in self.protocol.messages):
            override = "override "
        self.write_line("public %svoid WriteBytes(BinaryWriter bw)" % override)
        self.write_line("{")
        self.indent_level += 1
        for var_name, var_type in s[1]:
            [self.write_line(s) for s in self.serializer(var_type, var_name)]
        self.indent_level -= 1
        self.write_line("}")

        self.write_line()
        self.write_line("public static %s FromBytes(BinaryReader br)" % s[0])
        self.write_line("{")
        self.indent_level += 1
        self.write_line("%s n%s = new %s();" % (s[0], s[0], self.get_var(s[0])))
        for var_name, var_type in s[1]:
            [self.write_line(s) for s in self.deserializer(var_type, var_name, "n%s" % s[0])]
        self.write_line("return n%s;" % s[0])
        self.indent_level -= 1
        self.write_line("}")

        self.indent_level -= 1
        self.write_line("}")
        self.write_line()

    def gen_message(self, m: tuple[str, list[tuple[str,str]]]):
        self.gen_struct(m)

    def generate(self) -> str:
        self.output = ""

        self.write_line(f"// This file was automatically generated by {LIB_NAME} v{LIB_VERSION}.")
        self.write_line(f"// Do not edit directly.")
        self.write_line()
        self.write_line("using System;")
        self.write_line("using System.IO;")
        self.write_line("using System.Text;")
        self.write_line()

        if self.protocol.namespace:
            self.write_line("namespace %s" % self.protocol.namespace)
            self.write_line("{")
            self.indent_level += 1

        msg_types = [mt for mt in self.protocol.messages.keys()]

        self.write_line("public enum MessageType")
        self.write_line("{")
        self.indent_level += 1
        self.direct_write(",\n".join([self.indent_string(k + " = %d" % (i+1)) for i, k in enumerate(msg_types)]))
        self.direct_write("\n")
        self.indent_level -= 1
        self.write_line("}")
        self.write_line()

        self.write_line("public abstract class Message {")
        self.indent_level += 1
        self.write_line("abstract public MessageType GetMessageType();")
        self.write_line("abstract public void WriteBytes(BinaryWriter bw);")
        self.write_line()
        self.write_line("public static Message ProcessRawBytes(BinaryReader br)")
        self.write_line("{")
        self.indent_level += 1
        self.write_line("byte msgType = br.ReadByte();")
        self.write_line("switch (msgType)")
        self.write_line("{")
        self.indent_level += 1
        for msg_type in msg_types:
            self.write_line("case (byte)MessageType.%s:" % msg_type)
            self.indent_level += 1
            self.write_line("return %s.FromBytes(br);" % msg_type)
            self.indent_level -= 1
        self.write_line("default:")
        self.indent_level += 1
        self.write_line("throw new NotImplementedException(\"Can't deserialize unknown message type: \" + msgType.ToString());")
        self.indent_level -= 1
        self.indent_level -= 1
        self.write_line("}")
        self.indent_level -= 1
        self.write_line("}")
        self.indent_level -= 1
        self.write_line("}")
        self.write_line()

        for s in self.protocol.structs.items():
            self.gen_struct(s)

        for m in self.protocol.messages.items():
            self.gen_message(m)

        if self.protocol.namespace:
            self.indent_level -= 1
            self.write_line("}")

        self.write_line()
        assert self.indent_level == 0
        return self.output
