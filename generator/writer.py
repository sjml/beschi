from collections import defaultdict

from .protocol import Protocol

DEFAULT_TAB = " " * 4


class Writer:
    def __init__(self, protocol: Protocol, tab: str = DEFAULT_TAB):
        self.ind: int = 0
        self.output: str = ""

        self.protocol = protocol
        self.tab: str = tab

        self.type_mapping: dict[str, str] = {}
        for coll_type in self.protocol.complexTypes:
            self.type_mapping[coll_type] = coll_type
        for struct_type in self.protocol.structs:
            self.type_mapping[struct_type] = struct_type
        for msg_type in self.protocol.messages:
            self.type_mapping[msg_type] = msg_type

    # direct write (just put text right in output)
    def dw(self, text: str):
        self.output += text

    # write (put text in output, indented to current level)
    def w(self, text: str):
        self.output += (self.tab * self.ind) + text

    # write line (write, then newline)
    def wl(self, text: str = ""):
        self.output += (self.tab * self.ind) + text + "\n"

    # write string? (return text with current indentation level)
    def ws(self, text: str) -> str:
        return (self.tab * self.ind) + text

    # write line string (write string + a newline)
    def wls(self, text: str) -> str:
        return (self.tab * self.ind) + text + "\n"

    def var(self, var_type: str) -> str:
        if var_type not in self.type_mapping:
            raise NotImplementedError("No type called %s implemented for <%s>." % (var_type, type(self)))
        return self.type_mapping[var_type]
