import { query } from "../../core/db.js";
import { logAuditEvent } from "../../core/audit.js";

export class UsersService {
  static async getUser(targetUserId: string, actor: any) {
    // Anti-IDOR: Users can only see their own profile unless they are an admin
    if (actor.id !== targetUserId && actor.role !== "admin") {
      throw {
        statusCode: 403,
        code: "FORBIDDEN",
        message: "You do not have permission to access this resource",
      };
    }

    const res = await query(
      "SELECT id, email, role, status, failed_login_attempts, locked_until, created_at FROM users WHERE id = $1",
      [targetUserId]
    );

    if (res.rows.length === 0) {
      throw { statusCode: 404, code: "USER_NOT_FOUND", message: "User not found" };
    }

    return res.rows[0];
  }

  static async updateStatus(targetUserId: string, newStatus: string, actor: any, ip: string) {
    // 1. Admin self-suspension guard (ADR-005)
    if (actor.id === targetUserId) {
      throw {
        statusCode: 400,
        code: "INVALID_ACTION",
        message: "Administrators cannot suspend or terminate their own account.",
      };
    }

    const validStatuses = ["active", "suspended", "terminated"];
    if (!validStatuses.includes(newStatus)) {
      throw {
        statusCode: 400,
        code: "INVALID_STATUS",
        message: `Status must be one of: ${validStatuses.join(", ")}`,
      };
    }

    const userRes = await query("SELECT id, status FROM users WHERE id = $1", [targetUserId]);
    if (userRes.rows.length === 0) {
      throw { statusCode: 404, code: "USER_NOT_FOUND", message: "User not found" };
    }

    await query("UPDATE users SET status = $1, updated_at = NOW() WHERE id = $2", [
      newStatus,
      targetUserId,
    ]);

    // 2. JML Instant Session Kill-Switch (ADR-005)
    let revokedTokensCount = 0;
    if (newStatus === "suspended" || newStatus === "terminated") {
      const revokeRes = await query(
        "UPDATE refresh_tokens SET is_revoked = TRUE WHERE user_id = $1 AND is_revoked = FALSE",
        [targetUserId]
      );
      revokedTokensCount = revokeRes.rowCount || 0;
    }

    await logAuditEvent({
      userId: actor.id,
      actorRole: actor.role,
      action: "USER_STATUS_UPDATED",
      resourceType: "user",
      resourceId: targetUserId,
      ipAddress: ip,
      status: "SUCCESS",
      details: { newStatus, revokedSessions: revokedTokensCount },
    });

    return {
      userId: targetUserId,
      status: newStatus,
      revokedSessions: revokedTokensCount,
    };
  }

  static async unlockUser(targetUserId: string, actor: any, ip: string) {
    const userRes = await query("SELECT id, email FROM users WHERE id = $1", [targetUserId]);
    if (userRes.rows.length === 0) {
      throw { statusCode: 404, code: "USER_NOT_FOUND", message: "User not found" };
    }

    await query(
      "UPDATE users SET failed_login_attempts = 0, locked_until = NULL, updated_at = NOW() WHERE id = $1",
      [targetUserId]
    );

    await logAuditEvent({
      userId: actor.id,
      actorRole: actor.role,
      action: "ACCOUNT_MANUALLY_UNLOCKED",
      resourceType: "user",
      resourceId: targetUserId,
      ipAddress: ip,
      status: "SUCCESS",
    });

    return { userId: targetUserId, locked: false };
  }
}
