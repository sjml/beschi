from ..protocol import Protocol, BASE_TYPE_SIZES
from ..writer import Writer
from .. import LIB_NAME, LIB_VERSION

LANGUAGE_NAME = "C"


class CWriter(Writer):
    language_name = LANGUAGE_NAME
    default_extension = ".h"

    def __init__(self, p: Protocol):
        super().__init__(protocol=p, tab="    ")

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

    def gen_default(self, members: list[tuple[str,str]]):
        for mname, mtype in members:
            if mtype in self.base_defaults:
                self.write_line(f".{mname} = {self.base_defaults[mtype]},")
            elif mtype == "string":
                self.write_line(f".{mname} = (char*)\"\",")
            elif mtype[0] == "[" and mtype[-1] == "]":
                self.write_line(f".{mname} = NULL,")
            else:
                self.write_line(f".{mname} = {{")
                self.indent_level += 1
                self.gen_default(self.protocol.structs[mtype])
                self.indent_level -= 1
                self.write_line("},")

    def gen_struct(self, sname: str, members: list[tuple[str,str]], is_message: bool = False):
        self.write_line("typedef struct {")
        self.indent_level += 1
        if is_message:
            self.write_line(f"{self.prefix}MessageType _mt;")
        for member_name, member_type in members:
            if member_type in BASE_TYPE_SIZES.keys():
                self.write_line(f"{self.type_mapping[member_type]} {member_name};")
            elif member_type == "string":
                self.write_line(f"{self.type_mapping['uint32']} {member_name}_len;")
                self.write_line(f"{self.type_mapping[member_type]} {member_name};")
            elif member_type[0] == "[" and member_type[-1] == "]":
                listed_type = member_type[1:-1]
                self.write_line(f"{self.type_mapping['uint32']} {member_name}_len;")
                if listed_type == "string":
                    self.write_line(f"{self.type_mapping['uint32']}* {member_name}_els_len;")
                if listed_type in BASE_TYPE_SIZES.keys() or listed_type == "string":
                    self.write_line(f"{self.type_mapping[listed_type]}* {member_name};")
                elif listed_type in self.protocol.structs:
                    self.write_line(f"{self.prefix}{listed_type}* {member_name};")
            elif member_type in self.protocol.structs:
                self.write_line(f"{self.prefix}{member_type} {member_name};")

        self.indent_level -= 1
        self.write_line(f"}} {self.prefix}{sname};")
        if is_message:
            self.write_line(f"extern const {self.prefix}{sname} {self.prefix}{sname}_default;")
            self.write_line(f"const {self.prefix}{sname} {self.prefix}{sname}_default = {{")
            self.indent_level += 1
            self.write_line(f"._mt = {self.prefix}MessageType_{sname},")
            self.gen_default(members)
            self.indent_level -= 1
            self.write_line("};")
        self.write_line()
        if is_message:
            self.write_line(f"{self.prefix}err_t {self.prefix}{sname}_WriteBytes({self.prefix}DataAccess* w, const {self.prefix}{sname}* src, bool tag);")
        else:
            self.write_line(f"{self.prefix}err_t {self.prefix}{sname}_WriteBytes({self.prefix}DataAccess* w, const {self.prefix}{sname}* src);")
        self.write_line(f"{self.prefix}err_t {self.prefix}{sname}_FromBytes({self.prefix}DataAccess* r, {self.prefix}{sname}* dst);")
        if is_message:
            self.write_line(f"{self.prefix}err_t {self.prefix}{sname}_GetSizeInBytes(const {self.prefix}{sname}* m, size_t* size);")
            self.write_line(f"void {self.prefix}{sname}_Destroy({self.prefix}{sname} *m);")

        self.write_line()
        self.write_line()

    def deserializer(self, varname: str, vartype: str, accessor: str):
        if vartype in BASE_TYPE_SIZES.keys():
            self.write_line(f"err = {self.prefix}_Read{self.base_serializers[vartype]}(r, &({accessor}{varname}));")
            self.err_check_return()
        elif vartype == "string":
            self.write_line(f"err = {self.prefix}_ReadString(r, &({accessor}{varname}), &({accessor}{varname}_len));")
            self.err_check_return()
        elif vartype[0] == "[" and vartype[-1] == "]":
            listed_type = vartype[1:-1]
            self.write_line(f"err = {self.prefix}_ReadUInt32(r, &({accessor}{varname}_len));")
            self.err_check_return()
            if listed_type in BASE_TYPE_SIZES.keys() or listed_type == "string":
                self.write_line(f"{accessor}{varname} = ({self.type_mapping[listed_type]}*)malloc(sizeof({self.type_mapping[listed_type]}) * {accessor}{varname}_len);")
                self.write_line(f"if ({accessor}{varname} == NULL) {{ return {self.prefix.upper()}ERR_ALLOCATION_FAILURE; }}")
                if listed_type == "string":
                    self.write_line(f"{accessor}{varname}_els_len = ({self.type_mapping['uint32']}*)malloc(sizeof({self.type_mapping['uint32']}) * {accessor}{varname}_len);")
                    self.write_line(f"if ({accessor}{varname} == NULL) {{ return {self.prefix.upper()}ERR_ALLOCATION_FAILURE; }}")
            else:
                self.write_line(f"{accessor}{varname} = ({self.prefix}{listed_type}*)malloc(sizeof({self.prefix}{listed_type}) * {accessor}{varname}_len);")
                self.write_line(f"if ({accessor}{varname} == NULL) {{ return {self.prefix.upper()}ERR_ALLOCATION_FAILURE; }}")
            self.write_line(f"for (uint32_t i = 0; i < {accessor}{varname}_len; i++) {{")
            self.indent_level += 1
            if listed_type in BASE_TYPE_SIZES.keys():
                self.write_line(f"err = {self.prefix}_Read{self.base_serializers[listed_type]}(r, &({accessor}{varname}[i]));")
            elif listed_type == "string":
                self.write_line(f"err = {self.prefix}_ReadString(r, &({accessor}{varname}[i]), &({accessor}{varname}_els_len[i]));")
            else:
                self.write_line(f"err = {self.prefix}{listed_type}_FromBytes(r, &({accessor}{varname}[i]));")

            self.err_check_return()
            self.indent_level -= 1
            self.write_line("}")
        else:
            self.write_line(f"err = {self.prefix}{vartype}_FromBytes(r, &({accessor}{varname}));")
            self.err_check_return()

    def serializer(self, varname: str, vartype: str, accessor: str):
        if vartype in BASE_TYPE_SIZES.keys():
            self.write_line(f"err = {self.prefix}_Write{self.base_serializers[vartype]}(w, &({accessor}{varname}));")
            self.err_check_return()
        elif vartype == "string":
            self.write_line(f"err = {self.prefix}_WriteString(w, &({accessor}{varname}), &({accessor}{varname}_len));")
            self.err_check_return()
        elif vartype[0] == "[" and vartype[-1] == "]":
            listed_type = vartype[1:-1]
            self.write_line(f"err = {self.prefix}_WriteUInt32(w, &({accessor}{varname}_len));")
            self.err_check_return()
            self.write_line(f"for (uint32_t i = 0; i < {accessor}{varname}_len; i++) {{")
            self.indent_level += 1
            if listed_type in BASE_TYPE_SIZES.keys():
                self.write_line(f"err = {self.prefix}_Write{self.base_serializers[listed_type]}(w, &({accessor}{varname}[i]));")
            elif listed_type == "string":
                self.write_line(f"err = {self.prefix}_WriteString(w, &({accessor}{varname}[i]), &({accessor}{varname}_els_len[i]));")
            else:
                self.write_line(f"err = {self.prefix}{listed_type}_WriteBytes(w, &({accessor}{varname}[i]));")

            self.err_check_return()
            self.indent_level -= 1
            self.write_line("}")
        else:
            self.write_line(f"err = {self.prefix}{vartype}_WriteBytes(w, &({accessor}{varname}));")
            self.err_check_return()

    def gen_measurement(self, s: tuple[str, list[tuple[str,str]]], accessor_prefix: str = "") -> tuple[list[str], int]:
        lines: list[str] = []

        accum = 0
        if self.protocol.is_simple(s[0]):
            lines.append(f"*size = {self.protocol.calculate_size(s[0])};")
        else:
            size_init = "*size = 0;"
            lines.append(size_init)

            for var_name, var_type in s[1]:
                if self.protocol.is_simple(var_type):
                    accum += self.protocol.calculate_size(var_type)
                else:
                    if var_type == "string":
                        accum += BASE_TYPE_SIZES["uint32"]
                        lines.append(f"*size += {accessor_prefix}{var_name}_len;")
                    elif var_type == "[string]":
                        accum += BASE_TYPE_SIZES["uint32"]
                        lines.append(f"for (uint32_t i = 0; i < {accessor_prefix}{var_name}_len; i++) {{")
                        lines.append(f"{self.tab}*size += {BASE_TYPE_SIZES['uint32']} + {accessor_prefix}{var_name}_els_len[i];")
                        lines.append("}")
                    elif var_type[0] == "[" and var_type[-1] == "]":
                        listed_var_type = var_type[1:-1]
                        if self.protocol.is_simple(listed_var_type):
                            accum += BASE_TYPE_SIZES["uint32"]
                            lines.append(f"*size += {accessor_prefix}{var_name}_len * {self.protocol.calculate_size(listed_var_type)};")
                        else:
                            accum += BASE_TYPE_SIZES["uint32"]
                            lines.append(f"for (uint32_t i = 0; i < {accessor_prefix}{var_name}_len; i++) {{")
                            clines, caccum = self.gen_measurement((var_type, self.protocol.structs[listed_var_type]), f"{accessor_prefix}{var_name}[i].")
                            if clines[0] == size_init:
                                clines = clines[1:]
                            clines.append(f"*size += {caccum};")
                            lines += [f"{self.tab}{l}" for l in clines]
                            lines.append("}")
                    else:
                        clines, caccum = self.gen_measurement((var_type, self.protocol.structs[var_type]), f"{accessor_prefix}{var_name}.")
                        if clines[0] == size_init:
                            clines = clines[1:]
                        lines += clines
                        accum += caccum
        return lines, accum

    def gen_implementation(self, sname: str, members: list[tuple[str,str]], is_message: bool = False):
        self.write_line(f"{self.prefix}err_t {self.prefix}{sname}_FromBytes({self.prefix}DataAccess* r, {self.prefix}{sname}* dst) {{")
        self.indent_level += 1
        if is_message:
            self.write_line(f"dst->_mt = {self.prefix}MessageType_{sname};")
        if len(members) > 0:
            self.write_line(f"{self.prefix}err_t err;")
        [self.deserializer(v, t, "dst->") for v,t in members]
        self.write_line(f"return {self.prefix.upper()}ERR_OK;")
        self.indent_level -= 1
        self.write_line("}")
        self.write_line()

        if is_message:
            self.write_line(f"{self.prefix}err_t {self.prefix}{sname}_WriteBytes({self.prefix}DataAccess* w, const {self.prefix}{sname}* src, bool tag) {{")
        else:
            self.write_line(f"{self.prefix}err_t {self.prefix}{sname}_WriteBytes({self.prefix}DataAccess* w, const {self.prefix}{sname}* src) {{")
        self.indent_level += 1
        self.write_line(f"{self.prefix}err_t err;")
        if is_message:
            self.write_line("if (tag) {")
            self.indent_level += 1
            self.write_line(f"err = {self.prefix}_WriteUInt8(w, (const uint8_t *)&(src->_mt));")
            self.err_check_return()
            self.indent_level -= 1
            self.write_line("}")
        [self.serializer(v, t, "src->") for v,t in members]
        self.write_line(f"return {self.prefix.upper()}ERR_OK;")
        self.indent_level -= 1
        self.write_line("}")
        self.write_line()

        if is_message:
            self.write_line(f"{self.prefix}err_t {self.prefix}{sname}_GetSizeInBytes(const {self.prefix}{sname}* m, size_t* size) {{")
            self.indent_level += 1
            measure_lines, accumulator = self.gen_measurement((sname, members), "m->")
            [self.write_line(s) for s in measure_lines]
            if accumulator > 0:
                self.write_line(f"*size += {accumulator};")
            self.write_line(f"return {self.prefix.upper()}ERR_OK;")
            self.indent_level -= 1
            self.write_line("}")
            self.write_line()

            self.write_line(f"void {self.prefix}{sname}_Destroy({self.prefix}{sname} *m) {{")
            self.indent_level += 1

            def destroyer(vartype: str, varname: str):
                if self.protocol.is_simple(vartype):
                    return
                if vartype == "string":
                    self.write_line(f"free({varname});")
                elif vartype == "[string]":
                    self.write_line(f"for (uint32_t i = 0; i < {varname}_len; i++) {{")
                    self.indent_level += 1
                    self.write_line(f"free({varname}[i]);")
                    self.indent_level -= 1
                    self.write_line("}")
                    self.write_line(f"free({varname}_els_len);")
                    self.write_line(f"free({varname});")
                elif vartype[0] == "[" and vartype[-1] == "]":
                    listed_type = vartype[1:-1]
                    if self.protocol.is_simple(listed_type):
                        self.write_line(f"free({varname});")
                    else:
                        self.write_line(f"for (uint32_t i = 0; i < {varname}_len; i++) {{")
                        self.indent_level += 1
                        destroyer(listed_type, f"{varname}[i]")
                        self.indent_level -= 1
                        self.write_line("}")
                        self.write_line(f"free({varname});")
                else:
                    [destroyer(t, f"{varname}.{n}") for (n,t) in self.protocol.structs[vartype]]

            [destroyer(t, f"m->{n}") for (n,t) in members]
            self.write_line("free(m);")
            self.indent_level -= 1
            self.write_line("}")
            self.write_line()



    def generate(self) -> str:
        self.output = []
        self.write_line(f"// This file was automatically generated by {LIB_NAME} v{LIB_VERSION}.")
        self.write_line( "// <https://github.com/sjml/beschi>")
        self.write_line(f"// Do not edit directly.")
        self.write_line()
        self.add_boilerplate(self.subs, 0)

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

        for sname, smembers in self.protocol.structs.items():
            self.gen_struct(sname, smembers)

        for mname, mmembers in self.protocol.messages.items():
            self.gen_struct(mname, mmembers, True)

        self.add_boilerplate(self.subs, 1)

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
        for msg_type in self.protocol.messages.keys():
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
        for msg_type in self.protocol.messages.keys():
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
        for msg_type in self.protocol.messages.keys():
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

        for sname, smembers in self.protocol.structs.items():
            self.gen_implementation(sname, smembers)

        for mname, mmembers in self.protocol.messages.items():
            self.gen_implementation(mname, mmembers, True)

        self.add_boilerplate(self.subs, 2)
        return "\n".join(self.output)
