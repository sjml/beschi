// This file was automatically generated by Beschi v0.3.0
// <https://github.com/sjml/beschi>
// Do not edit directly.


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
    const len = this.getByte();
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
    this.setByte(strBuffer.byteLength as u8);
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

export enum MessageType {
  Vector3MessageType = 1,
  NewCharacterMessageType = 2,
  CharacterJoinedTeamType = 3,
  _Unknown,
}

export function ProcessRawBytes(data: DataView, max: number): Message[] {
  const da = new DataAccess(data);
  return ProcessRawBytesDA(da, max);
}

export function ProcessRawBytesDA(da: DataAccess, max: number): Message[] {
  const msgList: Message[] = [];
  if (max == 0) {
    return msgList;
  }
  while (!da.isFinished() && (max < 0 || msgList.length < max)) {
    const msgType: u8 = da.getByte();
    let newMsg: Message | null;
    switch (msgType) {
      case 0:
        return msgList;
      case MessageType.Vector3MessageType:
        newMsg = Vector3Message.fromBytesDA(da);
        if (newMsg == null) {
          return msgList;
        }
        msgList.push(newMsg);
        break;
      case MessageType.NewCharacterMessageType:
        newMsg = NewCharacterMessage.fromBytesDA(da);
        if (newMsg == null) {
          return msgList;
        }
        msgList.push(newMsg);
        break;
      case MessageType.CharacterJoinedTeamType:
        newMsg = CharacterJoinedTeam.fromBytesDA(da);
        if (newMsg == null) {
          return msgList;
        }
        msgList.push(newMsg);
        break;
      default:
        return msgList;
    }
  }
  return msgList;
}

export enum CharacterClass {
  Fighter = 0,
  Wizard = 1,
  Rogue = 2,
  Cleric = 3,
  _Unknown,
}

export enum TeamRole {
  Minion = 256,
  Ally = 512,
  Leader = 1024,
  Traitor = -1,
  _Unknown,
}

export class Color {
  red: f32 = 0;
  green: f32 = 0;
  blue: f32 = 0;
  alpha: f32 = 0;

  static fromBytes(da: DataAccess): Color | null {
    const nColor = new Color();
    nColor.red = da.getFloat32();
    if (da.hasError) { return null; }
    nColor.green = da.getFloat32();
    if (da.hasError) { return null; }
    nColor.blue = da.getFloat32();
    if (da.hasError) { return null; }
    nColor.alpha = da.getFloat32();
    if (da.hasError) { return null; }
    return nColor;
  }

  writeBytes(da: DataAccess): bool {
    da.setFloat32(this.red);
    if (da.hasError) { return false; }
    da.setFloat32(this.green);
    if (da.hasError) { return false; }
    da.setFloat32(this.blue);
    if (da.hasError) { return false; }
    da.setFloat32(this.alpha);
    if (da.hasError) { return false; }
    return true;
  }
}

export class Spectrum {
  defaultColor: Color = new Color();
  colors: Color[] = [];

  static fromBytes(da: DataAccess): Spectrum | null {
    const nSpectrum = new Spectrum();
    const _defaultColor = Color.fromBytes(da);
    if (_defaultColor == null) {
      return null;
    }
    else {
      nSpectrum.defaultColor = _defaultColor;
    }
    const colors_Length = da.getUint16();
    if (da.hasError) { return null; }
    nSpectrum.colors = new Array<Color>(colors_Length);
    for (let i2: u16 = 0; i2 < colors_Length; i2++) {
      const _colors_i2_ = Color.fromBytes(da);
      if (_colors_i2_ == null) {
        return null;
      }
      else {
        nSpectrum.colors[i2] = _colors_i2_;
      }
    }
    return nSpectrum;
  }

  writeBytes(da: DataAccess): bool {
    if (!this.defaultColor.writeBytes(da)) { return false; };
    da.setUint16(this.colors.length as u16);
    if (da.hasError) { return false; }
    for (let i = 0; i < this.colors.length; i++) {
      let el = this.colors[i];
      if (!el.writeBytes(da)) { return false; };
    }
    return true;
  }
}

export class Vector3Message extends Message {
  x: f32 = 0;
  y: f32 = 0;
  z: f32 = 0;

  getMessageType() : MessageType { return MessageType.Vector3MessageType; }

  getSizeInBytes(): usize {
    return 12;
  }

  static override fromBytes(data: DataView): Vector3Message | null {
    const da = new DataAccess(data);
    return Vector3Message.fromBytesDA(da);
  }

  static override fromBytesDA(da: DataAccess): Vector3Message | null {
    const nVector3Message = new Vector3Message();
    nVector3Message.x = da.getFloat32();
    if (da.hasError) { return null; }
    nVector3Message.y = da.getFloat32();
    if (da.hasError) { return null; }
    nVector3Message.z = da.getFloat32();
    if (da.hasError) { return null; }
    return nVector3Message;
  }

  writeBytes(data: DataView, tag: boolean): bool {
    const da = new DataAccess(data);
    return this.writeBytesDA(da, tag);
  }

  writeBytesDA(da: DataAccess, tag: boolean): bool {
    if (tag) {
      da.setByte(MessageType.Vector3MessageType as u8);
      if (da.hasError) { return false; }
    }
    da.setFloat32(this.x);
    if (da.hasError) { return false; }
    da.setFloat32(this.y);
    if (da.hasError) { return false; }
    da.setFloat32(this.z);
    if (da.hasError) { return false; }
    return true;
  }
}

export class NewCharacterMessage extends Message {
  id: u64 = 0;
  characterName: string = "";
  job: CharacterClass = CharacterClass.Fighter;
  strength: u16 = 0;
  intelligence: u16 = 0;
  dexterity: u16 = 0;
  wisdom: u16 = 0;
  goldInWallet: u32 = 0;
  nicknames: string[] = [];

  getMessageType() : MessageType { return MessageType.NewCharacterMessageType; }

  getSizeInBytes(): usize {
    let size: usize = 0;
    size += String.UTF8.encode(this.characterName, false).byteLength;
    for (let nicknames_i=0; nicknames_i < this.nicknames.length; nicknames_i++) {
      size += 1 + String.UTF8.encode(this.nicknames[nicknames_i], false).byteLength;
    }
    size += 24;
    return size;
  }

  static override fromBytes(data: DataView): NewCharacterMessage | null {
    const da = new DataAccess(data);
    return NewCharacterMessage.fromBytesDA(da);
  }

  static override fromBytesDA(da: DataAccess): NewCharacterMessage | null {
    const nNewCharacterMessage = new NewCharacterMessage();
    nNewCharacterMessage.id = da.getUint64();
    if (da.hasError) { return null; }
    nNewCharacterMessage.characterName = da.getString();
    if (da.hasError) { return null; }
    let _job = da.getByte();
    if (da.hasError) { return null; }
    if (_job < 0 || _job >= (CharacterClass._Unknown as u8)) {
      _job = CharacterClass._Unknown as u8;
    }
    nNewCharacterMessage.job = _job;
    nNewCharacterMessage.strength = da.getUint16();
    if (da.hasError) { return null; }
    nNewCharacterMessage.intelligence = da.getUint16();
    if (da.hasError) { return null; }
    nNewCharacterMessage.dexterity = da.getUint16();
    if (da.hasError) { return null; }
    nNewCharacterMessage.wisdom = da.getUint16();
    if (da.hasError) { return null; }
    nNewCharacterMessage.goldInWallet = da.getUint32();
    if (da.hasError) { return null; }
    const nicknames_Length = da.getUint16();
    if (da.hasError) { return null; }
    nNewCharacterMessage.nicknames = new Array<string>(nicknames_Length);
    for (let i2: u16 = 0; i2 < nicknames_Length; i2++) {
      nNewCharacterMessage.nicknames[i2] = da.getString();
      if (da.hasError) { return null; }
    }
    return nNewCharacterMessage;
  }

  writeBytes(data: DataView, tag: boolean): bool {
    const da = new DataAccess(data);
    return this.writeBytesDA(da, tag);
  }

  writeBytesDA(da: DataAccess, tag: boolean): bool {
    if (tag) {
      da.setByte(MessageType.NewCharacterMessageType as u8);
      if (da.hasError) { return false; }
    }
    da.setUint64(this.id);
    if (da.hasError) { return false; }
    da.setString(this.characterName);
    if (da.hasError) { return false; }
    da.setByte(this.job as u8);
    if (da.hasError) { return false; }
    da.setUint16(this.strength);
    if (da.hasError) { return false; }
    da.setUint16(this.intelligence);
    if (da.hasError) { return false; }
    da.setUint16(this.dexterity);
    if (da.hasError) { return false; }
    da.setUint16(this.wisdom);
    if (da.hasError) { return false; }
    da.setUint32(this.goldInWallet);
    if (da.hasError) { return false; }
    da.setUint16(this.nicknames.length as u16);
    if (da.hasError) { return false; }
    for (let i = 0; i < this.nicknames.length; i++) {
      let el = this.nicknames[i];
      da.setString(el);
      if (da.hasError) { return false; }
    }
    return true;
  }
}

export class CharacterJoinedTeam extends Message {
  characterID: u64 = 0;
  teamName: string = "";
  teamColors: Color[] = [];
  role: TeamRole = TeamRole.Minion;

  getMessageType() : MessageType { return MessageType.CharacterJoinedTeamType; }

  getSizeInBytes(): usize {
    let size: usize = 0;
    size += String.UTF8.encode(this.teamName, false).byteLength;
    size += this.teamColors.length * 16;
    size += 13;
    return size;
  }

  static override fromBytes(data: DataView): CharacterJoinedTeam | null {
    const da = new DataAccess(data);
    return CharacterJoinedTeam.fromBytesDA(da);
  }

  static override fromBytesDA(da: DataAccess): CharacterJoinedTeam | null {
    const nCharacterJoinedTeam = new CharacterJoinedTeam();
    nCharacterJoinedTeam.characterID = da.getUint64();
    if (da.hasError) { return null; }
    nCharacterJoinedTeam.teamName = da.getString();
    if (da.hasError) { return null; }
    const teamColors_Length = da.getUint16();
    if (da.hasError) { return null; }
    nCharacterJoinedTeam.teamColors = new Array<Color>(teamColors_Length);
    for (let i2: u16 = 0; i2 < teamColors_Length; i2++) {
      const _teamColors_i2_ = Color.fromBytes(da);
      if (_teamColors_i2_ == null) {
        return null;
      }
      else {
        nCharacterJoinedTeam.teamColors[i2] = _teamColors_i2_;
      }
    }
    let _role = da.getInt16();
    if (da.hasError) { return null; }
    if (_role < -1 || _role >= (TeamRole._Unknown as i16)) {
      _role = TeamRole._Unknown as i16;
    }
    nCharacterJoinedTeam.role = _role;
    return nCharacterJoinedTeam;
  }

  writeBytes(data: DataView, tag: boolean): bool {
    const da = new DataAccess(data);
    return this.writeBytesDA(da, tag);
  }

  writeBytesDA(da: DataAccess, tag: boolean): bool {
    if (tag) {
      da.setByte(MessageType.CharacterJoinedTeamType as u8);
      if (da.hasError) { return false; }
    }
    da.setUint64(this.characterID);
    if (da.hasError) { return false; }
    da.setString(this.teamName);
    if (da.hasError) { return false; }
    da.setUint16(this.teamColors.length as u16);
    if (da.hasError) { return false; }
    for (let i = 0; i < this.teamColors.length; i++) {
      let el = this.teamColors[i];
      if (!el.writeBytes(da)) { return false; };
    }
    da.setInt16(this.role as i16);
    if (da.hasError) { return false; }
    return true;
  }
}

