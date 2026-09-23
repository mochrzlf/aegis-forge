import Foundation
import CommonCrypto
import Security

/// Custom URLSessionDelegate implementing Public Key Pinning (SPKI SHA-256)
/// to defend against Man-in-the-Middle (MitM) attacks and user-installed proxy CAs.
public final class PinnedURLSessionDelegate: NSObject, URLSessionDelegate {
    
    /// Target host to pin
    public let targetHost: String
    
    /// Pinned SHA-256 public key hashes (Base64-encoded).
    /// Always supply at least ONE primary pin and ONE backup pin for rotation.
    public let pinnedPublicKeyHashes: Set<String>
    
    public init(targetHost: String, pinnedPublicKeyHashes: Set<String>) {
        self.targetHost = targetHost
        self.pinnedPublicKeyHashes = pinnedPublicKeyHashes
        super.init()
    }
    
    // MARK: - URLSessionDelegate
    
    public func urlSession(
        _ session: URLSession,
        didReceive challenge: URLAuthenticationChallenge,
        completionHandler: @escaping (URLSession.AuthChallengeDisposition, URLCredential?) -> Void
    ) {
        guard challenge.protectionSpace.authenticationMethod == NSURLAuthenticationMethodServerTrust,
              let serverTrust = challenge.protectionSpace.serverTrust,
              challenge.protectionSpace.host == targetHost else {
            // Default evaluation for non-pinned domains (or reject)
            completionHandler(.performDefaultHandling, nil)
            return
        }
        
        // 1. Evaluate standard system trust first (valid CA, not expired, valid hostname)
        var secResult: SecTrustResultType = .invalid
        let evalStatus: OSStatus
        if #available(iOS 12.0, *) {
            var error: CFError?
            let isTrusted = SecTrustEvaluateWithError(serverTrust, &error)
            evalStatus = isTrusted ? errSecSuccess : errSecNotTrusted
        } else {
            evalStatus = SecTrustEvaluate(serverTrust, &secResult)
        }
        
        guard evalStatus == errSecSuccess else {
            #if DEBUG
            print("⚠️ Server trust evaluation failed.")
            #endif
            completionHandler(.cancelAuthenticationChallenge, nil)
            return
        }
        
        // 2. Validate Public Key (SPKI) against pinned hashes
        guard let serverCertificate = SecTrustGetCertificateAtIndex(serverTrust, 0),
              let serverPublicKey = SecCertificateCopyKey(serverCertificate),
              let publicKeyData = SecKeyCopyExternalRepresentation(serverPublicKey, nil) as Data? else {
            completionHandler(.cancelAuthenticationChallenge, nil)
            return
        }
        
        let serverPublicKeyHash = sha256Base64(data: publicKeyData)
        
        if pinnedPublicKeyHashes.contains(serverPublicKeyHash) {
            // Certificate Pin matches! Trust accepted.
            completionHandler(.useCredential, URLCredential(trust: serverTrust))
        } else {
            #if DEBUG
            print("❌ Certificate Pin Mismatch! Expected one of: \(pinnedPublicKeyHashes), got: \(serverPublicKeyHash)")
            #endif
            // REJECT connection — potential MitM attack detected
            completionHandler(.cancelAuthenticationChallenge, nil)
        }
    }
    
    // MARK: - SHA-256 Helper
    
    private func sha256Base64(data: Data) -> String {
        var hash = [UInt8](repeating: 0, count: Int(CC_SHA256_DIGEST_LENGTH))
        data.withUnsafeBytes { buffer in
            _ = CC_SHA256(buffer.baseAddress, CC_LONG(data.count), &hash)
        }
        return Data(hash).base64EncodedString()
    }
}
