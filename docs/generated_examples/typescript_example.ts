// This file was automatically generated by Beschi v0.1.11
// <https://github.com/sjml/beschi>
// Do not edit directly.


const _textDec = new TextDecoder('utf-8');
const _textEnc = new TextEncoder();

export class DataAccess {
    buffer: DataView;
    currentOffset: number;

    constructor(buffer: ArrayBuffer|DataView) {
        this.currentOffset = 0;
        if (buffer instanceof ArrayBuffer) {
            this.buffer = new DataView(buffer);
        }
        else {
            this.buffer = buffer;
        }
    }

    IsFinished(): boolean {
        return this.currentOffset >= this.buffer.byteLength;
    }

    GetByte(): number {
        const ret = this.buffer.getUint8(this.currentOffset);
        this.currentOffset += 1;
        return ret;
    }

    GetBool(): boolean {
        return this.GetByte() > 0;
    }

    GetInt16(): number {
        const ret = this.buffer.getInt16(this.currentOffset, true);
        this.currentOffset += 2;
        return ret;
    }

    GetUint16(): number {
        const ret = this.buffer.getUint16(this.currentOffset, true);
        this.currentOffset += 2;
        return ret;
    }

    GetInt32(): number {
        const ret = this.buffer.getInt32(this.currentOffset, true);
        this.currentOffset += 4;
        return ret;
    }

    GetUint32(): number {
        const ret = this.buffer.getUint32(this.currentOffset, true);
        this.currentOffset += 4;
        return ret;
    }

    GetInt64(): bigint {
        const ret = this.buffer.getBigInt64(this.currentOffset, true);
        this.currentOffset += 8;
        return ret;
    }

    GetUint64(): bigint {
        const ret = this.buffer.getBigUint64(this.currentOffset, true);
        this.currentOffset += 8;
        return ret;
    }

    GetFloat32(): number {
        const ret = this.buffer.getFloat32(this.currentOffset, true);
        this.currentOffset += 4;
        return Math.fround(ret);
    }

    GetFloat64(): number {
        const ret = this.buffer.getFloat64(this.currentOffset, true);
        this.currentOffset += 8;
        return ret;
    }

    GetString(): string {
        const len = this.GetByte();
        const strBuffer = new Uint8Array(this.buffer.buffer, this.currentOffset, len);
        this.currentOffset += len;
        return _textDec.decode(strBuffer);
    }


    SetByte(val: number) {
        this.buffer.setUint8(this.currentOffset, val);
        this.currentOffset += 1;
    }

    SetBool(val: boolean) {
        this.SetByte(val ? 1 : 0);
    }

    SetInt16(val: number) {
        this.buffer.setInt16(this.currentOffset, val, true);
        this.currentOffset += 2;
    }

    SetUint16(val: number) {
        this.buffer.setUint16(this.currentOffset, val, true);
        this.currentOffset += 2;
    }

    SetInt32(val: number) {
        this.buffer.setInt32(this.currentOffset, val, true);
        this.currentOffset += 4;
    }

    SetUint32(val: number) {
        this.buffer.setUint32(this.currentOffset, val, true);
        this.currentOffset += 4;
    }

    SetInt64(val: bigint) {
        this.buffer.setBigInt64(this.currentOffset, val, true);
        this.currentOffset += 8;
    }

    SetUint64(val: bigint) {
        this.buffer.setBigUint64(this.currentOffset, val, true);
        this.currentOffset += 8;
    }

    SetFloat32(val: number) {
        this.buffer.setFloat32(this.currentOffset, val, true);
        this.currentOffset += 4;
    }

    SetFloat64(val: number) {
        this.buffer.setFloat64(this.currentOffset, val, true);
        this.currentOffset += 8;
    }

    SetString(val: string) {
        const strBuffer = _textEnc.encode(val);
        this.SetByte(strBuffer.byteLength);
        const arr = new Uint8Array(this.buffer.buffer);
        arr.set(strBuffer, this.currentOffset);
        this.currentOffset += strBuffer.byteLength;
    }
}
export enum MessageType {
  Vector3MessageType = 1,
  NewCharacterMessageType = 2,
  CharacterJoinedTeamType = 3,
}

export interface Message {
  GetMessageType(): MessageType;
  WriteBytes(dv: DataView, tag: boolean): void;
  GetSizeInBytes(): number;
}
export interface MessageStatic {
  new(): Message;
  FromBytes(dv: DataView): Message | null;
}
function staticImplements<T>() {
  return (constructor: T) => {}
}

export function ProcessRawBytes(dv: DataView): Message[] {
  const da = new DataAccess(dv);
  const msgList: Message[] = [];
  while (!da.IsFinished()) {
    const msgType: number = da.GetByte();
    switch (msgType) {
      case MessageType.Vector3MessageType:
        msgList.push(Vector3Message.FromBytes(da));
        break;
      case MessageType.NewCharacterMessageType:
        msgList.push(NewCharacterMessage.FromBytes(da));
        break;
      case MessageType.CharacterJoinedTeamType:
        msgList.push(CharacterJoinedTeam.FromBytes(da));
        break;
      default:
        msgList.push(null);
        break;
    }
    if (msgList[msgList.length - 1] == null) {
      break;
    }
  }
  return msgList;
}

export class Color {
  red: number = 0;
  green: number = 0;
  blue: number = 0;
  alpha: number = 0;

  static FromBytes(da: DataAccess): Color {
    const nColor = new Color();
    nColor.red = da.GetFloat32();
    nColor.green = da.GetFloat32();
    nColor.blue = da.GetFloat32();
    nColor.alpha = da.GetFloat32();
    return nColor;
  }

  WriteBytes(da: DataAccess) {
    da.SetFloat32(this.red);
    da.SetFloat32(this.green);
    da.SetFloat32(this.blue);
    da.SetFloat32(this.alpha);
  }

}

export class Spectrum {
  defaultColor: Color = new Color();
  colors: Color[] = [];

  static FromBytes(da: DataAccess): Spectrum {
    const nSpectrum = new Spectrum();
    nSpectrum.defaultColor = Color.FromBytes(da);
    const colors_Length = da.GetUint16();
    nSpectrum.colors = Array<Color>(colors_Length);
    for (let i2 = 0; i2 < colors_Length; i2++) {
      nSpectrum.colors[i2] = Color.FromBytes(da);
    }
    return nSpectrum;
  }

  WriteBytes(da: DataAccess) {
    this.defaultColor.WriteBytes(da);
    da.SetUint16(this.colors.length);
    for (let i = 0; i < this.colors.length; i++) {
      let el = this.colors[i];
      el.WriteBytes(da);
    }
  }

}

@staticImplements<MessageStatic>()
export class Vector3Message implements Message {
  x: number = 0;
  y: number = 0;
  z: number = 0;

  GetMessageType() : MessageType { return MessageType.Vector3MessageType; }

  GetSizeInBytes(): number {
    return 12;
  }

  static FromBytes(data: DataView|DataAccess): Vector3Message {
    let da: DataAccess = null;
    if (data instanceof DataView) {
      da = new DataAccess(data);
    }
    else {
      da = data;
    }
    try {
      const nVector3Message = new Vector3Message();
      nVector3Message.x = da.GetFloat32();
      nVector3Message.y = da.GetFloat32();
      nVector3Message.z = da.GetFloat32();
      return nVector3Message;
    }
    catch (RangeError) {
      return null;
    }
  }

  WriteBytes(data: DataView|DataAccess, tag: boolean): void {
    let da: DataAccess = null;
    if (data instanceof DataView) {
      da = new DataAccess(data);
    }
    else {
      da = data;
    }
    if (tag) {
      da.SetByte(MessageType.Vector3MessageType);
    }
    da.SetFloat32(this.x);
    da.SetFloat32(this.y);
    da.SetFloat32(this.z);
  }

}

@staticImplements<MessageStatic>()
export class NewCharacterMessage implements Message {
  id: bigint = 0n;
  characterName: string = "";
  strength: number = 0;
  intelligence: number = 0;
  dexterity: number = 0;
  goldInWallet: number = 0;
  nicknames: string[] = [];

  GetMessageType() : MessageType { return MessageType.NewCharacterMessageType; }

  GetSizeInBytes(): number {
    let size: number = 0;
    size += _textEnc.encode(this.characterName).byteLength;
    for (let nicknames_i=0; nicknames_i < this.nicknames.length; nicknames_i++) {
      size += 1 + _textEnc.encode(this.nicknames[nicknames_i]).byteLength;
    }
    size += 21;
    return size;
  }

  static FromBytes(data: DataView|DataAccess): NewCharacterMessage {
    let da: DataAccess = null;
    if (data instanceof DataView) {
      da = new DataAccess(data);
    }
    else {
      da = data;
    }
    try {
      const nNewCharacterMessage = new NewCharacterMessage();
      nNewCharacterMessage.id = da.GetUint64();
      nNewCharacterMessage.characterName = da.GetString();
      nNewCharacterMessage.strength = da.GetUint16();
      nNewCharacterMessage.intelligence = da.GetUint16();
      nNewCharacterMessage.dexterity = da.GetUint16();
      nNewCharacterMessage.goldInWallet = da.GetUint32();
      const nicknames_Length = da.GetUint16();
      nNewCharacterMessage.nicknames = Array<string>(nicknames_Length);
      for (let i3 = 0; i3 < nicknames_Length; i3++) {
        nNewCharacterMessage.nicknames[i3] = da.GetString();
      }
      return nNewCharacterMessage;
    }
    catch (RangeError) {
      return null;
    }
  }

  WriteBytes(data: DataView|DataAccess, tag: boolean): void {
    let da: DataAccess = null;
    if (data instanceof DataView) {
      da = new DataAccess(data);
    }
    else {
      da = data;
    }
    if (tag) {
      da.SetByte(MessageType.NewCharacterMessageType);
    }
    da.SetUint64(this.id);
    da.SetString(this.characterName);
    da.SetUint16(this.strength);
    da.SetUint16(this.intelligence);
    da.SetUint16(this.dexterity);
    da.SetUint32(this.goldInWallet);
    da.SetUint16(this.nicknames.length);
    for (let i = 0; i < this.nicknames.length; i++) {
      let el = this.nicknames[i];
      da.SetString(el);
    }
  }

}

@staticImplements<MessageStatic>()
export class CharacterJoinedTeam implements Message {
  characterID: bigint = 0n;
  teamName: string = "";
  teamColors: Color[] = [];

  GetMessageType() : MessageType { return MessageType.CharacterJoinedTeamType; }

  GetSizeInBytes(): number {
    let size: number = 0;
    size += _textEnc.encode(this.teamName).byteLength;
    size += this.teamColors.length * 16;
    size += 11;
    return size;
  }

  static FromBytes(data: DataView|DataAccess): CharacterJoinedTeam {
    let da: DataAccess = null;
    if (data instanceof DataView) {
      da = new DataAccess(data);
    }
    else {
      da = data;
    }
    try {
      const nCharacterJoinedTeam = new CharacterJoinedTeam();
      nCharacterJoinedTeam.characterID = da.GetUint64();
      nCharacterJoinedTeam.teamName = da.GetString();
      const teamColors_Length = da.GetUint16();
      nCharacterJoinedTeam.teamColors = Array<Color>(teamColors_Length);
      for (let i3 = 0; i3 < teamColors_Length; i3++) {
        nCharacterJoinedTeam.teamColors[i3] = Color.FromBytes(da);
      }
      return nCharacterJoinedTeam;
    }
    catch (RangeError) {
      return null;
    }
  }

  WriteBytes(data: DataView|DataAccess, tag: boolean): void {
    let da: DataAccess = null;
    if (data instanceof DataView) {
      da = new DataAccess(data);
    }
    else {
      da = data;
    }
    if (tag) {
      da.SetByte(MessageType.CharacterJoinedTeamType);
    }
    da.SetUint64(this.characterID);
    da.SetString(this.teamName);
    da.SetUint16(this.teamColors.length);
    for (let i = 0; i < this.teamColors.length; i++) {
      let el = this.teamColors[i];
      el.WriteBytes(da);
    }
  }

}

