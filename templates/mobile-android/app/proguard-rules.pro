# Aegis Forge Android ProGuard & R8 Obfuscation Rules

# Preserve Security Crypto models & Keystore classes
-keep class androidx.security.crypto.** { *; }
-dontwarn androidx.security.crypto.**

# Preserve internal security wrapper names
-keep class com.aegisforge.starter.security.** { *; }

# Remove logging statements in release builds
-assumenosideeffects class android.util.Log {
    public static boolean isLoggable(java.lang.String, int);
    public static int v(...);
    public static int d(...);
    public static int i(...);
}

# Preserve standard Kotlin metadata
-keepattributes *Annotation*, Signature, InnerClasses, EnclosingMethod
