
export class DataAccess {
  data: DataView;
  currentOffset: u32;
  hasError: bool;

  constructor(buffer: DataView) {
    this.currentOffset = 0;
    this.data = buffer;
    this.hasError = false;
  }

  isFinished(): bool {
    return this.currentOffset > (this.data.byteLength as u32);
  }

  getByte(): u8 {
    if (this.currentOffset + 1 > (this.data.byteLength as u32)) {
        this.hasError = true;
        return 0;
    }
    const ret = this.data.getUint8(this.currentOffset);
    this.currentOffset += 1;
    return ret;
  }

  getBool(): bool {
    return this.getByte() > 0;
  }

  getInt16(): i16 {
    if (this.currentOffset + 2 > (this.data.byteLength as u32)) {
        this.hasError = true;
        return 0;
    }
    const ret = this.data.getInt16(this.currentOffset, true);
    this.currentOffset += 2;
    return ret;
  }

  getUint16(): u16 {
    if (this.currentOffset + 2 > (this.data.byteLength as u32)) {
        this.hasError = true;
        return 0;
    }
    const ret = this.data.getUint16(this.currentOffset, true);
    this.currentOffset += 2;
    return ret;
  }

  getInt32(): i32 {
    if (this.currentOffset + 4 > (this.data.byteLength as u32)) {
        this.hasError = true;
        return 0;
    }
    const ret = this.data.getInt32(this.currentOffset, true);
    this.currentOffset += 4;
    return ret;
  }

  getUint32(): u32 {
    if (this.currentOffset + 4 > (this.data.byteLength as u32)) {
        this.hasError = true;
        return 0;
    }
    const ret = this.data.getUint32(this.currentOffset, true);
    this.currentOffset += 4;
    return ret;
  }

  getInt64(): i64 {
    if (this.currentOffset + 8 > (this.data.byteLength as u32)) {
        this.hasError = true;
        return 0;
    }
    const ret = this.data.getInt64(this.currentOffset, true);
    this.currentOffset += 8;
    return ret;
  }

  getUint64(): u64 {
    if (this.currentOffset + 8 > (this.data.byteLength as u32)) {
        this.hasError = true;
        return 0;
    }
    const ret = this.data.getUint64(this.currentOffset, true);
    this.currentOffset += 8;
    return ret;
  }

  getFloat32(): f32 {
    if (this.currentOffset + 4 > (this.data.byteLength as u32)) {
        this.hasError = true;
        return 0;
    }
    const ret = this.data.getFloat32(this.currentOffset, true);
    this.currentOffset += 4;
    return ret;
  }

  getFloat64(): f64 {
    if (this.currentOffset + 8 > (this.data.byteLength as u32)) {
        this.hasError = true;
        return 0;
    }
    const ret = this.data.getFloat64(this.currentOffset, true);
    this.currentOffset += 8;
    return ret;
  }

  getString(): string {
    const len = this.get{# STRING_SIZE_TYPE #}();
    if (this.hasError) {
        return "";
    }
    if (this.currentOffset + len > (this.data.byteLength as u32)) {
        this.hasError = true;
        return "";
    }
    const strBuffer = new Uint8Array(len);
    for (let i = 0; i < strBuffer.byteLength; i++) {
        strBuffer[i] = this.getByte();
    }
    return String.UTF8.decode(strBuffer.buffer, false);
  }


  setByte(val: u8): void {
    if (this.currentOffset + 1 > (this.data.byteLength as u32)) {
        this.hasError = true;
        return;
    }
    this.data.setUint8(this.currentOffset, val);
    this.currentOffset += 1;
  }

  setBool(val: bool): void {
    this.setByte(val ? 1 : 0);
  }

  setInt16(val: i16): void {
    if (this.currentOffset + 2 > (this.data.byteLength as u32)) {
        this.hasError = true;
        return;
    }
    this.data.setInt16(this.currentOffset, val, true);
    this.currentOffset += 2;
  }

  setUint16(val: u16): void {
    if (this.currentOffset + 2 > (this.data.byteLength as u32)) {
        this.hasError = true;
        return;
    }
    this.data.setUint16(this.currentOffset, val, true);
    this.currentOffset += 2;
  }

  setInt32(val: i32): void {
    if (this.currentOffset + 4 > (this.data.byteLength as u32)) {
        this.hasError = true;
        return;
    }
    this.data.setInt32(this.currentOffset, val, true);
    this.currentOffset += 4;
  }

  setUint32(val: u32): void {
    if (this.currentOffset + 4 > (this.data.byteLength as u32)) {
        this.hasError = true;
        return;
    }
    this.data.setUint32(this.currentOffset, val, true);
    this.currentOffset += 4;
  }

  setInt64(val: i64): void {
    if (this.currentOffset + 8 > (this.data.byteLength as u32)) {
        this.hasError = true;
        return;
    }
    this.data.setInt64(this.currentOffset, val, true);
    this.currentOffset += 8;
  }

  setUint64(val: u64): void {
    if (this.currentOffset + 8 > (this.data.byteLength as u32)) {
        this.hasError = true;
        return;
    }
    this.data.setUint64(this.currentOffset, val, true);
    this.currentOffset += 8;
  }

  setFloat32(val: f32): void {
    if (this.currentOffset + 4 > (this.data.byteLength as u32)) {
        this.hasError = true;
        return;
    }
    this.data.setFloat32(this.currentOffset, val, true);
    this.currentOffset += 4;
  }

  setFloat64(val: f64): void {
    if (this.currentOffset + 8 > (this.data.byteLength as u32)) {
        this.hasError = true;
        return;
    }
    this.data.setFloat64(this.currentOffset, val, true);
    this.currentOffset += 8;
  }

  setString(val: string): void {
    const strBuffer = String.UTF8.encode(val, false);
    const bufferArray = Uint8Array.wrap(strBuffer);
    this.set{# STRING_SIZE_TYPE #}(strBuffer.byteLength as {# NATIVE_STRING_SIZE_TYPE #});
    if (this.hasError) {
        return;
    }
    if (this.currentOffset + bufferArray.byteLength > (this.data.byteLength as u32)) {
        this.hasError = true;
        return;
    }
    for (let i = 0; i < bufferArray.byteLength; i++) {
      this.setByte(bufferArray[i] as u8);
    }
  }
}

export abstract class Message {
  abstract getMessageType(): MessageType;
  abstract writeBytes(dv: DataView, tag: bool): bool;
  abstract writeBytesDA(da: DataAccess, tag: bool): bool;
  abstract getSizeInBytes(): usize;

  static fromBytes(data: DataView): Message | null {
    const da = new DataAccess(data);
    return this.fromBytesDA(da);
  };

  static fromBytesDA(data: DataAccess): Message | null {
    const msgList = ProcessRawBytes(data, 1);
    if (msgList.length == 0) {
      return null;
    }
    return msgList[0];
  }
}

export function GetPackedSize(msgList: Message[]): usize {
  let size: usize = 0;
  for (let i = 0; i < msgList.length; i++) {
    size += msgList[i].getSizeInBytes();
  }
  size += msgList.length;
  size += 9;
  return size;
}

export function PackMessages(msgList: Message[], data: DataView): void {
  const da = new DataAccess(data);
  const headerBytes = String.UTF8.encode("BSCI", false);
  const arr = Uint8Array.wrap(headerBytes);
  for (let i = 0; i < arr.byteLength; i++) {
    da.setByte(arr[i] as u8);
    if (da.hasError) { return; }
}
  da.setUint32(msgList.length);
  if (da.hasError) { return; }
  for (let i = 0; i < msgList.length; i++) {
      msgList[i].writeBytesDA(da, true);
      if (da.hasError) { return; }
  }
  da.setByte(0);
}

export function UnpackMessages(data: DataView): Message[] {
  const da = new DataAccess(data);
  if (da.data.byteLength < 12) {
    throw new Error("Packed message buffer is too short.");
  }
  const headerBuffer = new Uint8Array(4);
  for (let i = 0; i < 4; i++) {
    headerBuffer[i] = da.getByte();
  }
  const headerLabel = String.UTF8.decode(headerBuffer.buffer, false);
  if (headerLabel !== "BSCI") {
    throw new Error("Packed message buffer has invalid header: " + headerLabel);
  }
  const msgCount = da.getUint32();
  if (msgCount == 0) {
    return [];
  }
  const dv = new DataView(data.buffer, da.currentOffset, data.byteLength - da.currentOffset);
  const msgList = ProcessRawBytes(dv, msgCount);
  if (msgList.length == 0) {
    throw new Error("No messages in buffer.");
  }
  if (msgList.length != msgCount) {
    throw new Error("Unexpected number of messages in buffer.");
  }
  return msgList;
}

