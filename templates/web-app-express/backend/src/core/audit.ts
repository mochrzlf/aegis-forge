import { query } from "./db.js";
import { hashIdentifier } from "./crypto.js";

export interface AuditLogEntry {
  userId?: string;
  actorRole: string;
  action: string;
  resourceType: string;
  resourceId?: string;
  ipAddress: string;
  status: "SUCCESS" | "FAILURE" | "DENIED";
  details?: Record<string, any>;
}

export async function logAuditEvent(entry: AuditLogEntry): Promise<void> {
  const userIdHash = entry.userId ? hashIdentifier(entry.userId) : "anonymous";
  const ipHash = hashIdentifier(entry.ipAddress || "unknown");

  try {
    await query(
      `INSERT INTO audit_logs 
       (user_id_hash, actor_role, action, resource_type, resource_id, ip_hash, status, details)
       VALUES ($1, $2, $3, $4, $5, $6, $7, $8)`,
      [
        userIdHash,
        entry.actorRole,
        entry.action,
        entry.resourceType,
        entry.resourceId || null,
        ipHash,
        entry.status,
        JSON.stringify(entry.details || {}),
      ]
    );
  } catch (err) {
    if (process.env.NODE_ENV !== "test") {
      console.error("❌ Failed to write immutable audit log:", err);
    }
  }
}
