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


var trunc = BrokenMessages.TruncatedMessage()
trunc.x = 1.0
trunc.y = 2.0

var full = BrokenMessages.FullMessage()
full.x = 1.0
full.y = 2.0
full.z = 3.0


if parsed["generate"] != nil {
    let outPath = URL(fileURLWithPath: parsed["generate"]!)
    let outDir = outPath.deletingLastPathComponent()
    try FileManager.default.createDirectory(at: outDir, withIntermediateDirectories: true)

    var data = Data()
    full.WriteBytes(data: &data, tag: true)
    full.WriteBytes(data: &data, tag: true)
    full.WriteBytes(data: &data, tag: true)

    // write a truncated message tagged as a full one
    data.append(BrokenMessages.MessageType.FullMessageType.rawValue)
    trunc.WriteBytes(data: &data, tag: false)

    full.WriteBytes(data: &data, tag: true)
    full.WriteBytes(data: &data, tag: true)
    full.WriteBytes(data: &data, tag: true)

    try data.write(to: outPath)
}
else if parsed["read"] != nil {
    let data = try Data(contentsOf: URL(fileURLWithPath: parsed["read"]!))

    let msgList = BrokenMessages.ProcessRawBytes(data)

    softAssert(msgList.count == 5, "read broken stream length")
    softAssert(msgList[4] == nil, "read broken stream null sentinel")
}


if (!OK) {
    "Failed assertions.\n".data(using: .utf8).map(FileHandle.standardError.write)
    exit(1)
}
