package com.aegisforge.starter.ui

import android.os.Bundle
import android.widget.TextView
import com.aegisforge.starter.security.SecureStorage

/**
 * Main Activity demonstrating BaseSecureActivity usage and SecureStorage interaction.
 */
class MainActivity : BaseSecureActivity() {

    private lateinit var secureStorage: SecureStorage

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        secureStorage = SecureStorage(this)

        val textView = TextView(this).apply {
            text = "Aegis Forge Mobile Starter\n[FLAG_SECURE Active]\n[Keystore Storage Ready]"
            textSize = 18f
            setPadding(48, 48, 48, 48)
        }

        setContentView(textView)
    }
}
