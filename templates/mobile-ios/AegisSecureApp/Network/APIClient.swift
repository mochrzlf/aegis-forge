import Foundation

/// Standard Banking API Response Envelope
public struct APIResponseEnvelope<T: Codable>: Codable {
    public let success: Bool
    public let data: T?
    public let error: APIErrorPayload?
}

public struct APIErrorPayload: Codable {
    public let code: String
    public let message: String
}

public enum NetworkError: LocalizedError {
    case invalidURL
    case serverError(code: String, message: String)
    case unauthorized
    case decodingError
    case pinMismatchOrConnectionFailed
    
    public var errorDescription: String? {
        switch self {
        case .invalidURL:
            return "Format URL endpoint tidak valid."
        case .serverError(let code, let message):
            return "[\(code)] \(message)"
        case .unauthorized:
            return "Sesi autentikasi telah berakhir. Silakan login kembali."
        case .decodingError:
            return "Gagal memproses data balasan dari server."
        case .pinMismatchOrConnectionFailed:
            return "Koneksi ditolak demi keamanan (SSL Pinning Mismatch atau jaringan tidak aman)."
        }
    }
}

/// Banking-grade API Client with SSL Pinning and Keychain Token integration.
public final class APIClient {
    
    public static let shared = APIClient()
    
    public var baseURL: String = "https://api.example.com"
    private var urlSession: URLSession
    
    public init(
        targetHost: String = "api.example.com",
        pinnedHashes: Set<String> = [
            // Example Primary & Backup SPKI SHA-256 Hashes
            "47DEQpj8HBSa+/TImW+5JCeuQeRkm5NMpJWZG3hSuFU=",
            "k2v657xBsOVe1PQR/JU7tNm+hmd2hGO+2O759zyoK40="
        ]
    ) {
        let delegate = PinnedURLSessionDelegate(targetHost: targetHost, pinnedPublicKeyHashes: pinnedHashes)
        let config = URLSessionConfiguration.ephemeral
        // Enforce cookie acceptance for HttpOnly refresh tokens
        config.httpCookieAcceptPolicy = .always
        config.httpShouldSetCookies = true
        
        self.urlSession = URLSession(configuration: config, delegate: delegate, delegateQueue: nil)
    }
    
    /// Executes authenticated request with response envelope decoding
    public func request<T: Codable>(
        endpoint: APIEndpoint,
        method: String = "GET",
        body: Data? = nil
    ) async throws -> T {
        guard let url = URL(string: baseURL + endpoint.path) else {
            throw NetworkError.invalidURL
        }
        
        var request = URLRequest(url: url)
        request.httpMethod = method
        request.httpBody = body
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.setValue("application/json", forHTTPHeaderField: "Accept")
        
        // Attach bearer token from Secure Keychain if available
        if let token = KeychainStorage.shared.getString(key: "access_token") {
            request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        }
        
        do {
            let (data, response) = try await urlSession.data(for: request)
            
            guard let httpResponse = response as? HTTPURLResponse else {
                throw NetworkError.decodingError
            }
            
            if httpResponse.statusCode == 401 {
                // Wipe local tokens on authorization rejection (killswitch trigger)
                KeychainStorage.shared.delete(key: "access_token")
                throw NetworkError.unauthorized
            }
            
            let decoder = JSONDecoder()
            let envelope = try decoder.decode(APIResponseEnvelope<T>.self, from: data)
            
            if envelope.success, let responseData = envelope.data {
                return responseData
            } else if let err = envelope.error {
                throw NetworkError.serverError(code: err.code, message: err.message)
            } else {
                throw NetworkError.decodingError
            }
        } catch let netErr as NetworkError {
            throw netErr
        } catch {
            throw NetworkError.pinMismatchOrConnectionFailed
        }
    }
}
