
const _textDec = new TextDecoder('utf-8');
const _textEnc = new TextEncoder();

export class DataAccess {
  data: DataView;
  currentOffset: number;

  constructor(buffer: ArrayBuffer|DataView) {
    this.currentOffset = 0;
    if (buffer instanceof ArrayBuffer) {
      this.data = new DataView(buffer);
    }
    else {
      this.data = buffer;
    }
  }

  isFinished(): boolean {
    return this.currentOffset >= this.data.byteLength;
  }

  getByte(): number {
    const ret = this.data.getUint8(this.currentOffset);
    this.currentOffset += 1;
    return ret;
  }

  getBool(): boolean {
    return this.getByte() > 0;
  }

  getInt16(): number {
    const ret = this.data.getInt16(this.currentOffset, true);
    this.currentOffset += 2;
    return ret;
  }

  getUint16(): number {
    const ret = this.data.getUint16(this.currentOffset, true);
    this.currentOffset += 2;
    return ret;
  }

  getInt32(): number {
    const ret = this.data.getInt32(this.currentOffset, true);
    this.currentOffset += 4;
    return ret;
  }

  getUint32(): number {
    const ret = this.data.getUint32(this.currentOffset, true);
    this.currentOffset += 4;
    return ret;
  }

  getInt64(): bigint {
    const ret = this.data.getBigInt64(this.currentOffset, true);
    this.currentOffset += 8;
    return ret;
  }

  getUint64(): bigint {
    const ret = this.data.getBigUint64(this.currentOffset, true);
    this.currentOffset += 8;
    return ret;
  }

  getFloat32(): number {
    const ret = this.data.getFloat32(this.currentOffset, true);
    this.currentOffset += 4;
    return Math.fround(ret);
  }

  getFloat64(): number {
    const ret = this.data.getFloat64(this.currentOffset, true);
    this.currentOffset += 8;
    return ret;
  }

  getString(): string {
    const len = this.get{# STRING_SIZE_TYPE #}();
    const strBuffer = new Uint8Array(this.data.buffer, this.currentOffset, len);
    this.currentOffset += len;
    return _textDec.decode(strBuffer);
  }


  setByte(val: number) {
    this.data.setUint8(this.currentOffset, val);
    this.currentOffset += 1;
  }

  setBool(val: boolean): void {
    this.setByte(val ? 1 : 0);
  }

  setInt16(val: number): void {
    this.data.setInt16(this.currentOffset, val, true);
    this.currentOffset += 2;
  }

  setUint16(val: number): void {
    this.data.setUint16(this.currentOffset, val, true);
    this.currentOffset += 2;
  }

  setInt32(val: number): void {
    this.data.setInt32(this.currentOffset, val, true);
    this.currentOffset += 4;
  }

  setUint32(val: number): void {
    this.data.setUint32(this.currentOffset, val, true);
    this.currentOffset += 4;
  }

  setInt64(val: bigint): void {
    this.data.setBigInt64(this.currentOffset, val, true);
    this.currentOffset += 8;
  }

  setUint64(val: bigint): void {
    this.data.setBigUint64(this.currentOffset, val, true);
    this.currentOffset += 8;
  }

  setFloat32(val: number): void {
    this.data.setFloat32(this.currentOffset, val, true);
    this.currentOffset += 4;
  }

  setFloat64(val: number): void {
    this.data.setFloat64(this.currentOffset, val, true);
    this.currentOffset += 8;
  }

  setString(val: string): void {
    const strBuffer = _textEnc.encode(val);
    this.set{# STRING_SIZE_TYPE #}(strBuffer.byteLength);
    const arr = new Uint8Array(this.data.buffer, this.data.byteOffset, this.data.byteLength);
    arr.set(strBuffer, this.currentOffset);
    this.currentOffset += strBuffer.byteLength;
  }
}

export abstract class Message {
  abstract getMessageType(): MessageType;
  abstract writeBytes(dv: DataView|DataAccess, tag: boolean): void;
  abstract getSizeInBytes(): number;

  static fromBytes(data: DataView|DataAccess|ArrayBuffer): Message | null {
    throw new Error("Cannot read abstract Message from bytes.");
  };
}

export function GetPackedSize(msgList: Message[]): number {
  let size = 0;
  for (const msg of msgList) {
    size += msg.getSizeInBytes();
  }
  size += msgList.length;
  size += 9;
  return size;
}

export function PackMessages(msgList: Message[], data: DataView|DataAccess): void {
  let da: DataAccess;
  if (data instanceof DataView) {
    da = new DataAccess(data);
  }
  else {
    da = data;
  }
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

export function UnpackMessages(data: DataView|DataAccess): Message[] {
  let da: DataAccess;
  if (data instanceof DataView) {
    da = new DataAccess(data);
  }
  else {
    da = data;
  }
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

