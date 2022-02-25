from ..protocol import Protocol, BASE_TYPE_SIZES
from ..writer import Writer
from .. import LIB_NAME, LIB_VERSION

LANGUAGE_NAME = "C"


class CWriter(Writer):
    language_name = LANGUAGE_NAME
    default_extension = ".h"
    in_progress = True

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

        self.subs: list[tuple[str,str]] = []
        self.prefix = "beschi_"
        if self.protocol.namespace != None:
            self.subs = [("beschi", self.protocol.namespace), ("BESCHI", self.protocol.namespace.upper())]
            self.prefix = f"{self.protocol.namespace}_"

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
            self.write_line(f"{self.prefix.upper()}ERR_CHECK_RETURN;")
        elif vartype == "string":
            self.write_line(f"err = {self.prefix}_ReadString(r, &({accessor}{varname}), &({accessor}{varname}_len));")
            self.write_line(f"{self.prefix.upper()}ERR_CHECK_RETURN;")
        elif vartype[0] == "[" and vartype[-1] == "]":
            listed_type = vartype[1:-1]
            self.write_line(f"err = {self.prefix}_ReadUInt32(r, &({accessor}{varname}_len));")
            self.write_line(f"{self.prefix.upper()}ERR_CHECK_RETURN;")
            if listed_type in BASE_TYPE_SIZES.keys() or listed_type == "string":
                self.write_line(f"{accessor}{varname} = malloc(sizeof({self.type_mapping[listed_type]}) * {accessor}{varname}_len);")
                if listed_type == "string":
                    self.write_line(f"{accessor}{varname}_els_len = malloc(sizeof({self.type_mapping['uint32']}) * {accessor}{varname}_len);")
            else:
                self.write_line(f"{accessor}{varname} = malloc(sizeof({self.prefix}{listed_type}) * {accessor}{varname}_len);")
            self.write_line(f"for (uint32_t i = 0; i < {accessor}{varname}_len; i++) {{")
            self.indent_level += 1
            if listed_type in BASE_TYPE_SIZES.keys():
                self.write_line(f"err = {self.prefix}_Read{self.base_serializers[listed_type]}(r, &({accessor}{varname}));")
            elif listed_type == "string":
                self.write_line(f"err = {self.prefix}_ReadString(r, &({accessor}{varname}[i]), &({accessor}{varname}_els_len[i]));")
            else:
                self.write_line(f"err = {self.prefix}{listed_type}_FromBytes(r, &({accessor}{varname}[i]));")

            self.write_line(f"{self.prefix.upper()}ERR_CHECK_RETURN;")
            self.indent_level -= 1
            self.write_line("}")
        else:
            self.write_line(f"err = {self.prefix}{vartype}_FromBytes(r, &({accessor}{varname}));")
            self.write_line(f"{self.prefix.upper()}ERR_CHECK_RETURN;")

    def serializer(self, varname: str, vartype: str, accessor: str):
        if vartype in BASE_TYPE_SIZES.keys():
            self.write_line(f"err = {self.prefix}_Write{self.base_serializers[vartype]}(w, &({accessor}{varname}));")
            self.write_line(f"{self.prefix.upper()}ERR_CHECK_RETURN;")
        elif vartype == "string":
            self.write_line(f"err = {self.prefix}_WriteString(w, &({accessor}{varname}), &({accessor}{varname}_len));")
            self.write_line(f"{self.prefix.upper()}ERR_CHECK_RETURN;")
        elif vartype[0] == "[" and vartype[-1] == "]":
            listed_type = vartype[1:-1]
            self.write_line(f"err = {self.prefix}_WriteUInt32(w, &({accessor}{varname}_len));")
            self.write_line(f"{self.prefix.upper()}ERR_CHECK_RETURN;")
            self.write_line(f"for (uint32_t i = 0; i < {accessor}{varname}_len; i++) {{")
            self.indent_level += 1
            if listed_type in BASE_TYPE_SIZES.keys():
                self.write_line(f"err = {self.prefix}_Write{self.base_serializers[listed_type]}(w, &({accessor}{varname}));")
            elif listed_type == "string":
                self.write_line(f"err = {self.prefix}_WriteString(w, &({accessor}{varname}[i]), &({accessor}{varname}_els_len[i]));")
            else:
                self.write_line(f"err = {self.prefix}{listed_type}_WriteBytes(w, &({accessor}{varname}[i]));")

            self.write_line(f"{self.prefix.upper()}ERR_CHECK_RETURN;")
            self.indent_level -= 1
            self.write_line("}")
        else:
            self.write_line(f"err = {self.prefix}{vartype}_WriteBytes(w, &({accessor}{varname}));")
            self.write_line(f"{self.prefix.upper()}ERR_CHECK_RETURN;")

    def gen_measurement(self, s: tuple[str, list[tuple[str,str]]], accessor_prefix: str = "") -> tuple[list[str], int]:
        lines: list[str] = []

        accum = 0
        if self.protocol.is_simple(s[0]):
            lines.append(f"return {self.protocol.calculate_size(s[0])};")
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
            self.write_line(f"{self.prefix.upper()}ERR_CHECK_RETURN;")
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
            if len(measure_lines) > 1:
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



    def generate(self) -> str:
        self.output = []
        self.write_line(f"// This file was automatically generated by {LIB_NAME} v{LIB_VERSION}.")
        self.write_line( "// <https://github.com/sjml/beschi>")
        self.write_line(f"// Do not edit directly.")
        self.write_line()
        self.add_boilerplate(self.subs, 0)

        # structure definitions and message declarations
        self.write_line("typedef enum {")
        self.indent_level += 1
        self.write_line(f"{self.prefix}MessageType___NullMessage = 0,")
        [self.write_line(f"{self.prefix}MessageType_{k} = {i+1},") for i, k in enumerate(self.protocol.messages.keys())]
        self.indent_level -= 1
        self.write_line(f"}} {self.prefix}MessageType;")
        self.write_line()
        self.write_line(f"{self.prefix}MessageType {self.prefix}GetMessageType(const void* m);")
        self.write_line(f"{self.prefix}err_t {self.prefix}GetSizeInBytes(const void* m, size_t* len);")
        self.write_line(f"{self.prefix}err_t {self.prefix}ProcessRawBytes({self.prefix}DataAccess* r, void** msgListOut, size_t* len);")
        self.write_line()

        for sname, smembers in self.protocol.structs.items():
            self.gen_struct(sname, smembers)

        for mname, mmembers in self.protocol.messages.items():
            self.gen_struct(mname, mmembers, True)

        self.add_boilerplate(self.subs, 1)

        self.write_line(f"{self.prefix}MessageType {self.prefix}GetMessageType(const void* m) {{")
        self.indent_level += 1
        self.write_line("// TODO")
        self.write_line(f"return {self.prefix}MessageType___NullMessage;")
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
            self.write_line(f"return {self.prefix}{msg_type}_GetSizeInBytes(m, len);")
            self.write_line("break;")
            self.indent_level -= 1
            self.write_line("}")
        self.write_line(f"return {self.prefix.upper()}ERR_INVALID_DATA;")
        self.indent_level -= 1
        self.write_line("}")

        self.write_line(f"{self.prefix}err_t {self.prefix}ProcessRawBytes({self.prefix}DataAccess* r, void** msgListDst, size_t* len) {{")
        self.indent_level += 1
        self.write_line("// TODO")
        self.write_line(f"return {self.prefix.upper()}ERR_OK;")
        self.indent_level -= 1
        self.write_line("}")

        for sname, smembers in self.protocol.structs.items():
            self.gen_implementation(sname, smembers)

        for mname, mmembers in self.protocol.messages.items():
            self.gen_implementation(mname, mmembers, True)

        self.add_boilerplate(self.subs, 2)
        return "\n".join(self.output)
