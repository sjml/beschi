import sys

from ..protocol import Protocol
from ..writer import Writer
from .. import LIB_NAME, LIB_VERSION


class PythonWriter(Writer):
    def __init__(self):
        super().__init__(tab="    ")

    def var(self, p: Protocol, varType: str):
        if varType in p.baseTypes.keys():
            if varType == "byte":
                return "int"
            elif varType == "bool":
                return "bool"
            elif varType == "uint16":
                return "int"
            elif varType == "int16":
                return "int"
            elif varType == "uint32":
                return "int"
            elif varType == "int32":
                return "int"
            elif varType == "float":
                return "float"
            elif varType == "double":
                return "float"
        elif varType in p.complexTypes or varType in p.structs.keys():
            if varType == "string":
                return "str"
            return varType
        elif varType in p.messages.keys():
            return varType
        raise NotImplementedError("No type called %s." % varType)


    def dw(self, text: str):
        self.output += text

    def w(self, text: str):
        self.output += (self.tab * self.ind) + text

    def wl(self, text: str = ""):
        self.output += (self.tab * self.ind) + text + "\n"

    def ws(self, text: str) -> str:
        return (self.tab * self.ind) + text

    def wls(self, text: str) -> str:
        return (self.tab * self.ind) + text + "\n"
