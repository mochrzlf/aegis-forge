// swift-tools-version: 5.9
import PackageDescription

let package = Package(
    name: "AegisSecureApp",
    platforms: [
        .iOS(.v15),
        .macOS(.v12)
    ],
    products: [
        .library(
            name: "AegisSecureApp",
            targets: ["AegisSecureApp"]
        ),
    ],
    dependencies: [],
    targets: [
        .target(
            name: "AegisSecureApp",
            dependencies: [],
            path: "AegisSecureApp"
        ),
    ]
)
