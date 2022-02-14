from collections import OrderedDict

import toml

BASE_TYPES: dict[str, int] = {
    "byte":   1,
    "bool":   1,
    "uint16": 2,
    "int16":  2,
    "uint32": 4,
    "int32":  4,
    "float":  4,
    "double": 8,
}

COLLECTION_TYPES: list[str] = [
    "list",
    "str",
]

class Protocol():
    def __init__(self, filename: str):
        self.namespace: str = None
        self.baseTypes: OrderedDict = OrderedDict()
        self.complexTypes: list[str] = []
        self.structs: OrderedDict = OrderedDict()
        self.messages: OrderedDict = OrderedDict()

        protocolData = toml.load(filename)

        if "namespace" in protocolData["meta"]:
            self.namespace = protocolData["meta"]["namespace"]

        for typeName, typeSize in protocolData["baseTypes"].items():
            self.baseTypes[typeName] = typeSize

        self.complexTypes = protocolData["complexTypes"]["typeList"]

        for sData in protocolData["structs"]:
            self.structs[sData["_name"]] = []
        for struct in protocolData["structs"]:
            structName = struct["_name"]
            for varName, varType in struct.items():
                if (varName[0] == "_"):
                    continue
                if not self.verifyTypeName(varType):
                    raise NotImplementedError("No type called %s (definition: %s)" % (varType, structName))
                self.structs[structName].append((varName, varType))

        for mData in protocolData["messages"]:
            self.messages[mData["_name"]] = []
        for message in protocolData["messages"]:
            messageName = message["_name"]
            for varName, varType in message.items():
                if (varName[0] == "_"):
                    continue
                if not self.verifyTypeName(varType):
                    raise NotImplementedError("No type called %s (message: %s)" % (varType, messageName))
                self.messages[messageName].append((varName, varType))

    def __str__(self) -> str:
        return f"Protocol (namespace: {self.namespace}, {len(self.baseTypes)} base, {len(self.complexTypes)} complex, {len(self.structs)} structs, {len(self.messages)} messages)"

    def verifyTypeName(self, typeName) -> bool:
        if typeName[0] == "[" and typeName[-1] == "]":
            typeName = typeName[1:-1]

        if typeName in self.baseTypes.keys():
            return True
        if typeName in self.structs.keys():
            return True
        if typeName in self.complexTypes:
            return True
        return False
