import string
from collections import OrderedDict

import toml

BASE_TYPE_SIZES: dict[str, int] = {
    "byte":   1,
    "bool":   1,
    "uint16": 2,
    "int16":  2,
    "uint32": 4,
    "int32":  4,
    "uint64": 8,
    "int64":  8,
    "float":  4,
    "double": 8,
}

COLLECTION_TYPES: list[str] = [
    "list",
    "string",
]

def _contains_whitespace(s: str) -> bool:
    return True in [c in s for c in string.whitespace]

class Protocol():
    def __init__(self, filename: str):
        self.namespace: str = None
        self.structs: OrderedDict = OrderedDict()
        self.messages: OrderedDict = OrderedDict()

        protocol_data = toml.load(filename)

        if "meta" in protocol_data and "namespace" in protocol_data["meta"]:
            if _contains_whitespace(protocol_data["meta"]["namespace"]):
                raise ValueError(f"Namespace cannot contain whitespace: '{protocol_data['meta']['namespace']}'")
            self.namespace = protocol_data["meta"]["namespace"]

        if "structs" in protocol_data:
            for struct_data in protocol_data["structs"]:
                if "_name" not in struct_data:
                    raise ValueError(f"Missing _name on {struct_data}")
                if struct_data["_name"] in self.structs:
                    raise ValueError(f"Duplicate _name on {struct_data}")
                if _contains_whitespace(struct_data["_name"]):
                    raise ValueError(f"Struct _name cannot contain whitespace: '{struct_data['_name']}'")
                if struct_data['_name'] in BASE_TYPE_SIZES.keys() or struct_data['_name'] in COLLECTION_TYPES:
                    raise ValueError(f"Struct _name is reserved word: '{struct_data['_name']}'")
                self.structs[struct_data["_name"]] = []
            for struct in protocol_data["structs"]:
                struct_name = struct["_name"]
                for var_name, var_type in struct.items():
                    if (var_name[0] == "_"):
                        continue
                    if _contains_whitespace(var_name):
                        raise ValueError(f"Member name cannot contain whitespace: '{var_name}'")
                    if not self.verify_type_name(var_type):
                        raise NotImplementedError(f"No type called {var_type} (definition: {struct_name})")
                    self.structs[struct_name].append((var_name, var_type))

        if "messages" in protocol_data:
            for message_data in protocol_data["messages"]:
                if "_name" not in message_data:
                    raise ValueError(f"Missing _name on {message_data}")
                if message_data["_name"] in self.messages:
                    raise ValueError(f"Duplicate _name on {message_data}")
                if _contains_whitespace(message_data["_name"]):
                    raise ValueError(f"Message _name cannot contain whitespace: '{message_data['_name']}'")
                if message_data['_name'] in BASE_TYPE_SIZES.keys() or message_data['_name'] in COLLECTION_TYPES:
                    raise ValueError(f"Message _name is reserved word: '{message_data['_name']}'")
                if message_data['_name'] in self.structs.keys():
                    raise ValueError(f"Message name cannot shadow struct: '{message_data['_name']}'")
                self.messages[message_data["_name"]] = []
            for message in protocol_data["messages"]:
                message_name = message["_name"]
                for var_name, var_type in message.items():
                    if (var_name[0] == "_"):
                        continue
                    if _contains_whitespace(var_name):
                        raise ValueError(f"Member name cannot contain whitespace: '{var_name}'")
                    if not self.verify_type_name(var_type):
                        raise NotImplementedError(f"No type called {var_type} (message: {message_name})")
                    self.messages[message_name].append((var_name, var_type))

            if len(protocol_data["messages"]) > 255:
                raise ValueError("Cannot, at present, have more than 255 types of messages. Sorry. :(")

    def __str__(self) -> str:
        return f"Protocol (namespace: {self.namespace}, {len(self.structs)} structs, {len(self.messages)} messages)"


    def verify_type_name(self, type_name) -> bool:
        if type_name[0] == "[" and type_name[-1] == "]":
            type_name = type_name[1:-1]

        if type_name in BASE_TYPE_SIZES:
            return True
        if type_name in COLLECTION_TYPES:
            return True
        if type_name in self.structs:
            return True
        return False

    def is_simple(self, var_type: str) -> bool:
        if var_type in BASE_TYPE_SIZES:
            return True
        elif var_type in COLLECTION_TYPES:
            return False
        elif var_type[0] == "[" and var_type[-1] == "]":
            return False
        elif var_type in self.structs or var_type in self.messages:
            datums: list[tuple[str,str]] = None
            if var_type in self.structs:
                datums = self.structs[var_type]
            else:
                datums = self.messages[var_type]
            for _, vt in datums:
                if not self.is_simple(vt):
                    return False
            return True
        else:
            raise NotImplementedError(f"Can't determine simplicity of {var_type}.")

    def calculate_size(self, var_type: str) -> int:
        if self.is_simple(var_type):
            if var_type in BASE_TYPE_SIZES:
                return BASE_TYPE_SIZES[var_type]
            else:
                size = 0
                if var_type in self.structs:
                    datums = self.structs[var_type]
                else:
                    datums = self.messages[var_type]
                for _, vt in datums:
                    size += self.calculate_size(vt)
                return size
        else:
            return -1
