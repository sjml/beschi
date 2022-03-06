import re # two problems

from ..protocol import Protocol, Variable, Struct, NUMERIC_TYPE_SIZES
from ..writer import Writer, TextUtil
from .. import LIB_NAME, LIB_VERSION

LANGUAGE_NAME = "C"


class CWriter(Writer):
    language_name = LANGUAGE_NAME
    default_extension = ".h"

    def __init__(self, p: Protocol, extra_args: dict[str,any] = {}):
        super().__init__(protocol=p, tab="    ")

        self.embed_protocol = extra_args["embed_protocol"]

        self.type_mapping["byte"] = "uint8_t"
        self.type_mapping["bool"] = "bool"
        self.type_mapping["uint16"] = "uint16_t"
        self.type_mapping["int16"] = "int16_t"
        self.type_mapping["uint32"] = "uint32_t"
        self.type_mapping["int32"] = "int32_t"
        self.type_mapping["uint64"] = "uint64_t"
        self.type_mapping["int64"] = "int64_t"
        self.type_mapping["float"] = "float"
        self.type_mapping["double"] = "double"
        self.type_mapping["string"] = "char*"

        self.base_serializers: dict[str,str] = {
            "byte":   "UInt8",
            "bool":   "Bool",
            "uint16": "UInt16",
            "int16":  "Int16",
            "uint32": "UInt32",
            "int32":  "Int32",
            "uint64": "UInt64",
            "int64":  "Int64",
            "float":  "Float",
            "double": "Double",
        }

        self.base_defaults: dict[str,str] = {
            "byte":   "0",
            "bool":   "false",
            "uint16": "0",
            "int16":  "0",
            "uint32": "0",
            "int32":  "0",
            "uint64": "0",
            "int64":  "0",
            "float":  "0.0f",
            "double": "0.0",
        }

        self.subs: list[tuple[str,str]] = []
        self.prefix = "beschi_"
        if self.protocol.namespace != None:
            self.subs = [("beschi", self.protocol.namespace), ("BESCHI", self.protocol.namespace.upper())]
            self.prefix = f"{self.protocol.namespace}_"

    def err_check_return(self):
        self.write_line(f"if (err != {self.prefix.upper()}ERR_OK) {{")
        self.indent_level += 1
        self.write_line("return err;")
        self.indent_level -= 1
        self.write_line("}")

    def deserializer(self, var: Variable, accessor: str):
        if var.is_list:
            self.write_line(f"err = {self.prefix}_Read{self.base_serializers[self.protocol.list_size_type]}(r, &({accessor}{var.name}_len));")
            self.err_check_return()
            if var.vartype in NUMERIC_TYPE_SIZES or var.vartype == "string":
                pref = ""
            else:
                pref = self.prefix
            self.write_line(f"{accessor}{var.name} = ({pref}{self.type_mapping[var.vartype]}*)malloc(sizeof({pref}{self.type_mapping[var.vartype]}) * {accessor}{var.name}_len);")
            self.write_line(f"if ({accessor}{var.name} == NULL) {{ return {self.prefix.upper()}ERR_ALLOCATION_FAILURE; }}")
            if var.vartype == "string":
                self.write_line(f"{accessor}{var.name}_els_len = ({self.get_native_string_size()}*)malloc(sizeof({self.get_native_string_size()}) * {accessor}{var.name}_len);")
                self.write_line(f"if ({accessor}{var.name} == NULL) {{ return {self.prefix.upper()}ERR_ALLOCATION_FAILURE; }}")
            idx = self.indent_level
            self.write_line(f"for ({self.get_native_list_size()} i{idx} = 0; i{idx} < {accessor}{var.name}_len; i{idx}++) {{")
            self.indent_level += 1
            inner = Variable(self.protocol, f"{var.name}[i{idx}]", var.vartype)
            self.deserializer(inner, accessor)
            self.indent_level -= 1
            self.write_line("}")
        elif var.vartype == "string":
            idx_search = re.match(r"(.*)\[(i\d+)\]$", var.name)
            if idx_search != None:
                name = idx_search.group(1)
                idx = idx_search.group(2)
                self.write_line(f"err = {self.prefix}_ReadString(r, &({accessor}{var.name}), &({accessor}{name}_els_len[{idx}]));")
            else:
                self.write_line(f"err = {self.prefix}_ReadString(r, &({accessor}{var.name}), &({accessor}{var.name}_len));")
        elif var.vartype in NUMERIC_TYPE_SIZES:
            self.write_line(f"err = {self.prefix}_Read{self.base_serializers[var.vartype]}(r, &({accessor}{var.name}));")
        else:
            self.write_line(f"err = {self.prefix}{var.vartype}_FromBytes(r, &({accessor}{var.name}));")
        self.err_check_return()

    def serializer(self, var: Variable, accessor: str):
        if var.is_list:
            self.write_line(f"err = {self.prefix}_Write{self.base_serializers[self.protocol.list_size_type]}(w, &({accessor}{var.name}_len));")
            self.err_check_return()
            idx = self.indent_level
            self.write_line(f"for ({self.get_native_list_size()} i{idx} = 0; i{idx} < {accessor}{var.name}_len; i{idx}++) {{")
            self.indent_level += 1
            inner = Variable(self.protocol, f"{var.name}[i{idx}]", var.vartype)
            self.serializer(inner, accessor)
            self.indent_level -= 1
            self.write_line("}")
        elif var.vartype == "string":
            idx_search = re.match(r"(.*)\[(i\d+)\]$", var.name)
            if idx_search != None:
                name = idx_search.group(1)
                idx = idx_search.group(2)
                self.write_line(f"err = {self.prefix}_WriteString(w, &({accessor}{var.name}), &({accessor}{name}_els_len[{idx}]));")
            else:
                self.write_line(f"err = {self.prefix}_WriteString(w, &({accessor}{var.name}), &({accessor}{var.name}_len));")
        elif var.vartype in NUMERIC_TYPE_SIZES:
            self.write_line(f"err = {self.prefix}_Write{self.base_serializers[var.vartype]}(w, &({accessor}{var.name}));")
        else:
            self.write_line(f"err = {self.prefix}{var.vartype}_WriteBytes(w, &({accessor}{var.name}));")
        self.err_check_return()

    def gen_measurement(self, st: Struct, accessor: str = "") -> tuple[list[str], int]:
        lines: list[str] = []
        accum = 0

        if st.is_simple():
            lines.append(f"*size = {self.protocol.get_size_of(st.name)};")
        else:
            size_init = "*size = 0;"
            lines.append(size_init)

            for var in st.members:
                if var.is_list:
                    accum += NUMERIC_TYPE_SIZES[self.protocol.list_size_type]
                    idx = self.indent_level
                    if var.is_simple(True):
                        lines.append(f"*size += {accessor}{var.name}_len * {self.protocol.get_size_of(var.vartype)};")
                    elif var.vartype == "string":
                        lines.append(f"for ({self.get_native_list_size()} i{idx} = 0; i{idx} < {accessor}{var.name}_len; i{idx}++) {{")
                        lines.append(f"{self.tab}*size += {NUMERIC_TYPE_SIZES[self.protocol.string_size_type]} + {accessor}{var.name}_els_len[i{idx}];")
                        lines.append("}")
                    else:
                        lines.append(f"for ({self.get_native_list_size()} i{idx} = 0; i{idx} < {accessor}{var.name}_len; i{idx}++) {{")
                        self.indent_level += 1
                        clines, caccum = self.gen_measurement(self.protocol.structs[var.vartype], f"{accessor}{var.name}[i{idx}].")
                        self.indent_level -= 1
                        if clines[0] == size_init:
                            clines = clines[1:]
                        clines.append(f"*size += {caccum};")
                        lines += [f"{self.tab}{l}" for l in clines]
                        lines.append("}")
                else:
                    if var.is_simple():
                        accum += self.protocol.get_size_of(var.vartype)
                    elif var.vartype == "string":
                        accum += NUMERIC_TYPE_SIZES[self.protocol.string_size_type]
                        lines.append(f"*size += {accessor}{var.name}_len;")
                    else:
                        clines, caccum = self.gen_measurement(self.protocol.structs[var.vartype], f"{accessor}{var.name}.")
                        if clines[0] == size_init:
                            clines = clines[1:]
                        lines += clines
                        accum += caccum
        return lines, accum

    def gen_default(self, members: list[Variable]):
        for var in members:
            if var.is_list:
                self.write_line(f".{var.name}_len = 0,")
                if var.vartype == "string":
                    self.write_line(f".{var.name}_els_len = NULL,")
                self.write_line(f".{var.name} = NULL,")
            elif var.vartype in self.base_defaults:
                self.write_line(f".{var.name} = {self.base_defaults[var.vartype]},")
            elif var.vartype == "string":
                self.write_line(f".{var.name}_len = 0,")
                self.write_line(f".{var.name} = (char*)\"\",")
            else:
                self.write_line(f".{var.name} = {{")
                self.indent_level += 1
                self.gen_default(self.protocol.structs[var.vartype].members)
                self.indent_level -= 1
                self.write_line("},")

    def destructor(self, var: Variable, accessor: str):
        if var.is_simple():
            return
        if var.is_list:
            if var.is_simple(True):
                self.write_line(f"free({accessor}{var.name});")
            else:
                idx = self.indent_level
                self.write_line(f"for ({self.get_native_list_size()} i{idx} = 0; i{idx} < {accessor}{var.name}_len; i{idx}++) {{")
                self.indent_level += 1
                inner = Variable(self.protocol, f"{var.name}[i{idx}]", var.vartype)
                self.destructor(inner, accessor)
                self.indent_level -= 1
                self.write_line("}")
                if var.vartype == "string":
                    self.write_line(f"free({accessor}{var.name}_els_len);")
                self.write_line(f"free({accessor}{var.name});")
        elif var.vartype == "string":
            self.write_line(f"free({accessor}{var.name});")
        else:
            [self.destructor(mem, f"{accessor}{var.name}.") for mem in self.protocol.structs[var.vartype].members]

    def gen_struct(self, sname: str, sdata: Struct):
        self.write_line("typedef struct {")
        self.indent_level += 1
        if sdata.is_message:
            self.write_line(f"{self.prefix}MessageType _mt;")
        for var in sdata.members:
            if var.is_list:
                self.write_line(f"{self.get_native_list_size()} {var.name}_len;")
                if var.vartype == "string":
                    self.write_line(f"{self.get_native_list_size()}* {var.name}_els_len;")
                if var.vartype in NUMERIC_TYPE_SIZES or var.vartype == "string":
                    self.write_line(f"{self.type_mapping[var.vartype]}* {var.name};")
                elif var.vartype in self.protocol.structs:
                    self.write_line(f"{self.prefix}{var.vartype}* {var.name};")
            elif var.vartype == "string":
                self.write_line(f"{self.get_native_string_size()} {var.name}_len;")
                self.write_line(f"{self.type_mapping[var.vartype]} {var.name};")
            elif var.vartype in NUMERIC_TYPE_SIZES:
                self.write_line(f"{self.type_mapping[var.vartype]} {var.name};")
            elif var.vartype in self.protocol.structs:
                self.write_line(f"{self.prefix}{var.vartype} {var.name};")
        self.indent_level -= 1
        self.write_line(f"}} {self.prefix}{sname};")

        if sdata.is_message:
            self.write_line(f"extern const {self.prefix}{sname} {self.prefix}{sname}_default;")
            self.write_line(f"const {self.prefix}{sname} {self.prefix}{sname}_default = {{")
            self.indent_level += 1
            self.write_line(f"._mt = {self.prefix}MessageType_{sname},")
            self.gen_default(sdata.members)
            self.indent_level -= 1
            self.write_line("};")
        self.write_line()
        if sdata.is_message:
            self.write_line(f"{self.prefix}err_t {self.prefix}{sname}_WriteBytes({self.prefix}DataAccess* w, const {self.prefix}{sname}* src, bool tag);")
        else:
            self.write_line(f"{self.prefix}err_t {self.prefix}{sname}_WriteBytes({self.prefix}DataAccess* w, const {self.prefix}{sname}* src);")
        self.write_line(f"{self.prefix}err_t {self.prefix}{sname}_FromBytes({self.prefix}DataAccess* r, {self.prefix}{sname}* dst);")
        if sdata.is_message:
            self.write_line(f"{self.prefix}err_t {self.prefix}{sname}_GetSizeInBytes(const {self.prefix}{sname}* m, size_t* size);")
            self.write_line(f"void {self.prefix}{sname}_Destroy({self.prefix}{sname} *m);")
        self.write_line()
        self.write_line()

    def gen_implementation(self, sname: str, sdata: Struct):
        if sdata.is_message:
            self.write_line(f"{self.prefix}err_t {self.prefix}{sname}_GetSizeInBytes(const {self.prefix}{sname}* m, size_t* size) {{")
            self.indent_level += 1
            measure_lines, accumulator = self.gen_measurement(sdata, "m->")
            [self.write_line(s) for s in measure_lines]
            if accumulator > 0:
                self.write_line(f"*size += {accumulator};")
            self.write_line(f"return {self.prefix.upper()}ERR_OK;")
            self.indent_level -= 1
            self.write_line("}")
            self.write_line()

            self.write_line(f"void {self.prefix}{sname}_Destroy({self.prefix}{sname} *m) {{")
            self.indent_level += 1
            [self.destructor(mem, f"m->") for mem in sdata.members]
            self.write_line("free(m);")
            self.indent_level -= 1
            self.write_line("}")
            self.write_line()

        self.write_line(f"{self.prefix}err_t {self.prefix}{sname}_FromBytes({self.prefix}DataAccess* r, {self.prefix}{sname}* dst) {{")
        self.indent_level += 1
        if sdata.is_message:
            self.write_line(f"dst->_mt = {self.prefix}MessageType_{sname};")
        if len(sdata.members) > 0:
            self.write_line(f"{self.prefix}err_t err;")
        [self.deserializer(mem, "dst->") for mem in sdata.members]
        self.write_line(f"return {self.prefix.upper()}ERR_OK;")
        self.indent_level -= 1
        self.write_line("}")
        self.write_line()

        if sdata.is_message:
            self.write_line(f"{self.prefix}err_t {self.prefix}{sname}_WriteBytes({self.prefix}DataAccess* w, const {self.prefix}{sname}* src, bool tag) {{")
        else:
            self.write_line(f"{self.prefix}err_t {self.prefix}{sname}_WriteBytes({self.prefix}DataAccess* w, const {self.prefix}{sname}* src) {{")
        self.indent_level += 1
        self.write_line(f"{self.prefix}err_t err;")
        if sdata.is_message:
            self.write_line("if (tag) {")
            self.indent_level += 1
            self.write_line(f"err = {self.prefix}_WriteUInt8(w, (const uint8_t *)&(src->_mt));")
            self.err_check_return()
            self.indent_level -= 1
            self.write_line("}")
        [self.serializer(mem, "src->") for mem in sdata.members]
        self.write_line(f"return {self.prefix.upper()}ERR_OK;")
        self.indent_level -= 1
        self.write_line("}")
        self.write_line()

    def generate(self) -> str:
        self.output = []
        self.write_line(f"// This file was automatically generated by {LIB_NAME} v{LIB_VERSION}")
        self.write_line( "// <https://github.com/sjml/beschi>")
        self.write_line(f"// Do not edit directly.")
        self.write_line()

        if self.embed_protocol:
            self.write_line("/*")
            self.write_line("DATA PROTOCOL")
            self.write_line("-----------------")
            [self.write_line(f"{l}") for l in self.protocol.protocol_string.splitlines()]
            self.write_line("-----------------")
            self.write_line("END DATA PROTOCOL")
            self.write_line("*/")
            self.write_line()
            self.write_line()

        self.add_boilerplate(self.subs + [
            ("{# STRING_SIZE_TYPE #}", self.base_serializers[self.protocol.string_size_type]),
            ("{# STRING_SIZE_TYPE_LOWER #}", self.base_serializers[self.protocol.string_size_type].lower()),
            ("{# STRING_SIZE_TYPE_NATIVE #}", self.get_native_string_size()),
        ], 0)

        self.write_line("typedef enum {")
        self.indent_level += 1
        self.write_line(f"{self.prefix}MessageType___NullMessage = 0,")
        [self.write_line(f"{self.prefix}MessageType_{k} = {i+1}{',' if i < len(self.protocol.messages)-1 else ''}") for i, k in enumerate(self.protocol.messages.keys())]
        self.indent_level -= 1
        self.write_line(f"}} {self.prefix}MessageType;")
        self.write_line()
        self.write_line(f"{self.prefix}MessageType {self.prefix}GetMessageType(const void* m);")
        self.write_line(f"{self.prefix}err_t {self.prefix}GetSizeInBytes(const void* m, size_t* len);")
        self.write_line(f"{self.prefix}err_t {self.prefix}ProcessRawBytes({self.prefix}DataAccess* r, void*** msgListOut, size_t* len);")
        self.write_line(f"{self.prefix}err_t {self.prefix}DestroyMessageList(void** msgList, size_t len);")
        self.write_line()

        for sname, sdata in self.protocol.structs.items():
            self.gen_struct(sname, sdata)

        for mname, mdata in self.protocol.messages.items():
            self.gen_struct(mname, mdata)

        self.add_boilerplate(self.subs + [
            ("{# STRING_SIZE_TYPE #}", self.base_serializers[self.protocol.string_size_type]),
            ("{# STRING_SIZE_TYPE_LOWER #}", self.base_serializers[self.protocol.string_size_type].lower()),
        ], 1)

        self.write_line(f"{self.prefix}MessageType {self.prefix}GetMessageType(const void* m) {{")
        self.indent_level += 1
        self.write_line("const uint8_t* buffer = (const uint8_t*)m;")
        self.write_line("uint8_t msgType = buffer[0];")
        self.write_line(f"if (msgType > {len(self.protocol.messages)}) {{")
        self.indent_level += 1
        self.write_line(f"return {self.prefix}MessageType___NullMessage;")
        self.indent_level -= 1
        self.write_line("}")
        self.write_line(f"return ({self.prefix}MessageType)msgType;")
        self.indent_level -= 1
        self.write_line("}")
        self.write_line()

        self.write_line(f"{self.prefix}err_t {self.prefix}GetSizeInBytes(const void* m, size_t* len) {{")
        self.indent_level += 1
        self.write_line(f"{self.prefix}MessageType msgType = {self.prefix}GetMessageType(m);")
        self.write_line("switch (msgType) {")
        self.write_line(f"case {self.prefix}MessageType___NullMessage:")
        self.indent_level += 1
        self.write_line(f"return {self.prefix.upper()}ERR_INVALID_DATA;")
        self.write_line("break;")
        self.indent_level -= 1
        for msg_type in self.protocol.messages:
            self.write_line(f"case {self.prefix}MessageType_{msg_type}:")
            self.indent_level += 1
            self.write_line(f"return {self.prefix}{msg_type}_GetSizeInBytes((const {self.prefix}{msg_type}*)m, len);")
            self.write_line("break;")
            self.indent_level -= 1
        self.write_line("}")
        self.write_line(f"return {self.prefix.upper()}ERR_INVALID_DATA;")
        self.indent_level -= 1
        self.write_line("}")
        self.write_line()

        self.write_line(f"{self.prefix}err_t {self.prefix}ProcessRawBytes({self.prefix}DataAccess* r, void*** msgListDst, size_t* len) {{")
        self.indent_level += 1
        self.write_line(f"{self.prefix}err_t err = {self.prefix.upper()}ERR_OK;")
        self.write_line("size_t currCapacity = 8;")
        self.write_line("*msgListDst = (void**)malloc(sizeof(void*) * currCapacity);")
        self.write_line(f"if (*msgListDst == NULL) {{ return {self.prefix.upper()}ERR_ALLOCATION_FAILURE; }}")
        self.write_line("*len = 0;")
        self.write_line(f"while (!{self.prefix}IsFinished(r)) {{")
        self.indent_level += 1
        self.write_line("while (*len >= currCapacity) {")
        self.indent_level += 1
        self.write_line("currCapacity *= 2;")
        self.write_line("*msgListDst = (void**)realloc(*msgListDst, (sizeof(void*) * currCapacity));")
        self.write_line(f"if (*msgListDst == NULL) {{ return {self.prefix.upper()}ERR_ALLOCATION_FAILURE; }}")
        self.indent_level -= 1
        self.write_line("}")
        self.write_line("uint8_t msgType;")
        self.write_line(f"{self.prefix}_ReadUInt8(r, &msgType);")
        self.err_check_return()
        self.write_line()
        self.write_line("void* out;")
        self.write_line("switch (msgType) {")
        for msg_type in self.protocol.messages:
            self.write_line(f"case {self.prefix}MessageType_{msg_type}:")
            self.indent_level += 1
            self.write_line(f"out = malloc(sizeof({self.prefix}{msg_type}));")
            self.write_line(f"if (out == NULL) {{ return {self.prefix.upper()}ERR_ALLOCATION_FAILURE; }}")
            self.write_line(f"err = {self.prefix}{msg_type}_FromBytes(r, ({self.prefix}{msg_type}*)out);")
            self.write_line("(*msgListDst)[*len] = out;")
            self.write_line("*len += 1;")
            self.err_check_return()
            self.write_line("break;")
            self.indent_level -= 1
        self.write_line("default:")
        self.indent_level += 1
        self.write_line(f"return {self.prefix.upper()}ERR_INVALID_DATA;")
        self.write_line("break;")
        self.indent_level -= 1
        self.write_line("}")
        self.indent_level -= 1
        self.write_line("}")
        self.write_line(f"return {self.prefix.upper()}ERR_OK;")
        self.indent_level -= 1
        self.write_line("}")
        self.write_line()
        self.write_line(f"{self.prefix}err_t {self.prefix}DestroyMessageList(void** msgList, size_t len) {{")
        self.indent_level += 1
        self.write_line("for (size_t i = 0; i < len; i++) {")
        self.indent_level += 1
        self.write_line(f"{self.prefix}MessageType msgType = {self.prefix}GetMessageType(msgList[i]);")
        self.write_line("switch (msgType) {")
        for msg_type in self.protocol.messages:
            self.write_line(f"case {self.prefix}MessageType_{msg_type}:")
            self.indent_level += 1
            self.write_line(f"{self.prefix}{msg_type}_Destroy(({self.prefix}{msg_type}*)msgList[i]);")
            self.write_line("break;")
            self.indent_level -= 1
        self.write_line(f"case {self.prefix}MessageType___NullMessage:")
        self.indent_level += 1
        self.write_line(f"return {self.prefix.upper()}ERR_INVALID_DATA;")
        self.indent_level -= 1
        self.write_line("}")
        self.indent_level -= 1
        self.write_line("}")
        self.write_line("free(msgList);")
        self.write_line(f"return {self.prefix.upper()}ERR_OK;")
        self.indent_level -= 1
        self.write_line("}")
        self.write_line()

        for sname, sdata in self.protocol.structs.items():
            self.gen_implementation(sname, sdata)

        for mname, mdata in self.protocol.messages.items():
            self.gen_implementation(mname, mdata)

        self.add_boilerplate(self.subs, 2)
        return "\n".join(self.output)
