from collections import defaultdict

from .protocol import Protocol, COLLECTION_TYPES

DEFAULT_INDENT = "    "


class Writer:
    language_name = "[Base]"
    default_extension = ".beschi"

    def __init__(self, protocol: Protocol, tab: str = DEFAULT_INDENT):
        self.indent_level: int = 0
        self.output: list[str] = []

        self.protocol = protocol
        self.tab: str = tab

        self.type_mapping: dict[str, str] = {}
        for coll_type in COLLECTION_TYPES:
            self.type_mapping[coll_type] = coll_type
        for struct_type in self.protocol.structs:
            self.type_mapping[struct_type] = struct_type
        for msg_type in self.protocol.messages:
            self.type_mapping[msg_type] = msg_type

    # write line with current indentation level
    def write_line(self, text: str = ""):
        if len(text) == 0:
            self.output.append("")
        else:
            self.output.append(self.indent_string(text))

    # return text with current indentation level
    def indent_string(self, text: str) -> str:
        return (self.tab * self.indent_level) + text

    def get_var(self, var_type: str) -> str:
        if var_type not in self.type_mapping:
            raise NotImplementedError(f"No type called {var_type} implemented for <{type(self)}>.")
        return self.type_mapping[var_type]
