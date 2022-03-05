from ..protocol import Protocol, Variable, Struct, NUMERIC_TYPE_SIZES
from ..writer import Writer, TextUtil
from .. import LIB_NAME, LIB_VERSION

LANGUAGE_NAME = "TypeScript"


class TypeScriptWriter(Writer):
    language_name = LANGUAGE_NAME
    default_extension = ".ts"

    def __init__(self, p: Protocol):
        super().__init__(protocol=p, tab="  ")

        for var_type in NUMERIC_TYPE_SIZES:
            if var_type == "bool":
                self.type_mapping[var_type] = "boolean"
            elif var_type in ["int64", "uint64"]:
                self.type_mapping[var_type] = "bigint"
            else:
                # <sigh>, JavaScript
                self.type_mapping[var_type] = "number"

        self.base_serializers: dict[str,str] = {
            "byte": "Uint8",
            "uint16": "Uint16",
            "int16": "Int16",
            "uint32": "Uint32",
            "int32": "Int32",
            "uint64": "BigUint64",
            "int64": "BigInt64",
            "float": "Float32",
            "double": "Float64",
        }

    def deserializer(self, var: Variable, accessor: str):
        var_clean = TextUtil.replace(var.name, [("[", "_"), ("]", "_")])
        if var.is_list:
            self.write_line(f"const {var_clean}_Length = dv.get{self.base_serializers['uint32']}(offset, true);")
            self.write_line(f"offset += {NUMERIC_TYPE_SIZES['uint32']};")
            self.write_line(f"{accessor}{var.name} = Array<{self.type_mapping[var.vartype]}>({var_clean}_Length);")
            idx = self.indent_level
            self.write_line(f"for (let i{idx} = 0; i{idx} < {var_clean}_Length; i{idx}++) {{")
            self.indent_level += 1
            inner = Variable(self.protocol, f"{var.name}[i{idx}]", var.vartype)
            self.deserializer(inner, accessor)
            self.indent_level -= 1
            self.write_line("}")
        elif var.vartype == "string":
            self.write_line(f"const {var_clean}_Length = dv.get{self.base_serializers['uint32']}(offset, true);")
            self.write_line(f"offset += {NUMERIC_TYPE_SIZES['uint32']};")
            self.write_line(f"const {var_clean}_Buffer = new Uint8Array(dv.buffer, offset, {var_clean}_Length);")
            self.write_line(f"offset += {var_clean}_Length;")
            self.write_line(f"{accessor}{var.name} = textDec.decode({var_clean}_Buffer);")
        elif var.vartype == "bool":
            self.write_line(f"{accessor}{var.name} = (dv.getUint8(offset) > 0);")
            self.write_line("offset += 1;")
        elif var.vartype in self.base_serializers:
            pre = ""
            post = ""
            if var.vartype == "float":
                pre = "Math.fround("
                post = ")"
            self.write_line(f"{accessor}{var.name} = {pre}dv.get{self.base_serializers[var.vartype]}(offset{', true' if var.vartype != 'byte' else ''}){post};")
            self.write_line(f"offset += {NUMERIC_TYPE_SIZES[var.vartype]};")
        else:
            self.write_line(f"const {var_clean}_ret = {var.vartype}.FromBytes(dv, offset);")
            self.write_line(f"{accessor}{var.name} = {var_clean}_ret.val;")
            self.write_line(f"offset = {var_clean}_ret.offset;")

    def serializer(self, var: Variable, accessor: str):
        if var.is_list:
            self.write_line(f"dv.set{self.base_serializers['uint32']}(offset, {accessor}{var.name}.length, true);")
            self.write_line(f"offset += {NUMERIC_TYPE_SIZES['uint32']};")
            self.write_line(f"for (let i = 0; i < {accessor}{var.name}.length; i++) {{")
            self.indent_level += 1
            self.write_line(f"let el = {accessor}{var.name}[i];")
            inner = Variable(self.protocol, "el", var.vartype)
            self.serializer(inner, "")
            self.indent_level -= 1
            self.write_line("}")
        elif var.vartype == "string":
            self.write_line(f"const {var.name}_Buffer = textEnc.encode({accessor}{var.name});")
            self.write_line(f"dv.set{self.base_serializers['uint32']}(offset, {var.name}_Buffer.byteLength, true);")
            self.write_line(f"offset += {NUMERIC_TYPE_SIZES['uint32']};")
            self.write_line(f"const {var.name}_Arr = new Uint8Array(dv.buffer);")
            self.write_line(f"{var.name}_Arr.set({var.name}_Buffer, offset);")
            self.write_line(f"offset += {var.name}_Buffer.byteLength;")
        elif var.vartype in NUMERIC_TYPE_SIZES:
            if var.vartype == "bool":
                self.write_line(f"dv.setUint8(offset, {accessor}{var.name} ? 1 : 0);")
                self.write_line("offset += 1;")
            else:
                self.write_line(f"dv.set{self.base_serializers[var.vartype]}(offset, {accessor}{var.name}{', true' if var.vartype != 'byte' else ''});")
                self.write_line(f"offset += {NUMERIC_TYPE_SIZES[var.vartype]};")
        else:
            self.write_line(f"offset = {accessor}{var.name}.WriteBytes(dv, offset);")

    def gen_measurement(self, st: Struct, accessor: str = "") -> tuple[list[str], int]:
        lines: list[str] = []
        accum = 0

        if st.is_simple():
            lines.append(f"return {self.protocol.get_size_of(st.name)};")
        else:
            size_init = "let size: number = 0;"
            lines.append(size_init)

            for var in st.members:
                if var.is_list:
                    accum += NUMERIC_TYPE_SIZES["uint32"]
                    if var.is_simple(True):
                        lines.append(f"size += {accessor}{var.name}.length * {self.protocol.get_size_of(var.vartype)};")
                    elif var.vartype == "string":
                        lines.append(f"for (let {var.name}_i=0; {var.name}_i < {accessor}{var.name}.length; {var.name}_i++) {{")
                        lines.append(f"{self.tab}size += {NUMERIC_TYPE_SIZES['uint32']} + textEnc.encode({accessor}{var.name}[{var.name}_i]).byteLength;")
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
                        accum += NUMERIC_TYPE_SIZES["uint32"]
                        lines.append(f"size += textEnc.encode({accessor}{var.name}).byteLength;")
                    else:
                        clines, caccum = self.gen_measurement(self.protocol.structs[var.vartype], f"{accessor}{var.name}.")
                        if clines[0] == size_init:
                            clines = clines[1:]
                        lines += clines
                        accum += caccum
        return lines, accum

    def gen_struct(self, sname: str, sdata: Struct):
        if sdata.is_message:
            self.write_line("@staticImplements<MessageStatic>()")
            self.write_line(f"export class {sname} implements Message {{")
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
                    default_value = "\"\""
                elif var.vartype in self.protocol.structs:
                    default_value = None
                self.write_line(f"{var.name}: {self.type_mapping[var.vartype]}{f' = {default_value}' if default_value else ''};")
        self.write_line()

        if sdata.is_message:
            self.write_line(f"GetMessageType() : MessageType {{ return MessageType.{sname}Type; }}")
            self.write_line()

            self.write_line("GetSizeInBytes(): number {")
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

        self.write_line(f"static FromBytes(dv: DataView, offset: number): {{val: {sname}, offset: number}} {{")
        self.indent_level += 1
        if sdata.is_message:
            self.write_line("try {")
            self.indent_level += 1
        self.write_line(f"const n{sname} = new {self.type_mapping[sname]}();")
        [self.deserializer(mem, f"n{sname}.") for mem in sdata.members]
        self.write_line(f"return {{val: n{sname}, offset: offset}};")
        if sdata.is_message:
            self.indent_level -= 1
            self.write_line("}")
            self.write_line("catch (RangeError) {")
            self.indent_level += 1
            self.write_line("return {val: null, offset: offset};")
            self.indent_level -= 1
            self.write_line("}")
        self.indent_level -= 1
        self.write_line("}")

        if sdata.is_message:
            self.write_line("WriteBytes(dv: DataView, tag: boolean, offset: number) : number {")
            self.indent_level += 1
            self.write_line("if (tag) {")
            self.indent_level += 1
            self.write_line(f"dv.setUint8(offset, MessageType.{sname}Type);")
            self.write_line("offset += 1;")
            self.indent_level -= 1
            self.write_line("}")
        else:
            self.write_line("WriteBytes(dv: DataView, offset: number) : number {")
            self.indent_level += 1
        [self.serializer(mem, "this.") for mem in sdata.members]
        self.write_line("return offset;")
        self.indent_level -= 1
        self.write_line("}")
        self.write_line()

        self.indent_level -= 1
        self.write_line("}")
        self.write_line()

    def generate(self) -> str:
        self.output = []

        self.write_line(f"// This file was automatically generated by {LIB_NAME} v{LIB_VERSION}.")
        self.write_line( "// <https://github.com/sjml/beschi>")
        self.write_line(f"// Do not edit directly.")
        self.write_line()

        self.write_line("const textDec = new TextDecoder('utf-8');")
        self.write_line("const textEnc = new TextEncoder();")
        self.write_line()

        self.write_line("export enum MessageType {")
        self.indent_level += 1
        [self.write_line(f"{k}Type = {i+1},") for i, k in enumerate(self.protocol.messages)]
        self.indent_level -= 1
        self.write_line("}")
        self.write_line()

        self.write_line("export interface Message {")
        self.indent_level += 1
        self.write_line("GetMessageType() : MessageType;")
        self.write_line("WriteBytes(dv: DataView, tag: boolean, offset: number) : number;")
        self.write_line("GetSizeInBytes() : number;")
        self.indent_level -= 1
        self.write_line("}")
        self.write_line("export interface MessageStatic {")
        self.indent_level += 1
        self.write_line("new(): Message;")
        self.write_line("FromBytes(dv: DataView, offset: number): {val: Message | null, offset: number};")
        self.indent_level -= 1
        self.write_line("}")
        self.write_line("function staticImplements<T>() {")
        self.indent_level += 1
        self.write_line("return (constructor: T) => {}")
        self.indent_level -= 1
        self.write_line("}")
        self.write_line()

        self.write_line("export function ProcessRawBytes(dv: DataView, offset: number): {vals: Message[], offset: number} {")
        self.indent_level += 1
        self.write_line("const msgList: Message[] = [];")
        self.write_line("while (offset < dv.byteLength) {")
        self.indent_level += 1
        self.write_line("const msgType: number = dv.getUint8(offset);")
        self.write_line("offset += 1;")
        self.write_line("let msgRet: any = null;")
        self.write_line("switch (msgType) {")
        self.indent_level += 1
        for msg_type in self.protocol.messages:
            self.write_line(f"case MessageType.{msg_type}Type:")
            self.indent_level += 1
            self.write_line(f"msgRet = {msg_type}.FromBytes(dv, offset);")
            self.write_line("break;")
            self.indent_level -= 1
        self.write_line("default:")
        self.indent_level += 1
        self.write_line("msgRet = {val: null, offset: offset};")
        self.write_line("break;")
        self.indent_level -= 1
        self.indent_level -= 1
        self.write_line("}")
        self.write_line("offset = msgRet.offset;")
        self.write_line("msgList.push(msgRet.val);")
        self.write_line("if (msgRet.val == null) {")
        self.indent_level += 1
        self.write_line("break;")
        self.indent_level -= 1
        self.write_line("}")
        self.indent_level -= 1
        self.write_line("}")
        self.write_line("return {vals: msgList, offset: offset};")
        self.indent_level -= 1
        self.write_line("}")
        self.write_line()

        for sname, sdata in self.protocol.structs.items():
            self.gen_struct(sname, sdata)

        for mname, mdata in self.protocol.messages.items():
            self.gen_struct(mname, mdata)

        self.write_line()
        assert self.indent_level == 0

        return "\n".join(self.output)
