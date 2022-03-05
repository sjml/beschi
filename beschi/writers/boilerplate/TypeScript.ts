
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
        const len = this.Get{# STRING_SIZE_TYPE #}();
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
        this.Set{# STRING_SIZE_TYPE #}(strBuffer.byteLength);
        const arr = new Uint8Array(this.buffer.buffer);
        arr.set(strBuffer, this.currentOffset);
        this.currentOffset += strBuffer.byteLength;
    }
}
