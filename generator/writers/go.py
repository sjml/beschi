import sys
import re
import copy
from collections import OrderedDict

from ..protocol import Protocol
from ..writer import Writer
from .. import LIB_NAME, LIB_VERSION


class GoWriter(Writer):
    def __init__(self, p: Protocol):
        super().__init__(protocol=p, tab="\t")

        self.type_mapping["byte"] = "byte"
        self.type_mapping["bool"] = "bool"
        self.type_mapping["uint16"] = "uint16"
        self.type_mapping["int16"] = "int16"
        self.type_mapping["uint32"] = "uint32"
        self.type_mapping["int32"] = "int32"
        self.type_mapping["float"] = "float32"
        self.type_mapping["double"] = "float64"



    def simple(self, p: Protocol, varType: str) -> bool:
        if varType in p.baseTypes.keys():
            return True
        elif varType in p.complexTypes:
            return False
        elif varType[0] == "[" and varType[-1] == "]":
            return False
        elif varType in p.structs.keys() or varType in p.messages.keys():
            datums: list[tuple[str,str]] = None
            if varType in p.structs.keys():
                datums = p.structs[varType]
            else:
                datums = p.messages[varType]
            for _, vt in datums:
                if not self.simple(p, vt):
                    return False
            return True
        else:
            raise NotImplementedError("Can't determine simplicity of %s." % varType)

    def deserializer(self, p: Protocol, varType: str, varName: str, parent: str = None) -> list[str]:
        if parent == None:
            pref = ""
            ptr = ""
            this = "input"
        else:
            pref = "%s." % parent
            ptr = "&"
            this = pref + varName
        label = varName
        if label.endswith("[i]"):
            label = "i"

        if self.simple(p, varType):
            return ["binary.Read(data, binary.LittleEndian, %s%s%s)" % (ptr, pref, varName)]
        elif varType in p.structs.keys() or varType in p.messages.keys():
            fields: list[tuple[str,str]] = None
            if varType in p.structs.keys():
                fields = p.structs[varType]
            elif varType in p.messages.keys():
                fields = p.messages[varType]
            output: list[str] = []
            for vn, vt in fields:
                output += self.deserializer(p, vt, vn, this)
            return output
        elif varType == "string":
            return ["readString(data, %s%s%s)" % (ptr, pref, varName)]
        elif varType[0] == "[" and varType[-1] == "]":
            interior = varType[1:-1]
            out = [
                "var %sLen uint32" % label,
                "binary.Read(data, binary.LittleEndian, &%sLen)" % label,
                "%s%s = make([]%s, %sLen)" % (pref, varName, interior, label),
                "for i := (uint32)(0); i < %sLen; i++ {" % label
            ]
            out += [
                self.tab + deser for deser in self.deserializer(p, interior, "%s[i]" % (varName), parent)
            ]
            out += ["}"]
            return out
        else:
            raise NotImplementedError("Type %s not deserializable yet." % varType)


    def serializer(self, p: Protocol, varType: str, varName: str, parent: str = None) -> list[str]:
        if parent == None:
            pref = ""
            ptr = ""
            this = "output"
        else:
            pref = "%s." % parent
            ptr = "&"
            this = pref + varName
        label = varName
        if label.endswith("[i]"):
            label = "i"

        if self.simple(p, varType):
            return ["binary.Write(data, binary.LittleEndian, %s%s%s)" % (ptr, pref, varName)]
        elif varType in p.structs.keys() or varType in p.messages.keys():
            fields: list[tuple[str,str]] = None
            if varType in p.structs.keys():
                fields = p.structs[varType]
            elif varType in p.messages.keys():
                fields = p.messages[varType]
            output: list[str] = []
            for vn, vt in fields:
                output += self.serializer(p, vt, vn, this)
            return output
        elif varType == "string":
            return ["writeString(data, %s%s%s)" % (ptr, pref, varName)]
        elif varType[0] == "[" and varType[-1] == "]":
            interior = varType[1:-1]
            out = [
                "%sLen := (uint32)(len(%s%s))" % (label, pref, varName),
                "binary.Write(data, binary.LittleEndian, %sLen)" % label,
                "for i := (uint32)(0); i < %sLen; i++ {" % label
            ]
            out += [
                self.tab + deser for deser in self.serializer(p, interior, "%s[i]" % (varName), parent)
            ]
            out += ["}"]
            return out
        else:
            raise NotImplementedError("Type %s not serializable yet." % varType)


    def gen_struct(self, p: Protocol, s: tuple[str, list[tuple[str,str]]]):
        self.wl()
        self.wl("type %s struct {" % s[0])
        self.ind += 1

        for varData in s[1]:
            varName, varType = varData
            if varType[0] == "[" and varType[-1] == "]":
                self.wl("%s []%s" % (varName, self.var(varType[1:-1])))
            else:
                self.wl("%s %s" % (varName, self.var(varType)))
        self.ind -= 1
        self.wl("}")
        self.wl()

        self.wl("func Read%s (data io.Reader, input *%s) {" % (s[0], s[0]) )
        self.ind += 1
        [self.wl(s) for s in self.deserializer(p, s[0], "input")]
        self.ind -= 1
        self.wl("}")
        self.wl()

        self.wl("func (output %s) Write (data io.Writer) {" % (s[0]))
        self.ind += 1
        [self.wl(s) for s in self.serializer(p, s[0], "output")]
        self.ind -= 1
        self.wl("}")
        self.wl()



    def gen_message(self, p: Protocol, m: tuple[str, list[tuple[str,str]]]):
        self.gen_struct(p, m)

        self.wl("func (output %s) GetType() MessageType {" % (m[0]))
        self.ind += 1
        self.wl("return %sType" % m[0])
        self.ind -= 1
        self.wl("}")
        self.wl()


    def generate(self, p: Protocol) -> str:
        self.output = ""

        def publicize(s: str):
            return s[:1].upper() + s[1:]

        p2 = copy.deepcopy(p)
        nstructs = OrderedDict()
        for s in p2.structs:
            k = publicize(s)
            v = []
            for vdata in p2.structs[s]:
                v.append( (publicize(vdata[0]), vdata[1]) )
            nstructs[k] = v
        p2.structs = nstructs

        nmessages = OrderedDict()
        for m in p2.messages:
            k = publicize(m)
            v = []
            for vdata in p2.messages[m]:
                v.append( (publicize(vdata[0]), vdata[1]) )
            nmessages[k] = v
        p2.messages = nmessages

        self.wl(f"// This file was automatically generated by {LIB_NAME} v{LIB_VERSION}.")
        self.wl(f"// Do not edit directly.")
        self.wl()
        if p2.namespace:
            self.wl("package %s" % p2.namespace)
        else:
            self.wl("package main")
        self.wl()
        self.wl("import (")
        self.ind += 1
        self.wl("\"encoding/binary\"")
        self.wl("\"io\"")
        self.ind -= 1
        self.wl(")")
        self.wl()

        self.wl("type MessageType byte")
        self.wl("const (")
        self.ind += 1
        self.dw("\n".join([self.ws("%sType MessageType = %d" % (k, i)) for i, k in enumerate(p2.messages.keys())]))
        self.dw("\n")
        self.ind -= 1
        self.wl(")")
        self.wl()

        self.wl("type Message interface {")
        self.ind += 1
        self.wl("Write(data io.Writer)")
        self.wl("GetType() MessageType")
        self.ind -= 1
        self.wl("}")
        self.wl()

        self.wl("func readString(data io.Reader, str *string) {")
        self.ind += 1
        self.wl("var len uint32")
        self.wl("binary.Read(data, binary.LittleEndian, &len)")
        self.wl("sbytes := make([]byte, len)")
        self.wl("binary.Read(data, binary.LittleEndian, &sbytes)")
        self.wl("*str = string(sbytes)")
        self.ind -= 1
        self.wl("}")
        self.wl()

        self.wl("func writeString(data io.Writer, str *string) {")
        self.ind += 1
        self.wl("strLen := (uint32)(len(*str))")
        self.wl("binary.Write(data, binary.LittleEndian, strLen)")
        self.wl("io.WriteString(data, *str)")
        self.ind -= 1
        self.wl("}")
        self.wl()

        for s in p2.structs.items():
            self.gen_struct(p2, s)

        for m in p2.messages.items():
            self.gen_message(p2, m)

        self.wl()
        assert self.ind == 0

        return self.output
