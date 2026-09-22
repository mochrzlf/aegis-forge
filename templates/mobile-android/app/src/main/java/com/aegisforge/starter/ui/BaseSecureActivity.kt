package com.aegisforge.starter.ui

import android.os.Bundle
import android.view.WindowManager
import androidx.appcompat.app.AppCompatActivity

/**
 * Base Activity enforcing banking-grade screen protection via WindowManager.FLAG_SECURE.
 *
 * Prevents:
 * 1. Screen captures (screenshots) and screen recording.
 * 2. Visual snooping through Android Recent Apps switcher thumbnail previews.
 * 3. Video projection interception over insecure displays.
 */
abstract class BaseSecureActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        applySecurityFlags()
    }

    private fun applySecurityFlags() {
        window.setFlags(
            WindowManager.LayoutParams.FLAG_SECURE,
            WindowManager.LayoutParams.FLAG_SECURE
        )
    }
}
