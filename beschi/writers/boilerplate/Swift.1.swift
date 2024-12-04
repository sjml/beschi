extension Array where Element == {# NAMESPACE_PREFIX_DOT #}Message {
    public func GetPackedSize() -> Int {
        var size: Int = 0
        for msg in self {
            size += Int(msg.GetSizeInBytes())
        }
        size += self.count
        size += 9
        return size
    }

    public func PackMessages(_ data: NSMutableData) -> Void {
        let dataWriter = {# NAMESPACE_PREFIX_DOT #}DataWriter(withData: data)
        let headerBytes = "BSCI".data(using: String.Encoding.utf8)!
        dataWriter.data.append(headerBytes)
        var msgCount = UInt32(littleEndian: UInt32(self.count))
        dataWriter.data.append(Swift.withUnsafeBytes(of: &msgCount, {Data($0)}))
        for msg in self {
            msg.WriteBytes(data: dataWriter.data, tag: true)
        }
        dataWriter.Write(uint8: 0)
    }
}
