import crypto from "crypto";
import { query } from "../../core/db.js";
import {
  hashPassword,
  verifyPassword,
  createAccessToken,
  createRefreshToken,
  verifyRefreshToken,
  hashToken,
} from "../../core/crypto.js";
import { logAuditEvent } from "../../core/audit.js";

export class AuthService {
  static async register(email: string, password: string, ip: string) {
    const existing = await query("SELECT id FROM users WHERE email = $1", [email]);
    if (existing.rows.length > 0) {
      throw { statusCode: 409, code: "EMAIL_EXISTS", message: "Email is already registered" };
    }

    const hashedPassword = await hashPassword(password);
    const result = await query(
      `INSERT INTO users (email, password_hash, role, status)
       VALUES ($1, $2, 'user', 'active')
       RETURNING id, email, role, status, created_at`,
      [email, hashedPassword]
    );

    const newUser = result.rows[0];
    await logAuditEvent({
      userId: newUser.id,
      actorRole: "user",
      action: "USER_REGISTERED",
      resourceType: "user",
      resourceId: newUser.id,
      ipAddress: ip,
      status: "SUCCESS",
    });

    return newUser;
  }

  static async login(email: string, password: string, ip: string) {
    const userRes = await query(
      `SELECT id, email, password_hash, role, status, failed_login_attempts, locked_until 
       FROM users WHERE email = $1`,
      [email]
    );

    if (userRes.rows.length === 0) {
      throw { statusCode: 401, code: "INVALID_CREDENTIALS", message: "Invalid email or password" };
    }

    const user = userRes.rows[0];

    // 1. Account Lockout check (ADR-004)
    if (user.locked_until && new Date(user.locked_until) > new Date()) {
      const remainingSeconds = Math.ceil(
        (new Date(user.locked_until).getTime() - Date.now()) / 1000
      );
      throw {
        statusCode: 423,
        code: "ACCOUNT_LOCKED",
        message: `Account is temporarily locked. Try again in ${remainingSeconds} seconds.`,
        details: { retryAfter: remainingSeconds },
      };
    }

    // 2. JML Status check (ADR-005)
    if (user.status !== "active") {
      throw {
        statusCode: 403,
        code: "ACCOUNT_DISABLED",
        message: "Account is suspended or terminated",
      };
    }

    // 3. Password Verification
    const isMatch = await verifyPassword(password, user.password_hash);
    if (!isMatch) {
      const attempts = user.failed_login_attempts + 1;
      let lockedUntil: Date | null = null;

      if (attempts >= 5) {
        lockedUntil = new Date(Date.now() + 15 * 60 * 1000); // 15 min lock
        await query(
          "UPDATE users SET failed_login_attempts = $1, locked_until = $2 WHERE id = $3",
          [attempts, lockedUntil, user.id]
        );
        await logAuditEvent({
          userId: user.id,
          actorRole: user.role,
          action: "ACCOUNT_LOCKED_FAILED_ATTEMPTS",
          resourceType: "user",
          resourceId: user.id,
          ipAddress: ip,
          status: "FAILURE",
          details: { attempts },
        });
        throw {
          statusCode: 423,
          code: "ACCOUNT_LOCKED",
          message: "Account locked for 15 minutes due to 5 consecutive failed login attempts.",
          details: { retryAfter: 900 },
        };
      } else {
        await query("UPDATE users SET failed_login_attempts = $1 WHERE id = $2", [
          attempts,
          user.id,
        ]);
        await logAuditEvent({
          userId: user.id,
          actorRole: user.role,
          action: "LOGIN_FAILED",
          resourceType: "user",
          resourceId: user.id,
          ipAddress: ip,
          status: "FAILURE",
          details: { attempts },
        });
        throw {
          statusCode: 401,
          code: "INVALID_CREDENTIALS",
          message: "Invalid email or password",
        };
      }
    }

    // 4. Success — Reset lockout counters
    await query("UPDATE users SET failed_login_attempts = 0, locked_until = NULL WHERE id = $1", [
      user.id,
    ]);

    // 5. Issue Tokens & Setup RTR Session
    const familyId = crypto.randomUUID();
    const accessToken = createAccessToken({ userId: user.id, role: user.role });
    const refreshToken = createRefreshToken({
      userId: user.id,
      familyId,
      jti: crypto.randomUUID(),
    });
    const tokenHash = hashToken(refreshToken);
    const expiresAt = new Date(Date.now() + 7 * 24 * 60 * 60 * 1000);

    await query(
      `INSERT INTO refresh_tokens (user_id, token_hash, family_id, expires_at)
       VALUES ($1, $2, $3, $4)`,
      [user.id, tokenHash, familyId, expiresAt]
    );

    await logAuditEvent({
      userId: user.id,
      actorRole: user.role,
      action: "LOGIN_SUCCESS",
      resourceType: "user",
      resourceId: user.id,
      ipAddress: ip,
      status: "SUCCESS",
    });

    return {
      accessToken,
      refreshToken,
      user: {
        id: user.id,
        email: user.email,
        role: user.role,
        status: user.status,
      },
    };
  }

  static async refresh(oldRefreshToken: string, ip: string) {
    let decoded: any;
    try {
      decoded = verifyRefreshToken(oldRefreshToken);
    } catch (err) {
      throw { statusCode: 401, code: "INVALID_TOKEN", message: "Invalid or expired refresh token" };
    }

    const tokenHash = hashToken(oldRefreshToken);
    const tokenRes = await query(
      "SELECT id, user_id, family_id, is_revoked FROM refresh_tokens WHERE token_hash = $1",
      [tokenHash]
    );

    if (tokenRes.rows.length === 0) {
      throw { statusCode: 401, code: "INVALID_TOKEN", message: "Token not found" };
    }

    const record = tokenRes.rows[0];

    // 🚨 RTR Replay Detection: An already-revoked token was presented!
    if (record.is_revoked) {
      // Revoke all tokens in this family immediately!
      await query("UPDATE refresh_tokens SET is_revoked = TRUE WHERE family_id = $1", [
        record.family_id,
      ]);
      await logAuditEvent({
        userId: record.user_id,
        actorRole: "user",
        action: "TOKEN_REPLAY_DETECTED_ALL_REVOKED",
        resourceType: "refresh_token",
        resourceId: record.family_id,
        ipAddress: ip,
        status: "DENIED",
      });
      throw {
        statusCode: 401,
        code: "TOKEN_REPLAY_DETECTED",
        message: "Security violation: Compromised token reuse detected. All active sessions revoked.",
      };
    }

    // Revoke the old token (Single-use rotation)
    await query("UPDATE refresh_tokens SET is_revoked = TRUE WHERE id = $1", [record.id]);

    // Check user status
    const userRes = await query("SELECT id, role, status FROM users WHERE id = $1", [
      record.user_id,
    ]);
    if (userRes.rows.length === 0 || userRes.rows[0].status !== "active") {
      throw { statusCode: 403, code: "ACCOUNT_DISABLED", message: "Account is no longer active" };
    }

    const user = userRes.rows[0];

    // Issue new rotated pair keeping the same family
    const accessToken = createAccessToken({ userId: user.id, role: user.role });
    const newRefreshToken = createRefreshToken({
      userId: user.id,
      familyId: record.family_id,
      jti: crypto.randomUUID(),
    });
    const newTokenHash = hashToken(newRefreshToken);
    const expiresAt = new Date(Date.now() + 7 * 24 * 60 * 60 * 1000);

    await query(
      `INSERT INTO refresh_tokens (user_id, token_hash, family_id, expires_at)
       VALUES ($1, $2, $3, $4)`,
      [user.id, newTokenHash, record.family_id, expiresAt]
    );

    await logAuditEvent({
      userId: user.id,
      actorRole: user.role,
      action: "TOKEN_ROTATION_SUCCESS",
      resourceType: "refresh_token",
      ipAddress: ip,
      status: "SUCCESS",
    });

    return { accessToken, newRefreshToken };
  }

  static async logout(refreshToken?: string) {
    if (refreshToken) {
      const tokenHash = hashToken(refreshToken);
      await query("UPDATE refresh_tokens SET is_revoked = TRUE WHERE token_hash = $1", [tokenHash]);
    }
  }
}
