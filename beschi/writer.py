import os

from .protocol import Protocol, COLLECTION_TYPES

DEFAULT_INDENT = "    "


class Writer:
    language_name = "[Base]"
    default_extension = ".beschi"
    in_progress = False # if set to True, writer will not be added to
                        #  the writers.all_writers object, so will be
                        #  shielded from the test suite

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

    # inserts any boilerplate code, indented at the current level
    def add_boilerplate(self):
        boilerplate_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "writers", "boilerplate", f"{self.language_name}{self.default_extension}")
        if os.path.exists(boilerplate_path):
            boilerplate_lines = open(boilerplate_path, "r").read().splitlines()
            [self.write_line(bpl) for bpl in boilerplate_lines]

    # actually generate the code
    def generate(self) -> str:
        raise NotImplementedError(f"ERROR: 'generate' function needs to be implemented on {self.__class__.__name__}")

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
