import argparse

from ..protocol import Protocol, Variable, Struct, NUMERIC_TYPE_SIZES
from ..writer import Writer, TextUtil
from .typescript import TypeScriptWriter
from .. import LIB_NAME, LIB_VERSION

LANGUAGE_NAME = "AssemblyScript"


class AssemblyScriptWriter(TypeScriptWriter):
    language_name = LANGUAGE_NAME
    default_extension = ".ts"

    def __init__(self, p: Protocol, extra_args: dict[str,any] = {}):
        Writer.__init__(self, p, tab="  ") # skip over TypeScriptWriter init

        self.embed_protocol = extra_args["embed_protocol"]
        self.use_namespace = False

        self.type_mapping["byte"] = "u8"
        self.type_mapping["bool"] = "bool"
        self.type_mapping["uint16"] = "u16"
        self.type_mapping["int16"] = "i16"
        self.type_mapping["uint32"] = "u32"
        self.type_mapping["int32"] = "i32"
        self.type_mapping["uint64"] = "u64"
        self.type_mapping["int64"] = "i64"
        self.type_mapping["float"] = "f32"
        self.type_mapping["double"] = "f64"
        self.type_mapping["string"] = "string"

        self.base_serializers: dict[str,str] = {
            "byte": "Byte",
            "bool": "Bool",
            "uint16": "Uint16",
            "int16": "Int16",
            "uint32": "Uint32",
            "int32": "Int32",
            "uint64": "Uint64",
            "int64": "Int64",
            "float": "Float32",
            "double": "Float64",
        }

        self.is_assembly_script = True
