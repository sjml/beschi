from __future__ import annotations
import string
from collections import Counter

import tomllib

NUMERIC_TYPE_SIZES: dict[str, int] = {
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

NUMERIC_TYPE_RANGES: dict[str, tuple[int,int]] = {
    "byte":   (                         0,                        255),
    "int16":  (                   -32_768,                     32_767),
    "uint16": (                         0,                     65_535),
    "int32":  (            -2_147_483_648,              2_147_483_647),
    "uint32": (                         0,              4_294_967_295),
    "int64":  (-9_223_372_036_854_775_808,  9_223_372_036_854_775_807),
    "uint64": (                         0, 18_446_744_073_709_551_615),
}


RESERVED_WORDS: list[str] = list(NUMERIC_TYPE_SIZES.keys()) + ["string", "list"]

def _contains_whitespace(s: str) -> bool:
    return True in [c in s for c in string.whitespace]

class Variable():
    def __init__(self, protocol: Protocol, name: str, vartype: str, is_list: bool = False):
        self.protocol = protocol
        self.name = name
        self.vartype = vartype
        self.is_list = is_list

    def __str__(self) -> str:
        return f"Variable: <{self.name} ({'list of ' if self.is_list else ''}{self.vartype})>"

    def __repr__(self) -> str:
        return self.__str__()

    def is_simple(self, listed: bool = False) -> bool:
        if self.is_list and not listed:
            return False
        elif self.vartype in NUMERIC_TYPE_SIZES:
            return True
        elif self.vartype == "string":
            return False
        elif self.vartype in self.protocol.enums:
            return True
        elif self.vartype in self.protocol.structs:
            return self.protocol.structs[self.vartype].is_simple()
        elif self.vartype in self.protocol.messages:
            return self.protocol.messages[self.vartype].is_simple()
        else:
            raise NotImplementedError(f"Can't determine simplicity of {self.name}.")

class Enum():
    def __init__(self, name: str, value_spec: list[str | dict[str, int|str] ]):
        self.name = name
        self.values: dict[str,int] = dict()

        if all(isinstance(entry, str) for entry in value_spec):
            duplicate_entries = [v for v, count in Counter(value_spec).items() if count > 1]
            if len(duplicate_entries) > 0:
                raise ValueError(f"Duplicate values in enum {name}: {', '.join(duplicate_entries)}")
            self.values = dict((entry, idx) for idx, entry in enumerate(value_spec))
        elif not all(isinstance(entry, dict) for entry in value_spec):
            raise TypeError(f"Values list for enum {name} is neither all strings nor all tables")
        else:
            od: dict[str,int] = dict()
            for entry in value_spec:
                if "_name" not in entry:
                    raise TypeError("Missing _name in enum entry")
                if not type(entry["_name"]) is str:
                    raise TypeError(f"Enum entry _name is not a string: {entry['_name']}")
                if "_value" not in entry:
                    raise TypeError("Missing _value in enum entry")
                if not type(entry["_value"]) is int:
                    raise TypeError(f"Enum entry _value is not an integer: {entry['_value']}")
                od[entry["_name"]] = entry["_value"]
            self.values = od

        min_value = min(self.values.values())
        max_value = max(self.values.values())

        possible_options = ["byte", "int16", "int32"]
        for opt in possible_options:
            if min_value >= NUMERIC_TYPE_RANGES[opt][0] and max_value <= NUMERIC_TYPE_RANGES[opt][1]:
                self.encoding = opt
                break
        else:
            raise ValueError(f"Cannot encode enum; does not fit in one of {', '.join(possible_options)}")

    def get_default_pair(self) -> tuple[str,int]:
        return next(iter(self.values.items()))

    def get_minimum_pair(self) -> tuple[str,int]:
        k = min(self.values, key=self.values.get)
        return (k, self.values[k])

class Struct():
    def __init__(self, name: str):
        self.name = name
        self.members: list[Variable] = []
        self.is_message: bool = False

    def is_simple(self) -> bool:
        return all([var.is_simple() for var in self.members])

class Protocol():
    def __init__(self, filename: str = None):
        self.namespace: str = None
        self.list_size_type: str = "uint32"
        self.string_size_type: str = "uint32"
        self.structs: dict[str,Struct] = {}
        self.messages: dict[str,Struct] = {}
        self.enums: dict[str,Enum] = {}

        if filename == None:
            return

        self.protocol_string = open(filename, "r", encoding="utf-8").read()
        protocol_data = tomllib.loads(self.protocol_string)

        if "meta" in protocol_data:
            if "namespace" in protocol_data["meta"]:
                if _contains_whitespace(protocol_data["meta"]["namespace"]):
                    raise ValueError(f"Namespace cannot contain whitespace: '{protocol_data['meta']['namespace']}'")
                self.namespace = protocol_data["meta"]["namespace"]
            valid_sizes = ["byte", "uint16", "int16", "uint32", "int32", "uint64", "int64"]
            if "list_size_type" in protocol_data["meta"]:
                if protocol_data["meta"]["list_size_type"] not in valid_sizes:
                    raise ValueError(f"List size type is not valid: '{protocol_data['meta']['list_size_type']}'")
                self.list_size_type = protocol_data["meta"]["list_size_type"]
            if "string_size_type" in protocol_data["meta"]:
                if protocol_data["meta"]["string_size_type"] not in valid_sizes:
                    raise ValueError(f"String size type is not valid: '{protocol_data['meta']['string_size_type']}'")
                self.string_size_type = protocol_data["meta"]["string_size_type"]

        if "structs" not in protocol_data: protocol_data["structs"] = []
        if "messages" not in protocol_data: protocol_data["messages"] = []
        if "enums" not in protocol_data: protocol_data["enums"] = []

        def build_struct(data: dict[str,any], is_message: bool = False):
            if "_name" not in data:
                raise ValueError(f"Missing _name on {data}")
            s = Struct(data["_name"])
            s.is_message = is_message
            for var_name, var_type in data.items():
                if var_name.startswith("_"): continue
                if var_type[0] == "[" and var_type[-1] == "]":
                    listed_type = var_type[1:-1]
                    if listed_type[0] == "[" and listed_type[-1] == "]":
                        raise ValueError(f"Cannot have list of lists")
                    var = Variable(self, var_name, listed_type, True)
                else:
                    var = Variable(self, var_name, var_type, False)
                s.members.append(var)
            return s

        for struct_data in protocol_data["structs"]:
            s = build_struct(struct_data)
            if s.name in self.structs:
                raise ValueError(f"Duplicate _name on {struct_data}")
            self.structs[s.name] = s
        for message_data in protocol_data["messages"]:
            m = build_struct(message_data, True)
            if m.name in self.messages:
                raise ValueError(f"Duplicate _name on {message_data}")
            self.messages[m.name] = m
        for enum_data in protocol_data["enums"]:
            if "_name" not in enum_data:
                raise ValueError(f"Missing _name on {enum_data}")
            if "_values" not in enum_data:
                raise ValueError(f"Missing _values on {enum_data}")
            if not type(enum_data["_values"]) is list:
                raise ValueError(f"Values is not list on {enum_data}")
            e = Enum(enum_data["_name"], enum_data["_values"])
            self.enums[e.name] = e

        def validate_enum(e: Enum):
            if len(e.name) == 0:
                raise ValueError("Enum _name cannot be empty!")
            if _contains_whitespace(e.name):
                raise ValueError(f"Enum _name cannot contain whitespace: '{e.name}'")
            if e.name.lower() in RESERVED_WORDS:
                raise ValueError(f"Enum _name is reserved word: '{e.name}'")
            if len(e.values) == 0:
                raise ValueError(f"No values given for enum {e.name}.")
            duplicate_assignment = [v for v, count in Counter(e.values.values()).items() if count > 1]
            if len(duplicate_assignment) > 0:
                raise ValueError(f"Duplicate assignments in enum {e.name}: {', '.join([str(v) for v in duplicate_assignment])}")
            if e.name in self.structs:
                raise ValueError(f"Enum name cannot shadow struct: '{e.name}'")
            if e.name in self.messages:
                raise ValueError(f"Enum name cannot shadow message: '{e.name}'")
            for v in e.values.keys():
                if v in self.structs:
                    raise ValueError(f"Enum value name cannot shadow struct: '{e.name}.{v}'")
                if v in self.messages:
                    raise ValueError(f"Enum value name cannot shadow message: '{e.name}.{v}'")
                if _contains_whitespace(v):
                    raise ValueError(f"Enum value name cannot contain whitespace: '{e.name}.{v}'")

        def validate_struct(s: Struct):
            label = "Struct"
            if s.is_message:
                label = "Message"
            if len(s.name) == 0:
                raise ValueError(f"{label} _name cannot be empty!")
            if _contains_whitespace(s.name):
                raise ValueError(f"{label} _name cannot contain whitespace: '{s.name}'")
            if s.name.lower() in RESERVED_WORDS:
                raise ValueError(f"{label} _name is reserved word: '{s.name}'")
            if s.is_message and s.name in self.structs:
                raise ValueError(f"Message name cannot shadow struct: '{s.name}'")
            for var in s.members:
                if _contains_whitespace(var.name):
                    raise ValueError(f"Member name cannot contain whitespace: '{var.name}'")
                valid_types: list[str] = list(self.structs) + list(self.enums) + list(NUMERIC_TYPE_SIZES.keys()) + ["string"]
                if var.vartype not in valid_types:
                    if s.is_message and var.vartype in self.messages:
                        raise ValueError(f"Messages cannot contain other messages ({s.name} contains {var.vartype})")
                    raise NotImplementedError(f"No type called {var.vartype} (definition: {s.name})")

        [validate_struct(s) for s in self.structs.values()]
        [validate_struct(m) for m in self.messages.values()]
        [  validate_enum(e) for e in self.enums.values()]

        if len(self.messages) > 255:
            raise ValueError("Cannot, at present, have more than 255 types of messages. Sorry. :(")

        def check_for_cycles(s: Struct):
            encountered = set([s.name])
            frontier = [m.vartype for m in s.members if m.vartype in self.structs]
            while len(frontier) > 0:
                new_type = frontier.pop()
                if new_type in encountered:
                    raise RecursionError(f"{s.name} and {new_type} reference each other")
                for cvar in self.structs[new_type].members:
                    if cvar.vartype in encountered:
                        raise RecursionError(f"{s.name} and {cvar.vartype} reference each other")
                    if cvar.vartype not in self.structs: continue
                    frontier.append(cvar.vartype)

        [check_for_cycles(s) for s in self.structs.values()]
        [check_for_cycles(m) for m in self.messages.values()]

    def __str__(self) -> str:
        return f"Protocol (namespace: {self.namespace}, {len(self.structs)} structs, {len(self.messages)} messages)"

    def get_size_of(self, var_type: str) -> int:
        if var_type in NUMERIC_TYPE_SIZES:
            return NUMERIC_TYPE_SIZES[var_type]
        elif var_type in self.enums:
            return NUMERIC_TYPE_SIZES[self.enums[var_type].encoding]
        elif var_type == "string":
            raise NotImplementedError("Cannot pre-calculate size of string")
        else:
            size = 0
            if var_type in self.structs:
                st = self.structs[var_type]
            else:
                st = self.messages[var_type]
            for var in st.members:
                if var.is_list:
                    raise NotImplementedError(f"Cannot calculate size of struct with list ({var_type})")
                size += self.get_size_of(var.vartype)
            return size
