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


var lmsg = BrokenMessages.ListMessage()
lmsg.ints = [1, 2, 32767, 4, 5]

if parsed["generate"] != nil {
    let outPath = URL(fileURLWithPath: parsed["generate"]!)
    let outDir = outPath.deletingLastPathComponent()
    try FileManager.default.createDirectory(at: outDir, withIntermediateDirectories: true)

    var data = NSMutableData()
    lmsg.WriteBytes(data: data, tag: false)

    softAssert(lmsg.GetSizeInBytes() == data.count, "written bytes check");

    // tweak the buffer so the message looks longer
    var buffer = [UInt8](data)
    buffer[0] = 0xFF
    data = NSMutableData(data: Data(buffer))

    try data.write(to: outPath)
}
else if parsed["read"] != nil {
    let data = try Data(contentsOf: URL(fileURLWithPath: parsed["read"]!))
    var caught: BrokenMessages.DataReaderError? = nil
    do {
        let _ = try BrokenMessages.ListMessage.FromBytes(data)
    }
    catch BrokenMessages.DataReaderError.EOF {
        caught = BrokenMessages.DataReaderError.EOF
    }

    softAssert(caught == BrokenMessages.DataReaderError.EOF, "reading truncated message")
}


if (!OK) {
    "Failed assertions.\n".data(using: .utf8).map(FileHandle.standardError.write)
    exit(1)
}
