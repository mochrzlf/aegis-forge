import SwiftUI

public struct ContentView: View {
    @State private var email: String = "nasabah@bank.com"
    @State private var balance: String = "Rp 125.450.000"
    @State private var isLoggedIn: Bool = false
    @State private var isJailbroken: Bool = false
    @State private var securityViolations: [String] = []
    
    public init() {}
    
    public var body: some View {
        NavigationView {
            VStack(spacing: 24) {
                // Jailbreak / Root Warning Banner
                if isJailbroken {
                    VStack(alignment: .leading, spacing: 8) {
                        HStack {
                            Image(systemName: "exclamationmark.triangle.fill")
                                .foregroundColor(.red)
                            Text("PERINGATAN KEAMANAN PERANGKAT")
                                .font(.caption)
                                .fontWeight(.bold)
                                .foregroundColor(.red)
                        }
                        Text("Perangkat terdeteksi mengalami modifikasi sistem (Jailbreak / Root). Fitur transaksi dibatasi.")
                            .font(.caption2)
                            .foregroundColor(.secondary)
                    }
                    .padding()
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .background(Color.red.opacity(0.1))
                    .cornerRadius(12)
                    .padding(.horizontal)
                }
                
                // Account Balance Card (Sensitive Information)
                VStack(alignment: .leading, spacing: 12) {
                    HStack {
                        Text("Rekening Tabungan Utama")
                            .font(.caption)
                            .foregroundColor(.white.opacity(0.8))
                        Spacer()
                        Image(systemName: "shield.checkered")
                            .foregroundColor(.white)
                    }
                    
                    Text(balance)
                        .font(.system(size: 32, weight: .bold, design: .rounded))
                        .foregroundColor(.white)
                    
                    HStack {
                        Text("Aegis Secure Platinum")
                            .font(.caption2)
                            .foregroundColor(.white.opacity(0.7))
                        Spacer()
                        Text("Hardware Encrypted")
                            .font(.caption2)
                            .foregroundColor(.green.opacity(0.9))
                    }
                }
                .padding(24)
                .background(
                    LinearGradient(
                        colors: [Color.blue, Color.indigo],
                        startPoint: .topLeading,
                        endPoint: .bottomTrailing
                    )
                )
                .cornerRadius(20)
                .shadow(color: Color.blue.opacity(0.3), radius: 10, x: 0, y: 5)
                .padding(.horizontal)
                
                // Security Controls Status List
                VStack(alignment: .leading, spacing: 16) {
                    Text("Pilar Proteksi Aktif")
                        .font(.headline)
                        .padding(.horizontal)
                    
                    SecurityFeatureRow(
                        icon: "key.fill",
                        title: "Apple Keychain Storage",
                        subtitle: "Token dienkripsi di Secure Enclave (kSecAttrAccessibleThisDeviceOnly)"
                    )
                    
                    SecurityFeatureRow(
                        icon: "lock.shield.fill",
                        title: "Public Key SSL Pinning",
                        subtitle: "Mencegah serangan Man-in-the-Middle (MitM) & proxy CA"
                    )
                    
                    SecurityFeatureRow(
                        icon: "eye.slash.fill",
                        title: "Screen Privacy Shield",
                        subtitle: "Otomatis blur saat App Switcher & blokir perekaman layar"
                    )
                }
                
                Spacer()
            }
            .navigationTitle("Aegis Mobile")
            .onAppear {
                auditDevice()
            }
        }
        // Protect entire view hierarchy with Banking Privacy Shield
        .enableScreenPrivacyShield()
    }
    
    private func auditDevice() {
        let audit = JailbreakDetector.checkDeviceIntegrity()
        self.isJailbroken = audit.isJailbroken
        self.securityViolations = audit.failedChecks
    }
}

struct SecurityFeatureRow: View {
    let icon: String
    let title: String
    let subtitle: String
    
    var body: some View {
        HStack(spacing: 16) {
            Image(systemName: icon)
                .font(.title2)
                .foregroundColor(.blue)
                .frame(width: 40)
            
            VStack(alignment: .leading, spacing: 4) {
                Text(title)
                    .font(.subheadline)
                    .fontWeight(.semibold)
                Text(subtitle)
                    .font(.caption)
                    .foregroundColor(.secondary)
            }
            Spacer()
            Image(systemName: "checkmark.circle.fill")
                .foregroundColor(.green)
        }
        .padding(.horizontal)
    }
}
