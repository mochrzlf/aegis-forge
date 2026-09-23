import SwiftUI

/// Privacy Shield Overlay displayed when the app transitions to inactive state
/// (App Switcher) or when screen recording / AirPlay mirroring is active.
public struct PrivacyShieldView: View {
    public init() {}
    
    public var body: some View {
        ZStack {
            Color(UIColor.systemBackground)
                .ignoresSafeArea()
            
            VStack(spacing: 20) {
                Image(systemName: "lock.shield.fill")
                    .resizable()
                    .aspectRatio(contentMode: .fit)
                    .frame(width: 80, height: 80)
                    .foregroundColor(.blue)
                
                Text("Aegis Forge Secure App")
                    .font(.title2)
                    .fontWeight(.bold)
                
                Text("Tampilan dilindungi demi keamanan data dan privasi perbankan Anda.")
                    .font(.subheadline)
                    .foregroundColor(.secondary)
                    .multilineTextAlignment(.center)
                    .padding(.horizontal, 40)
            }
        }
    }
}
