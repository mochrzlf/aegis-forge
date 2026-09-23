import Foundation

/// Standard REST API endpoint catalog aligned with `docs/openapi.yaml`.
public enum APIEndpoint {
    case healthLive
    case healthReady
    case register
    case login
    case refresh
    case logout
    case userProfile(id: String)
    case approvals
    case reviewApproval(id: String)
    
    public var path: String {
        switch self {
        case .healthLive:
            return "/health/live"
        case .healthReady:
            return "/health/ready"
        case .register:
            return "/api/auth/register"
        case .login:
            return "/api/auth/login"
        case .refresh:
            return "/api/auth/refresh"
        case .logout:
            return "/api/auth/logout"
        case .userProfile(let id):
            return "/api/users/\(id)"
        case .approvals:
            return "/api/approvals"
        case .reviewApproval(let id):
            return "/api/approvals/\(id)/review"
        }
    }
}
