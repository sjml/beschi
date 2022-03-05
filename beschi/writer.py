import os
import re
import argparse

from .protocol import Protocol

DEFAULT_INDENT = "    "

class TextUtil:
    def convert_to_lower_snake_case(s: str) -> str:
        s = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', s)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s).lower()

    def capitalize(s: str) -> str:
        return s[:1].upper() + s[1:]

    def replace(s: str, subs: list[tuple[str,str]]) -> str:
        for sub in subs:
            s = s.replace(sub[0], sub[1])
        return s


class Writer:
    language_name = "[Base]"
    default_extension = ".beschi"
    in_progress = False # if set to True, writer will not be added to
                        #  the writers.all_writers object, so will be
                        #  shielded from the test suite

    def get_additional_args(parser: argparse.ArgumentParser):
        pass

    def __init__(self, protocol: Protocol, tab: str = DEFAULT_INDENT):
        self.indent_level: int = 0
        self.output: list[str] = []

        self.protocol = protocol
        self.tab: str = tab

        self.type_mapping: dict[str, str] = {}
        self.type_mapping["string"] = "string"
        for struct_type in self.protocol.structs:
            self.type_mapping[struct_type] = struct_type
        for msg_type in self.protocol.messages:
            self.type_mapping[msg_type] = msg_type

    # inserts any boilerplate code, indented at the current level
    def add_boilerplate(self, substitutions: list[tuple[str,str]] = [], index: int =-1):
        if index >= 0:
            index_str = f".{index}"
        else:
            index_str = ""
        filename = f"{self.language_name}{index_str}{self.default_extension}"
        boilerplate_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "writers", "boilerplate", filename)
        if os.path.exists(boilerplate_path):
            boilerplate_lines = open(boilerplate_path, "r").read().splitlines()
            for s in substitutions:
                boilerplate_lines = [bpl.replace(s[0], s[1]) for bpl in boilerplate_lines]
            [self.write_line(bpl) for bpl in boilerplate_lines]
        else:
            print("no file", filename)

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

    def get_native_list_size(self) -> str:
        return self.type_mapping[self.protocol.list_size_type]

    def get_native_string_size(self) -> str:
        return self.type_mapping[self.protocol.string_size_type]
