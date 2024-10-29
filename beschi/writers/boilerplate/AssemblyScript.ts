
const _textDec = new TextDecoder('utf-8');
const _textEnc = new TextEncoder();

export class DataAccess {
    buffer: DataView;
    currentOffset: usize;

    constructor(buffer: ArrayBuffer|DataView) {
        this.currentOffset = 0;
        if (buffer instanceof ArrayBuffer) {
            this.buffer = new DataView(buffer);
        }
        else {
            this.buffer = buffer;
        }
    }

    isFinished(): boolean {
        return this.currentOffset >= this.buffer.byteLength;
    }

    getByte(): u8 {
        const ret = this.buffer.getUint8(this.currentOffset);
        this.currentOffset += 1;
        return ret;
    }

    getBool(): boolean {
        return this.GetByte() > 0;
    }

    getInt16(): i16 {
        const ret = this.buffer.getInt16(this.currentOffset, true);
        this.currentOffset += 2;
        return ret;
    }

    getUint16(): u16 {
        const ret = this.buffer.getUint16(this.currentOffset, true);
        this.currentOffset += 2;
        return ret;
    }

    getInt32(): i32 {
        const ret = this.buffer.getInt32(this.currentOffset, true);
        this.currentOffset += 4;
        return ret;
    }

    getUint32(): u32 {
        const ret = this.buffer.getUint32(this.currentOffset, true);
        this.currentOffset += 4;
        return ret;
    }

    getInt64(): i64 {
        const ret = this.buffer.getBigInt64(this.currentOffset, true);
        this.currentOffset += 8;
        return ret;
    }

    getUint64(): u64 {
        const ret = this.buffer.getBigUint64(this.currentOffset, true);
        this.currentOffset += 8;
        return ret;
    }

    getFloat32(): f32 {
        const ret = this.buffer.getFloat32(this.currentOffset, true);
        this.currentOffset += 4;
        return Math.fround(ret);
    }

    getFloat64(): f64 {
        const ret = this.buffer.getFloat64(this.currentOffset, true);
        this.currentOffset += 8;
        return ret;
    }

    getString(): string {
        const len = this.Get{# STRING_SIZE_TYPE #}();
        const strBuffer = new Uint8Array(this.buffer.buffer, this.currentOffset, len);
        this.currentOffset += len;
        return _textDec.decode(strBuffer);
    }


    setByte(val: u8) {
        this.buffer.setUint8(this.currentOffset, val);
        this.currentOffset += 1;
    }

    setBool(val: boolean) {
        this.setByte(val ? 1 : 0);
    }

    setInt16(val: i16) {
        this.buffer.setInt16(this.currentOffset, val, true);
        this.currentOffset += 2;
    }

    setUint16(val: u16) {
        this.buffer.setUint16(this.currentOffset, val, true);
        this.currentOffset += 2;
    }

    setInt32(val: i32) {
        this.buffer.setInt32(this.currentOffset, val, true);
        this.currentOffset += 4;
    }

    setUint32(val: u32) {
        this.buffer.setUint32(this.currentOffset, val, true);
        this.currentOffset += 4;
    }

    setInt64(val: i64) {
        this.buffer.setBigInt64(this.currentOffset, val, true);
        this.currentOffset += 8;
    }

    setUint64(val: u64) {
        this.buffer.setBigUint64(this.currentOffset, val, true);
        this.currentOffset += 8;
    }

    setFloat32(val: f32) {
        this.buffer.setFloat32(this.currentOffset, val, true);
        this.currentOffset += 4;
    }

    setFloat64(val: f64) {
        this.buffer.setFloat64(this.currentOffset, val, true);
        this.currentOffset += 8;
    }

    setString(val: string) {
        const strBuffer = _textEnc.encode(val);
        this.Set{# STRING_SIZE_TYPE #}(strBuffer.byteLength);
        const arr = new Uint8Array(this.buffer.buffer);
        arr.set(strBuffer, this.currentOffset);
        this.currentOffset += strBuffer.byteLength;
    }
}
