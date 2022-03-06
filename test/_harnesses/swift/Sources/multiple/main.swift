import Foundation

import GeneratedMessages

var OK: Bool = true
func softAssert(_ condition: Bool, _ label: String) {
    if (!condition) {
        "FAILED! Swift: \(label)\n".data(using: .utf8).map(FileHandle.standardError.write)
        OK = false
    }
}

var parsed: [String: String] = [:]
var currentKeyword: String? = nil
for arg in CommandLine.arguments[1...] {
    if arg.starts(with: "--") {
        currentKeyword = String(arg[arg.index(arg.startIndex, offsetBy: 2)...])
        continue
    }
    if (currentKeyword != nil) {
        parsed[currentKeyword!] = arg
        currentKeyword = nil
        continue
    }
    parsed[arg] = ""
}


var nested = Nested.DeepData()


var emptyMsg = SmallMessages.EmptyMessage()
var byteMsg = SmallMessages.ByteMessage()
byteMsg.byteMember = 242
var intMsgA = SmallMessages.IntMessage()
intMsgA.intMember = -42
var intMsgB = SmallMessages.IntMessage()
intMsgB.intMember = 2048
var floatMsg = SmallMessages.FloatMessage()
floatMsg.floatMember = 1234.5678
var longMsg = SmallMessages.LongMessage()
longMsg.intMember = 2147483647 + 10 // (2^31 - 1) + 10


if parsed["generate"] != nil {
    let outPath = URL(fileURLWithPath: parsed["generate"]!)
    let outDir = outPath.deletingLastPathComponent()
    try FileManager.default.createDirectory(at: outDir, withIntermediateDirectories: true)

    var data = Data()
    byteMsg.WriteBytes(data: &data, tag: true)   //  0
    intMsgA.WriteBytes(data: &data, tag: true)   //  1
    intMsgB.WriteBytes(data: &data, tag: true)   //  2
    emptyMsg.WriteBytes(data: &data, tag: true)  //  3
    longMsg.WriteBytes(data: &data, tag: true)   //  4
    floatMsg.WriteBytes(data: &data, tag: true)  //  5
    intMsgA.WriteBytes(data: &data, tag: true)   //  6
    intMsgB.WriteBytes(data: &data, tag: true)   //  7
    intMsgB.WriteBytes(data: &data, tag: true)   //  8
    intMsgB.WriteBytes(data: &data, tag: true)   //  9
    intMsgA.WriteBytes(data: &data, tag: true)   // 10
    emptyMsg.WriteBytes(data: &data, tag: true)  // 11

    try data.write(to: outPath)

    var size: UInt32 = 0
    size += byteMsg.GetSizeInBytes()
    size += intMsgA.GetSizeInBytes() * 3
    size += intMsgB.GetSizeInBytes() * 4
    size += emptyMsg.GetSizeInBytes() * 2
    size += longMsg.GetSizeInBytes()
    size += floatMsg.GetSizeInBytes()
    size += 12

    softAssert(size == data.count, "written bytes check")
}
else if parsed["read"] != nil {
    let data = try Data(contentsOf: URL(fileURLWithPath: parsed["read"]!))

    let msgList = SmallMessages.ProcessRawBytes(data)

    softAssert(msgList.count == 12, "reading multiple messages length")

    softAssert(msgList[0]?.GetMessageType() == SmallMessages.MessageType.ByteMessageType, "msg 0 type")
    softAssert((msgList[0] as? SmallMessages.ByteMessage)!.byteMember == byteMsg.byteMember, "msg 0 content")

    softAssert(msgList[1]?.GetMessageType() == SmallMessages.MessageType.IntMessageType, "msg 1 type")
    softAssert((msgList[1] as? SmallMessages.IntMessage)!.intMember == intMsgA.intMember, "msg 1 content")

    softAssert(msgList[2]?.GetMessageType() == SmallMessages.MessageType.IntMessageType, "msg 2 type")
    softAssert((msgList[2] as? SmallMessages.IntMessage)!.intMember == intMsgB.intMember, "msg 2 content")

    softAssert(msgList[3]?.GetMessageType() == SmallMessages.MessageType.EmptyMessageType, "msg 3 type")

    softAssert(msgList[4]?.GetMessageType() == SmallMessages.MessageType.LongMessageType, "msg 4 type")
    softAssert((msgList[4] as? SmallMessages.LongMessage)!.intMember == longMsg.intMember, "msg 4 content")

    softAssert(msgList[5]?.GetMessageType() == SmallMessages.MessageType.FloatMessageType, "msg 5 type")
    softAssert((msgList[5] as? SmallMessages.FloatMessage)!.floatMember == floatMsg.floatMember, "msg 5 content")

    softAssert(msgList[6]?.GetMessageType() == SmallMessages.MessageType.IntMessageType, "msg 6 type")
    softAssert((msgList[6] as? SmallMessages.IntMessage)!.intMember == intMsgA.intMember, "msg 6 content")

    softAssert(msgList[7]?.GetMessageType() == SmallMessages.MessageType.IntMessageType, "msg 7 type")
    softAssert((msgList[7] as? SmallMessages.IntMessage)!.intMember == intMsgB.intMember, "msg 7 content")

    softAssert(msgList[8]?.GetMessageType() == SmallMessages.MessageType.IntMessageType, "msg 8 type")
    softAssert((msgList[8] as? SmallMessages.IntMessage)!.intMember == intMsgB.intMember, "msg 8 content")

    softAssert(msgList[9]?.GetMessageType() == SmallMessages.MessageType.IntMessageType, "msg 9 type")
    softAssert((msgList[9] as? SmallMessages.IntMessage)!.intMember == intMsgB.intMember, "msg 9 content")

    softAssert(msgList[10]?.GetMessageType() == SmallMessages.MessageType.IntMessageType, "msg 10 type")
    softAssert((msgList[10] as? SmallMessages.IntMessage)!.intMember == intMsgA.intMember, "msg 10 content")

    softAssert(msgList[11]?.GetMessageType() == SmallMessages.MessageType.EmptyMessageType, "msg 11 type")
}


if (!OK) {
    "Failed assertions.\n".data(using: .utf8).map(FileHandle.standardError.write)
    exit(1)
}
