import SwiftUI
import Combine

/// ViewModifier that shields sensitive financial screens from being captured
/// in iOS App Switcher snapshots or unauthorized screen recordings.
public struct ScreenShieldModifier: ViewModifier {
    @Environment(\.scenePhase) private var scenePhase
    @State private var isScreenCaptured: Bool = UIScreen.main.isCaptured
    
    public init() {}
    
    public func body(content: Content) -> some View {
        ZStack {
            content
                .blur(radius: shouldShield ? 24 : 0)
                .disabled(shouldShield)
            
            if shouldShield {
                PrivacyShieldView()
                    .transition(.opacity)
            }
        }
        .onReceive(NotificationCenter.default.publisher(for: UIScreen.capturedDidChangeNotification)) { _ in
            self.isScreenCaptured = UIScreen.main.isCaptured
        }
        .animation(.easeInOut(duration: 0.2), value: shouldShield)
    }
    
    private var shouldShield: Bool {
        return scenePhase != .active || isScreenCaptured
    }
}

public extension View {
    /// Applies banking-grade privacy shielding (App Switcher blur & anti-screen capture).
    func enableScreenPrivacyShield() -> some View {
        modifier(ScreenShieldModifier())
    }
}
