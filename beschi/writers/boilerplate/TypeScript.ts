
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

    isFinished(): boolean {
        return this.currentOffset >= this.buffer.byteLength;
    }

    getByte(): number {
        const ret = this.buffer.getUint8(this.currentOffset);
        this.currentOffset += 1;
        return ret;
    }

    getBool(): boolean {
        return this.getByte() > 0;
    }

    getInt16(): number {
        const ret = this.buffer.getInt16(this.currentOffset, true);
        this.currentOffset += 2;
        return ret;
    }

    getUint16(): number {
        const ret = this.buffer.getUint16(this.currentOffset, true);
        this.currentOffset += 2;
        return ret;
    }

    getInt32(): number {
        const ret = this.buffer.getInt32(this.currentOffset, true);
        this.currentOffset += 4;
        return ret;
    }

    getUint32(): number {
        const ret = this.buffer.getUint32(this.currentOffset, true);
        this.currentOffset += 4;
        return ret;
    }

    getInt64(): bigint {
        const ret = this.buffer.getBigInt64(this.currentOffset, true);
        this.currentOffset += 8;
        return ret;
    }

    getUint64(): bigint {
        const ret = this.buffer.getBigUint64(this.currentOffset, true);
        this.currentOffset += 8;
        return ret;
    }

    getFloat32(): number {
        const ret = this.buffer.getFloat32(this.currentOffset, true);
        this.currentOffset += 4;
        return Math.fround(ret);
    }

    getFloat64(): number {
        const ret = this.buffer.getFloat64(this.currentOffset, true);
        this.currentOffset += 8;
        return ret;
    }

    getString(): string {
        const len = this.get{# STRING_SIZE_TYPE #}();
        const strBuffer = new Uint8Array(this.buffer.buffer, this.currentOffset, len);
        this.currentOffset += len;
        return _textDec.decode(strBuffer);
    }


    setByte(val: number) {
        this.buffer.setUint8(this.currentOffset, val);
        this.currentOffset += 1;
    }

    setBool(val: boolean) {
        this.setByte(val ? 1 : 0);
    }

    setInt16(val: number) {
        this.buffer.setInt16(this.currentOffset, val, true);
        this.currentOffset += 2;
    }

    setUint16(val: number) {
        this.buffer.setUint16(this.currentOffset, val, true);
        this.currentOffset += 2;
    }

    setInt32(val: number) {
        this.buffer.setInt32(this.currentOffset, val, true);
        this.currentOffset += 4;
    }

    setUint32(val: number) {
        this.buffer.setUint32(this.currentOffset, val, true);
        this.currentOffset += 4;
    }

    setInt64(val: bigint) {
        this.buffer.setBigInt64(this.currentOffset, val, true);
        this.currentOffset += 8;
    }

    setUint64(val: bigint) {
        this.buffer.setBigUint64(this.currentOffset, val, true);
        this.currentOffset += 8;
    }

    setFloat32(val: number) {
        this.buffer.setFloat32(this.currentOffset, val, true);
        this.currentOffset += 4;
    }

    setFloat64(val: number) {
        this.buffer.setFloat64(this.currentOffset, val, true);
        this.currentOffset += 8;
    }

    setString(val: string) {
        const strBuffer = _textEnc.encode(val);
        this.set{# STRING_SIZE_TYPE #}(strBuffer.byteLength);
        const arr = new Uint8Array(this.buffer.buffer);
        arr.set(strBuffer, this.currentOffset);
        this.currentOffset += strBuffer.byteLength;
    }
}
