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


let msgList: [SmallMessages.Message] = [
    SmallMessages.IntMessage(),
    SmallMessages.FloatMessage(),
    SmallMessages.FloatMessage(),
    SmallMessages.FloatMessage(),
    SmallMessages.IntMessage(),
    SmallMessages.EmptyMessage(),
    SmallMessages.LongMessage(),
    SmallMessages.LongMessage(),
    SmallMessages.LongMessage(),
    SmallMessages.IntMessage(),
]



if parsed["generate"] != nil {
    let outPath = URL(fileURLWithPath: parsed["generate"]!)
    let outDir = outPath.deletingLastPathComponent()
    try FileManager.default.createDirectory(at: outDir, withIntermediateDirectories: true)

    let data = NSMutableData()
    msgList.PackMessages(data)

    var fakeLength: UInt8 = 15
    data.replaceBytes(in: NSMakeRange(4,1), withBytes: &fakeLength)

    try data.write(to: outPath)
}
else if parsed["read"] != nil {
    let data = try Data(contentsOf: URL(fileURLWithPath: parsed["read"]!))

    var caught: SmallMessages.DataReaderError? = nil
    do {
        let _ = try SmallMessages.Message.UnpackMessages(data)
        softAssert(false, "broken unpack")
    } catch SmallMessages.DataReaderError.InvalidData {
        caught = SmallMessages.DataReaderError.InvalidData
    }

    softAssert(caught == SmallMessages.DataReaderError.InvalidData, "broken unpack error")
}


if (!OK) {
    "Failed assertions.\n".data(using: .utf8).map(FileHandle.standardError.write)
    exit(1)
}
