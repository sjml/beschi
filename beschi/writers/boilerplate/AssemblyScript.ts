
export class DataAccess {
  data: DataView;
  currentOffset: u32;

  constructor(buffer: DataView) {
    this.currentOffset = 0;
    this.data = buffer;
  }

  isFinished(): boolean {
    return this.currentOffset >= this.data.byteLength;
  }

  getByte(): u8 {
    const ret = this.data.getUint8(this.currentOffset);
    this.currentOffset += 1;
    return ret;
  }

  getBool(): boolean {
    return this.getByte() > 0;
  }

  getInt16(): i16 {
    const ret = this.data.getInt16(this.currentOffset, true);
    this.currentOffset += 2;
    return ret;
  }

  getUint16(): u16 {
    const ret = this.data.getUint16(this.currentOffset, true);
    this.currentOffset += 2;
    return ret;
  }

  getInt32(): i32 {
    const ret = this.data.getInt32(this.currentOffset, true);
    this.currentOffset += 4;
    return ret;
  }

  getUint32(): u32 {
    const ret = this.data.getUint32(this.currentOffset, true);
    this.currentOffset += 4;
    return ret;
  }

  getInt64(): i64 {
    const ret = this.data.getBigInt64(this.currentOffset, true);
    this.currentOffset += 8;
    return ret;
  }

  getUint64(): u64 {
    const ret = this.data.getBigUint64(this.currentOffset, true);
    this.currentOffset += 8;
    return ret;
  }

  getFloat32(): f32 {
    const ret = this.data.getFloat32(this.currentOffset, true);
    this.currentOffset += 4;
    return Math.fround(ret);
  }

  getFloat64(): f64 {
    const ret = this.data.getFloat64(this.currentOffset, true);
    this.currentOffset += 8;
    return ret;
  }

  getString(): string {
    const len = this.get{# STRING_SIZE_TYPE #}();
    const strBuffer = new Uint8Array(this.data.buffer, this.currentOffset, len);
    this.currentOffset += len;
    return String.UTF8.decode(strBuffer, false);
  }


  setByte(val: u8): void {
    this.data.setUint8(this.currentOffset, val);
    this.currentOffset += 1;
  }

  setBool(val: boolean): void {
    this.setByte(val ? 1 : 0);
  }

  setInt16(val: i16): void {
    this.data.setInt16(this.currentOffset, val, true);
    this.currentOffset += 2;
  }

  setUint16(val: u16): void {
    this.data.setUint16(this.currentOffset, val, true);
    this.currentOffset += 2;
  }

  setInt32(val: i32): void {
    this.data.setInt32(this.currentOffset, val, true);
    this.currentOffset += 4;
  }

  setUint32(val: u32): void {
    this.data.setUint32(this.currentOffset, val, true);
    this.currentOffset += 4;
  }

  setInt64(val: i64): void {
    this.data.setBigInt64(this.currentOffset, val, true);
    this.currentOffset += 8;
  }

  setUint64(val: u64): void {
    this.data.setBigUint64(this.currentOffset, val, true);
    this.currentOffset += 8;
  }

  setFloat32(val: f32): void {
    this.data.setFloat32(this.currentOffset, val, true);
    this.currentOffset += 4;
  }

  setFloat64(val: f64): void {
    this.data.setFloat64(this.currentOffset, val, true);
    this.currentOffset += 8;
  }

  setString(val: string): void {
    const strBuffer = String.UTF8.encode(val, false);
    const bufferArray = Uint8Array.wrap(strBuffer);
    this.setByte(strBuffer.byteLength as u8);
    for (let i = 0; i < bufferArray.byteLength; i++) {
      this.setByte(bufferArray[i] as u8);
    }
  }
}

export abstract class Message {
  abstract getMessageType(): MessageType;
  abstract writeBytes(dv: DataView, tag: boolean): void;
  abstract getSizeInBytes(): number;

  static fromBytes(data: DataView): Message | null {
    throw new Error("Cannot read abstract Message from bytes.");
  };
}

export function GetPackedSize(msgList: Message[]): usize {
  let size = 0;
  for (const msg of msgList) {
    size += msg.getSizeInBytes();
  }
  size += msgList.length;
  size += 9;
  return size;
}

export function PackMessages(msgList: Message[], data: DataView): void {
  const da = new DataAccess(data);
  const headerBytes = _textEnc.encode("BSCI");
  const arr = new Uint8Array(da.data.buffer);
  arr.set(headerBytes, da.currentOffset);
  da.currentOffset += headerBytes.byteLength;
  da.setUint32(msgList.length);
  for (const msg of msgList) {
    msg.writeBytes(da, true);
  }
  da.setByte(0);
}

export function UnpackMessages(data: DataView): Message[] {
  const da = new DataAccess(data);
  const headerBuffer = new Uint8Array(da.data.buffer, da.currentOffset, 4);
  da.currentOffset += 4;
  const headerLabel = _textDec.decode(headerBuffer);
  if (headerLabel !== "BSCI") {
    throw new Error("Packed message buffer has invalid header.");
  }
  const msgCount = da.getUint32();
  if (msgCount == 0) {
    return [];
  }
  const msgList = ProcessRawBytes(da, msgCount);
  if (msgList.length == 0) {
    throw new Error("No messages in buffer.");
  }
  if (msgList.length != msgCount) {
    throw new Error("Unexpected number of messages in buffer.");
  }
  return msgList;
}

