public enum DataReaderError: Error {
    case EOF
    case InvalidData
}

class DataReader {
    let data: Data
    var currentOffset: Int = 0
    init(fromData data: Data) {
        self.data = data
    }

    func IsFinished() -> Bool {
        return self.currentOffset >= self.data.count
    }

    func GetUInt8() throws -> UInt8 {
        if (self.data.count < self.currentOffset + 1) {
            throw DataReaderError.EOF
        }
        let ret = UInt8(littleEndian: data.withUnsafeBytes { dataBytes in
            var val: UInt8 = 0
            memcpy(&val, dataBytes.baseAddress! + self.currentOffset, 1)
            return val
        })
        self.currentOffset += 1
        return ret
    }

    func GetBool() throws -> Bool {
        return try self.GetUInt8() > 0
    }

    func GetInt16() throws -> Int16 {
        if (self.data.count < self.currentOffset + 2) {
            throw DataReaderError.EOF
        }
        let ret = Int16(littleEndian: data.withUnsafeBytes { dataBytes in
            var val: Int16 = 0
            memcpy(&val, dataBytes.baseAddress! + self.currentOffset, 2)
            return val
        })
        self.currentOffset += 2
        return ret
    }

    func GetUInt16() throws -> UInt16 {
        if (self.data.count < self.currentOffset + 2) {
            throw DataReaderError.EOF
        }
        let ret = UInt16(littleEndian: data.withUnsafeBytes { dataBytes in
            var val: UInt16 = 0
            memcpy(&val, dataBytes.baseAddress! + self.currentOffset, 2)
            return val
        })
        self.currentOffset += 2
        return ret
    }

    func GetInt32() throws -> Int32 {
        if (self.data.count < self.currentOffset + 4) {
            throw DataReaderError.EOF
        }
        let ret = Int32(littleEndian: data.withUnsafeBytes { dataBytes in
            var val: Int32 = 0
            memcpy(&val, dataBytes.baseAddress! + self.currentOffset, 4)
            return val
        })
        self.currentOffset += 4
        return ret
    }

    func GetUInt32() throws -> UInt32 {
        if (self.data.count < self.currentOffset + 4) {
            throw DataReaderError.EOF
        }
        let ret = UInt32(littleEndian: data.withUnsafeBytes { dataBytes in
            var val: UInt32 = 0
            memcpy(&val, dataBytes.baseAddress! + self.currentOffset, 4)
            return val
        })
        self.currentOffset += 4
        return ret
    }

    func GetInt64() throws -> Int64 {
        if (self.data.count < self.currentOffset + 8) {
            throw DataReaderError.EOF
        }
        let ret = Int64(littleEndian: data.withUnsafeBytes { dataBytes in
            var val: Int64 = 0
            memcpy(&val, dataBytes.baseAddress! + self.currentOffset, 8)
            return val
        })
        self.currentOffset += 8
        return ret
    }

    func GetUInt64() throws -> UInt64 {
        if (self.data.count < self.currentOffset + 8) {
            throw DataReaderError.EOF
        }
        let ret = UInt64(littleEndian: data.withUnsafeBytes { dataBytes in
            var val: UInt64 = 0
            memcpy(&val, dataBytes.baseAddress! + self.currentOffset, 8)
            return val
        })
        self.currentOffset += 8
        return ret
    }

    func GetFloat32() throws -> Float32 {
        if (self.data.count < self.currentOffset + 4) {
            throw DataReaderError.EOF
        }
        let ret = Float32(bitPattern: UInt32(littleEndian: data.withUnsafeBytes { dataBytes in
            var val: UInt32 = 0
            memcpy(&val, dataBytes.baseAddress! + self.currentOffset, 4)
            return val
        }))
        self.currentOffset += 4
        return ret
    }

    func GetFloat64() throws -> Float64 {
        if (self.data.count < self.currentOffset + 8) {
            throw DataReaderError.EOF
        }
        let ret = Float64(bitPattern: UInt64(littleEndian: data.withUnsafeBytes { dataBytes in
            var val: UInt64 = 0
            memcpy(&val, dataBytes.baseAddress! + self.currentOffset, 8)
            return val
        }))
        self.currentOffset += 8
        return ret
    }

    func GetString() throws -> String {
        let stringLength = try Int(self.Get{# STRING_SIZE_TYPE #}())
        if (self.data.count < self.currentOffset + stringLength) {
            throw DataReaderError.EOF
        }
        let stringData = self.data[self.currentOffset..<(self.currentOffset+stringLength)]
        guard
            let ret = String(data: stringData, encoding: String.Encoding.utf8)
        else {
            throw DataReaderError.InvalidData
        }
        self.currentOffset += stringLength
        return ret
    }
}

class DataWriter {
    var data: Data
    init() {
        self.data = Data()
    }
    init(withData: inout Data) {
        self.data = withData
    }

    func WriteUInt8(_ ui8: UInt8) {
        self.data.append(ui8)
    }

    func WriteBool(_ b: Bool) {
        self.WriteUInt8(b ? 1 : 0)
    }

    func WriteInt16(_ i16: Int16) {
        var _i16 = Int16(littleEndian: i16)
        self.data.append(withUnsafeBytes(of: &_i16, {Data($0)}))
    }

    func WriteUInt16(_ ui16: UInt16) {
        var _ui16 = UInt16(littleEndian: ui16)
        self.data.append(withUnsafeBytes(of: &_ui16, {Data($0)}))
    }

    func WriteInt32(_ i32: Int32) {
        var _i32 = Int32(littleEndian: i32)
        self.data.append(withUnsafeBytes(of: &_i32, {Data($0)}))
    }

    func WriteUInt32(_ ui32: UInt32) {
        var _ui32 = UInt32(littleEndian: ui32)
        self.data.append(withUnsafeBytes(of: &_ui32, {Data($0)}))
    }

    func WriteInt64(_ i64: Int64) {
        var _i64 = Int64(littleEndian: i64)
        self.data.append(withUnsafeBytes(of: &_i64, {Data($0)}))
    }

    func WriteUInt64(_ ui64: UInt64) {
        var _ui64 = UInt64(littleEndian: ui64)
        self.data.append(withUnsafeBytes(of: &_ui64, {Data($0)}))
    }

    func WriteFloat32(_ f: Float32) {
        var _f = f
        var out = UInt32(littleEndian: withUnsafeBytes(of: &_f, {$0.load(fromByteOffset: 0, as: UInt32.self)}))
        self.data.append(withUnsafeBytes(of: &out, {Data($0)}))
    }

    func WriteFloat64(_ d: Float64) {
        var _d = d
        var out = UInt64(littleEndian: withUnsafeBytes(of: &_d, {$0.load(fromByteOffset: 0, as: UInt64.self)}))
        self.data.append(withUnsafeBytes(of: &out, {Data($0)}))
    }

    func WriteString(_ s: String) {
        let buffer = s.data(using: String.Encoding.utf8)!
        self.Write{# STRING_SIZE_TYPE #}({# STRING_SIZE_TYPE #}(buffer.count))
        self.data.append(buffer)
    }
}

