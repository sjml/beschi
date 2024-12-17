import argparse

from ..protocol import Protocol, Variable, Struct, Enum, NUMERIC_TYPE_SIZES
from ..writer import Writer, TextUtil
from .. import LIB_NAME, LIB_VERSION

LANGUAGE_NAME = "TypeScript"


class TypeScriptWriter(Writer):
    language_name = LANGUAGE_NAME
    default_extension = ".ts"

    @classmethod
    def get_additional_args(cls, parser: argparse.ArgumentParser):
        if cls.language_name == LANGUAGE_NAME:
            group = parser.add_argument_group(cls.language_name)
            group.add_argument("--typescript-use-namespace", action="store_const", const=True, default=False, help="wrap generated TypeScript code in a namespace")

    def __init__(self, p: Protocol, extra_args: dict[str,any] = {}):
        super().__init__(protocol=p, tab="  ")

        self.embed_protocol = extra_args["embed_protocol"]

        self.use_namespace = extra_args["typescript_use_namespace"]

        for var_type in NUMERIC_TYPE_SIZES:
            if var_type == "bool":
                self.type_mapping[var_type] = "boolean"
            elif var_type in ["int64", "uint64"]:
                self.type_mapping[var_type] = "bigint"
            else:
                # <sigh>, JavaScript
                self.type_mapping[var_type] = "number"

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

        self.is_assembly_script = False

    def deserializer(self, var: Variable, accessor: str):
        var_clean = TextUtil.replace(var.name, [("[", "_"), ("]", "_")])
        if var.is_list:
            self.write_line(f"const {var_clean}_Length = da.get{self.base_serializers[self.protocol.list_size_type]}();")
            if self.is_assembly_script:
                self.write_line("if (da.hasError) { return null; }")
            self.write_line(f"{accessor}{var.name} = new Array<{self.type_mapping[var.vartype]}>({var_clean}_Length);")
            idx = self.indent_level
            self.write_line(f"for (let i{idx}: {self.type_mapping[self.protocol.list_size_type]} = 0; i{idx} < {var_clean}_Length; i{idx}++) {{")
            self.indent_level += 1
            if var.vartype in self.protocol.enums:
                e = self.protocol.enums[var.vartype]
                if not self.is_assembly_script:
                    self.write_line(f"const _{var.name} = da.get{self.base_serializers[e.encoding]}();")
                    self.write_line(f"if ({var.vartype}[_{var.name}] === undefined) {{")
                    self.indent_level += 1
                    self.write_line(f"throw new Error(`Enum (${{_{var.name}}}) out of range for {var.vartype}`);")
                    self.indent_level -= 1
                    self.write_line("}")
                else:
                    self.write_line(f"let _{var.name} = da.get{self.base_serializers[e.encoding]}();")
                    self.write_line("if (da.hasError) { return null; }")
                    self.write_line(f"if (_{var.name} < {e.get_minimum_pair()[1]} || _{var.name} >= ({var.vartype}._Unknown as {self.type_mapping[e.encoding]})) {{")
                    self.indent_level += 1
                    self.write_line(f"_{var.name} = {var.vartype}._Unknown as {self.type_mapping[e.encoding]};")
                    self.indent_level -= 1
                    self.write_line("}")
                self.write_line(f"{accessor}{var.name}[i{idx}] = _{var.name};")
            else:
                inner = Variable(self.protocol, f"{var.name}[i{idx}]", var.vartype)
                self.deserializer(inner, accessor)
            self.indent_level -= 1
            self.write_line("}")
        elif var.vartype == "string":
            self.write_line(f"{accessor}{var.name} = da.getString();")
            if self.is_assembly_script:
                self.write_line("if (da.hasError) { return null; }")
        elif var.vartype in self.protocol.enums:
            e = self.protocol.enums[var.vartype]
            if not self.is_assembly_script:
                self.write_line(f"const _{var.name} = da.get{self.base_serializers[e.encoding]}();")
                self.write_line(f"if ({var.vartype}[_{var.name}] === undefined) {{")
                self.indent_level += 1
                self.write_line(f"throw new Error(`Enum (${{_{var.name}}}) out of range for {var.vartype}`);")
                self.indent_level -= 1
                self.write_line("}")
            else:
                self.write_line(f"let _{var.name} = da.get{self.base_serializers[e.encoding]}();")
                self.write_line("if (da.hasError) { return null; }")
                self.write_line(f"if (_{var.name} < {e.get_minimum_pair()[1]} || _{var.name} >= ({var.vartype}._Unknown as {self.type_mapping[e.encoding]})) {{")
                self.indent_level += 1
                self.write_line(f"_{var.name} = {var.vartype}._Unknown as {self.type_mapping[e.encoding]};")
                self.indent_level -= 1
                self.write_line("}")
            self.write_line(f"{accessor}{var.name} = _{var.name};")
        elif var.vartype in NUMERIC_TYPE_SIZES:
            self.write_line(f"{accessor}{var.name} = da.get{self.base_serializers[var.vartype]}();")
            if self.is_assembly_script:
                self.write_line("if (da.hasError) { return null; }")
        else:
            if not self.is_assembly_script:
                self.write_line(f"{accessor}{var.name} = {var.vartype}.fromBytes(da);")
            else:
                self.write_line(f"const _{var_clean} = {var.vartype}.fromBytes(da);")
                self.write_line(f"if (_{var_clean} == null) {{")
                self.indent_level += 1
                self.write_line("return null;")
                self.indent_level -= 1
                self.write_line("}")
                self.write_line("else {")
                self.indent_level += 1
                self.write_line(f"{accessor}{var.name} = _{var_clean};")
                self.indent_level -= 1
                self.write_line("}")

    def serializer(self, var: Variable, accessor: str):
        if var.is_list:
            if not self.is_assembly_script:
                self.write_line(f"da.set{self.base_serializers[self.protocol.list_size_type]}({accessor}{var.name}.length);")
            else:
                self.write_line(f"da.set{self.base_serializers[self.protocol.list_size_type]}({accessor}{var.name}.length as {self.type_mapping[self.protocol.list_size_type]});")
                self.write_line("if (da.hasError) { return false; }")
            self.write_line(f"for (let i = 0; i < {accessor}{var.name}.length; i++) {{")
            self.indent_level += 1
            self.write_line(f"let el = {accessor}{var.name}[i];")
            inner = Variable(self.protocol, "el", var.vartype)
            self.serializer(inner, "")
            self.indent_level -= 1
            self.write_line("}")
        elif var.vartype == "string":
            self.write_line(f"da.setString({accessor}{var.name});")
            if self.is_assembly_script:
                self.write_line("if (da.hasError) { return false; }")
        elif var.vartype in self.protocol.enums:
            e = self.protocol.enums[var.vartype]
            if not self.is_assembly_script:
                self.write_line(f"da.set{self.base_serializers[e.encoding]}({accessor}{var.name});")
            else:
                self.write_line(f"da.set{self.base_serializers[e.encoding]}({accessor}{var.name} as {self.type_mapping[e.encoding]});")
                self.write_line("if (da.hasError) { return false; }")
        elif var.vartype in NUMERIC_TYPE_SIZES:
            self.write_line(f"da.set{self.base_serializers[var.vartype]}({accessor}{var.name});")
            if self.is_assembly_script:
                self.write_line("if (da.hasError) { return false; }")
        else:
            if not self.is_assembly_script:
                self.write_line(f"{accessor}{var.name}.writeBytes(da);")
            else:
                self.write_line(f"if (!{accessor}{var.name}.writeBytes(da)) {{ return false; }};")

    def gen_measurement(self, st: Struct, accessor: str = "") -> tuple[list[str], int]:
        lines: list[str] = []
        accum = 0

        if st.is_simple():
            lines.append(f"return {self.protocol.get_size_of(st.name)};")
        else:
            if not self.is_assembly_script:
                size_init = "let size: number = 0;"
            else:
                size_init = "let size: usize = 0;"
            lines.append(size_init)

            for var in st.members:
                if var.is_list:
                    accum += NUMERIC_TYPE_SIZES[self.protocol.list_size_type]
                    if var.is_simple(True):
                        lines.append(f"size += {accessor}{var.name}.length * {self.protocol.get_size_of(var.vartype)};")
                    elif var.vartype == "string":
                        lines.append(f"for (let {var.name}_i=0; {var.name}_i < {accessor}{var.name}.length; {var.name}_i++) {{")
                        if not self.is_assembly_script:
                            lines.append(f"{self.tab}size += {NUMERIC_TYPE_SIZES[self.protocol.string_size_type]} + _textEnc.encode({accessor}{var.name}[{var.name}_i]).byteLength;")
                        else:
                            lines.append(f"{self.tab}size += {NUMERIC_TYPE_SIZES[self.protocol.string_size_type]} + String.UTF8.encode({accessor}{var.name}[{var.name}_i], false).byteLength;")
                        lines.append("}")
                    else:
                        var_clean = TextUtil.replace(var.name, [("[", "_"), ("]", "_")])
                        lines.append(f"for (let {var_clean}_i=0; {var_clean}_i < {accessor}{var.name}.length; {var_clean}_i++) {{")
                        clines, caccum = self.gen_measurement(self.protocol.structs[var.vartype], f"{accessor}{var.name}[{var_clean}_i].")
                        if clines[0] == size_init:
                            clines = clines[1:]
                        clines.append(f"size += {caccum};")
                        lines += [f"{self.tab}{l}" for l in clines]
                        lines.append("}")
                else:
                    if var.is_simple():
                        accum += self.protocol.get_size_of(var.vartype)
                    elif var.vartype == "string":
                        accum += NUMERIC_TYPE_SIZES[self.protocol.string_size_type]
                        if not self.is_assembly_script:
                            lines.append(f"size += _textEnc.encode({accessor}{var.name}).byteLength;")
                        else:
                            lines.append(f"size += String.UTF8.encode({accessor}{var.name}, false).byteLength;")
                    else:
                        clines, caccum = self.gen_measurement(self.protocol.structs[var.vartype], f"{accessor}{var.name}.")
                        if clines[0] == size_init:
                            clines = clines[1:]
                        lines += clines
                        accum += caccum
        return lines, accum

    def gen_enum(self, ename: str, edata: Enum):
        self.write_line(f"export enum {ename} {{")
        self.indent_level += 1
        for v, vi in edata.values.items():
            self.write_line(f"{v} = {vi},")
        if self.is_assembly_script:
            self.write_line("_Unknown,")
        self.indent_level -= 1
        self.write_line("}")
        self.write_line()

    def gen_struct(self, sname: str, sdata: Struct):
        if sdata.is_message:
            self.write_line(f"export class {sname} extends Message {{")
        else:
            self.write_line(f"export class {sname} {{")
        self.indent_level += 1

        for var in sdata.members:
            if var.is_list:
                self.write_line(f"{var.name}: {self.type_mapping[var.vartype]}[] = [];")
            else:
                default_value = "0"
                if self.type_mapping[var.vartype] == "bigint":
                    default_value = "0n"
                elif self.type_mapping[var.vartype] == "boolean":
                    default_value = "false"
                elif self.type_mapping[var.vartype] == "string":
                    default_value = '""'
                elif var.vartype in self.protocol.enums:
                    e = self.protocol.enums[var.vartype]
                    default_value = f"{var.vartype}.{e.get_default_pair()[0]}"
                elif var.vartype in self.protocol.structs:
                    default_value = f"new {var.vartype}()"
                self.write_line(f"{var.name}: {self.type_mapping[var.vartype]}{f' = {default_value}' if default_value else ''};")
        self.write_line()

        if sdata.is_message:
            self.write_line(f"getMessageType() : MessageType {{ return MessageType.{sname}Type; }}")
            self.write_line()

            if not self.is_assembly_script:
                self.write_line("getSizeInBytes(): number {")
            else:
                self.write_line("getSizeInBytes(): usize {")
            self.indent_level += 1
            measure_lines, accumulator = self.gen_measurement(sdata, "this.")
            [self.write_line(s) for s in measure_lines]
            if accumulator > 0:
                self.write_line(f"size += {accumulator};")
            if len(measure_lines) > 1:
                self.write_line(f"return size;")
            self.indent_level -= 1
            self.write_line("}")
            self.write_line()

        if sdata.is_message:
            if not self.is_assembly_script:
                self.write_line(f"static override fromBytes(data: DataView|DataAccess|ArrayBuffer): {sname} {{")
                self.indent_level += 1
                self.write_line("let da: DataAccess;")
                self.write_line("if (data instanceof DataView) {")
                self.indent_level += 1
                self.write_line("da = new DataAccess(data);")
                self.indent_level -= 1
                self.write_line("}")
                self.write_line("else if (data instanceof ArrayBuffer) {")
                self.indent_level += 1
                self.write_line("da = new DataAccess(new DataView(data));")
                self.indent_level -= 1
                self.write_line("}")
                self.write_line("else {")
                self.indent_level += 1
                self.write_line("da = data;")
                self.indent_level -= 1
                self.write_line("}")
            else:
                self.write_line(f"static override fromBytes(data: DataView): {sname} | null {{")
                self.indent_level += 1
                self.write_line("const da = new DataAccess(data);")
                self.write_line(f"return {sname}.fromBytesDA(da);")
                self.indent_level -= 1
                self.write_line("}")
                self.write_line()
                self.write_line(f"static override fromBytesDA(da: DataAccess): {sname} | null {{")
                self.indent_level += 1
        else:
            if not self.is_assembly_script:
                self.write_line(f"static fromBytes(da: DataAccess): {sname} {{")
            else:
                self.write_line(f"static fromBytes(da: DataAccess): {sname} | null {{")
            self.indent_level += 1
        if sdata.is_message and not self.is_assembly_script:
            self.write_line("try {")
            self.indent_level += 1
        self.write_line(f"const n{sname} = new {self.type_mapping[sname]}();")
        [self.deserializer(mem, f"n{sname}.") for mem in sdata.members]
        self.write_line(f"return n{sname};")
        if sdata.is_message and not self.is_assembly_script:
            self.indent_level -= 1
            self.write_line("}")
            self.write_line("catch (err) {")
            self.indent_level += 1
            self.write_line("let errMsg = \"[Unknown error]\";")
            self.write_line("if (err instanceof Error) {")
            self.indent_level += 1
            self.write_line("errMsg = `${err.name} -- ${err.message}`;")
            self.indent_level -= 1
            self.write_line("}")
            self.write_line(f"throw new Error(`Could not read {sname} from offset ${{da.currentOffset}} (${{errMsg}})`);")
            self.indent_level -= 1
            self.write_line("}")
        self.indent_level -= 1
        self.write_line("}")
        self.write_line()

        if sdata.is_message:
            if not self.is_assembly_script:
                self.write_line("writeBytes(data: DataView|DataAccess, tag: boolean): void {")
                self.indent_level += 1
                self.write_line("let da: DataAccess;")
                self.write_line("if (data instanceof DataView) {")
                self.indent_level += 1
                self.write_line("da = new DataAccess(data);")
                self.indent_level -= 1
                self.write_line("}")
                self.write_line("else {")
                self.indent_level += 1
                self.write_line("da = data;")
                self.indent_level -= 1
                self.write_line("}")
                self.write_line("if (tag) {")
                self.indent_level += 1
                self.write_line(f"da.setByte(MessageType.{sname}Type);")
                self.indent_level -= 1
                self.write_line("}")
            else:
                self.write_line("writeBytes(data: DataView, tag: boolean): bool {")
                self.indent_level += 1
                self.write_line("const da = new DataAccess(data);")
                self.write_line(f"return this.writeBytesDA(da, tag);")
                self.indent_level -= 1
                self.write_line("}")
                self.write_line()
                self.write_line("writeBytesDA(da: DataAccess, tag: boolean): bool {")
                self.indent_level += 1
                self.write_line("if (tag) {")
                self.indent_level += 1
                self.write_line(f"da.setByte(MessageType.{sname}Type as u8);")
                self.write_line("if (da.hasError) { return false; }")
                self.indent_level -= 1
                self.write_line("}")
        else:
            if not self.is_assembly_script:
                self.write_line("writeBytes(da: DataAccess): void {")
            else:
                self.write_line("writeBytes(da: DataAccess): bool {")
            self.indent_level += 1
        [self.serializer(mem, "this.") for mem in sdata.members]
        if self.is_assembly_script:
            self.write_line("return true;")
        self.indent_level -= 1
        self.write_line("}")

        self.indent_level -= 1
        self.write_line("}")
        self.write_line()

    def generate(self) -> str:
        self.output = []

        self.write_line(f"// This file was automatically generated by {LIB_NAME} v{LIB_VERSION}")
        self.write_line( "// <https://github.com/sjml/beschi>")
        self.write_line( "// Do not edit directly.")
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

        if self.use_namespace:
            self.write_line(f"namespace {self.protocol.namespace} {{")
            self.indent_level += 1

        self.add_boilerplate(substitutions=[
            ("{# STRING_SIZE_TYPE #}", self.base_serializers[self.protocol.string_size_type]),
            ("{# NATIVE_STRING_SIZE_TYPE #}", self.type_mapping[self.protocol.string_size_type]),
        ])

        self.write_line("export enum MessageType {")
        self.indent_level += 1
        [self.write_line(f"{k}Type = {i+1},") for i, k in enumerate(self.protocol.messages)]
        if self.is_assembly_script:
            self.write_line("_Unknown,")
        self.indent_level -= 1
        self.write_line("}")
        self.write_line()

        if not self.is_assembly_script:
            self.write_line("export function ProcessRawBytes(data: DataView|DataAccess, max: number): Message[] {")
            self.indent_level += 1
            self.write_line("if (max === undefined) {")
            self.indent_level += 1
            self.write_line("max = -1;")
            self.indent_level -= 1
            self.write_line("}")
            self.write_line("let da: DataAccess;")
            self.write_line("if (data instanceof DataView) {")
            self.indent_level += 1
            self.write_line("da = new DataAccess(data);")
            self.indent_level -= 1
            self.write_line("}")
            self.write_line("else {")
            self.indent_level += 1
            self.write_line("da = data;")
            self.indent_level -= 1
            self.write_line("}")
        else:
            self.write_line("export function ProcessRawBytes(data: DataView, max: number): Message[] {")
            self.indent_level += 1
            self.write_line("const da = new DataAccess(data);")
            self.write_line("return ProcessRawBytesDA(da, max);")
            self.indent_level -= 1
            self.write_line("}")
            self.write_line()
            self.write_line("export function ProcessRawBytesDA(da: DataAccess, max: number): Message[] {")
            self.indent_level += 1
        self.write_line("const msgList: Message[] = [];")
        self.write_line("if (max == 0) {")
        self.indent_level += 1
        self.write_line("return msgList;")
        self.indent_level -= 1
        self.write_line("}")
        self.write_line("while (!da.isFinished() && (max < 0 || msgList.length < max)) {")
        self.indent_level += 1
        self.write_line(f"const msgType: {self.type_mapping['byte']} = da.getByte();")
        self.write_line(f"let newMsg: Message | null;")
        self.write_line("switch (msgType) {")
        self.indent_level += 1
        self.write_line("case 0:")
        self.indent_level +=1
        self.write_line("return msgList;")
        self.indent_level -=1
        for msg_type in self.protocol.messages:
            self.write_line(f"case MessageType.{msg_type}Type:")
            self.indent_level += 1
            if self.is_assembly_script:
                self.write_line(f"newMsg = {msg_type}.fromBytesDA(da);")
                self.write_line("if (newMsg == null) {")
                self.indent_level += 1
                self.write_line("return msgList;")
                self.indent_level -= 1
                self.write_line("}")
            else:
                self.write_line(f"newMsg = {msg_type}.fromBytes(da);")
            self.write_line("msgList.push(newMsg);")
            self.write_line("break;")
            self.indent_level -= 1
        self.write_line("default:")
        self.indent_level += 1
        if not self.is_assembly_script:
            self.write_line("throw new Error(`Unknown message type: ${msgType}`);")
        else:
            self.write_line("return msgList;")
        self.indent_level -= 1
        self.indent_level -= 1
        self.write_line("}")
        self.indent_level -= 1
        self.write_line("}")
        self.write_line("return msgList;")
        self.indent_level -= 1
        self.write_line("}")
        self.write_line()

        for ename, edata in self.protocol.enums.items():
            self.gen_enum(ename, edata)

        for sname, sdata in self.protocol.structs.items():
            self.gen_struct(sname, sdata)

        for mname, mdata in self.protocol.messages.items():
            self.gen_struct(mname, mdata)

        if not self.is_assembly_script:
            self.write_line("export const MessageTypeMap = new Map<MessageType, { new(): Message }>([");
            self.indent_level += 1
            for mname in self.protocol.messages:
                self.write_line(f"[MessageType.{mname}Type, {mname}],")
            self.indent_level -= 1
            self.write_line("]);")
            self.write_line()

        if self.use_namespace:
            self.indent_level -= 1
            self.write_line("}")

        self.write_line()
        assert self.indent_level == 0

        return "\n".join(self.output)
