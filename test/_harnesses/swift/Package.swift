// swift-tools-version:5.5
// The swift-tools-version declares the minimum version of Swift required to build this package.

import PackageDescription

let package = Package(
    name: "swift-harness",
    products: [
        .library(name: "GeneratedMessages", type: .static, targets: ["GeneratedMessages"]),
        .executable(name: "basic", targets: ["basic"]),
        .executable(name: "broken", targets: ["broken"]),
        .executable(name: "truncated", targets: ["truncated"]),
        .executable(name: "multiple", targets: ["multiple"]),
        .executable(name: "multiple_broken", targets: ["multiple_broken"]),
        .executable(name: "sized", targets: ["sized"]),
    ],
    dependencies: [],
    targets: [
        .target(name: "GeneratedMessages"),
        .executableTarget(name: "basic", dependencies: ["GeneratedMessages"]),
        .executableTarget(name: "broken", dependencies: ["GeneratedMessages"]),
        .executableTarget(name: "truncated", dependencies: ["GeneratedMessages"]),
        .executableTarget(name: "multiple", dependencies: ["GeneratedMessages"]),
        .executableTarget(name: "multiple_broken", dependencies: ["GeneratedMessages"]),
        .executableTarget(name: "sized", dependencies: ["GeneratedMessages"]),
    ]
)
