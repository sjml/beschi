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
    var data: NSMutableData

    init() {
        self.data = NSMutableData()
    }

    init(withData: NSMutableData) {
        self.data = withData
    }

    var asData: Data {
        return self.data as Data
    }

    func Write(uint8: UInt8) {
        var val = uint8;
        self.data.append(&val, length: MemoryLayout<UInt8>.size);
    }

    func Write(bool: Bool) {
        self.Write(uint8: bool ? 1 : 0)
    }

    func Write(int16: Int16) {
        var val = int16;
        self.data.append(&val, length: MemoryLayout<Int16>.size);
    }

    func Write(uint16: UInt16) {
        var val = uint16;
        self.data.append(&val, length: MemoryLayout<UInt16>.size);
    }

    func Write(int32: Int32) {
        var val = int32;
        self.data.append(&val, length: MemoryLayout<Int32>.size);
    }

    func Write(uint32: UInt32) {
        var val = uint32;
        self.data.append(&val, length: MemoryLayout<UInt32>.size);
    }

    func Write(int64: Int64) {
        var val = int64;
        self.data.append(&val, length: MemoryLayout<Int64>.size);
    }

    func Write(uint64: UInt64) {
        var val = uint64;
        self.data.append(&val, length: MemoryLayout<UInt64>.size);
    }

    func Write(float32: Float32) {
        var val = float32;
        var valOut = UInt32(littleEndian: withUnsafeBytes(of: &val) {
            $0.load(fromByteOffset: 0, as: UInt32.self)
        })
        self.data.append(&valOut, length: MemoryLayout<UInt32>.size);
    }

    func Write(float64: Float64) {
        var val = float64;
        var valOut = UInt64(littleEndian: withUnsafeBytes(of: &val) {
            $0.load(fromByteOffset: 0, as: UInt64.self)
        })
        self.data.append(&valOut, length: MemoryLayout<UInt64>.size);
    }

    func Write(string: String) {
        let buffer = string.data(using: .utf8)!
        self.Write({# STRING_SIZE_TYPE_LOWER #}: {# STRING_SIZE_TYPE #}(buffer.count))
        self.data.append(buffer)
    }
}


public class Message {
    public func GetMessageType() -> MessageType {
        fatalError("GetMessageType must be implemented in subclass")
    }
    public func WriteBytes(data: NSMutableData, tag: Bool) -> Void {
        fatalError("WriteBytes must be implemented in subclass")
    }
    public func GetSizeInBytes() -> UInt32 {
        fatalError("GetSizeInBytes must be implemented in subclass")
    }
    public class func FromBytes(_ fromData: Data) throws -> Self {
        fatalError("FromBytes:fromData must be implemented in subclass")
    }
    class func FromBytes(dataReader: DataReader) throws -> Self {
        fatalError("FromBytes:dataReader must be implemented in subclass")
    }

    public static func UnpackMessages(_ data: Data) throws -> [Message] {
        let dataReader = DataReader(fromData: data)
        let headerBytes = dataReader.data[dataReader.currentOffset..<dataReader.currentOffset+4];
        guard
            let headerLabel = String(data: headerBytes, encoding: String.Encoding.utf8)
        else {
            throw DataReaderError.InvalidData
        }
        dataReader.currentOffset += 4
        if headerLabel != "BSCI" {
            throw DataReaderError.InvalidData
        }
        let msgCount = try dataReader.GetUInt32();
        if msgCount == 0 {
            return [Message]()
        }
        let listData = data.subdata(in: dataReader.currentOffset..<dataReader.data.count)
        let msgList: [Message] = try ProcessRawBytes(listData, max: Int(msgCount))
        if msgList.count == 0 {
            throw DataReaderError.InvalidData
        }
        if msgList.count != msgCount {
            throw DataReaderError.InvalidData
        }
        return msgList.compactMap { $0 }
    }
}

