import Foundation
import UIKit

/// Multi-layered device integrity and jailbreak detector adhering to
/// Banking-Grade Mobile Security Standard (M3.1: Root & Jailbreak Detection).
public final class JailbreakDetector {
    
    public struct IntegrityResult {
        public let isJailbroken: Bool
        public let failedChecks: [String]
    }
    
    /// Performs comprehensive device integrity audit
    public static func checkDeviceIntegrity() -> IntegrityResult {
        #if targetEnvironment(simulator)
        // Bypass checks on iOS Simulator for development convenience
        return IntegrityResult(isJailbroken: false, failedChecks: [])
        #else
        var failedChecks: [String] = []
        
        if hasJailbreakFiles() {
            failedChecks.append("Jailbreak artifacts found in filesystem")
        }
        
        if canWriteOutsideSandbox() {
            failedChecks.append("App sandbox compromised (filesystem write outside container)")
        }
        
        if hasSuspiciousURLSchemes() {
            failedChecks.append("Cydia/Sileo URL schemes detected")
        }
        
        if hasDyldInjection() {
            failedChecks.append("DYLD_INSERT_LIBRARIES injection detected")
        }
        
        return IntegrityResult(
            isJailbroken: !failedChecks.isEmpty,
            failedChecks: failedChecks
        )
        #endif
    }
    
    // MARK: - Check 1: Known Jailbreak Paths
    
    private static func hasJailbreakFiles() -> Bool {
        let suspiciousPaths = [
            "/Applications/Cydia.app",
            "/Applications/Sileo.app",
            "/Applications/Zebra.app",
            "/Library/MobileSubstrate/MobileSubstrate.dylib",
            "/bin/bash",
            "/usr/sbin/sshd",
            "/etc/apt",
            "/private/var/lib/apt/",
            "/usr/bin/ssh",
            "/Library/PreferenceBundles/LibertyPref.bundle",
            "/Library/PreferenceBundles/ShadowPreferences.bundle"
        ]
        
        let fileManager = FileManager.default
        for path in suspiciousPaths {
            if fileManager.fileExists(atPath: path) {
                return true
            }
        }
        return false
    }
    
    // MARK: - Check 2: Sandbox Write Test
    
    private static func canWriteOutsideSandbox() -> Bool {
        let testPath = "/private/aegis_jailbreak_probe.txt"
        do {
            try "probe".write(toFile: testPath, atomically: true, encoding: .utf8)
            // If write succeeded, sandbox is BROKEN
            try? FileManager.default.removeItem(atPath: testPath)
            return true
        } catch {
            // Write failed as expected in a secure sandbox
            return false
        }
    }
    
    // MARK: - Check 3: Suspicious URL Schemes
    
    private static func hasSuspiciousURLSchemes() -> Bool {
        guard let cydiaURL = URL(string: "cydia://package/com.example.package") else { return false }
        return UIApplication.shared.canOpenURL(cydiaURL)
    }
    
    // MARK: - Check 4: Dynamic Linker Injection
    
    private static func hasDyldInjection() -> Bool {
        let dyldKey = "DYLD_INSERT_LIBRARIES"
        return getenv(dyldKey) != nil
    }
}
