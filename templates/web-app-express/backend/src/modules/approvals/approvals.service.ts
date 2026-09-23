import { query } from "../../core/db.js";
import { logAuditEvent } from "../../core/audit.js";

export class ApprovalsService {
  static async createApproval(actionType: string, payload: any, maker: any, ip: string) {
    const res = await query(
      `INSERT INTO approval_requests (maker_user_id, action_type, payload, status)
       VALUES ($1, $2, $3, 'pending')
       RETURNING id, maker_user_id, action_type, payload, status, created_at`,
      [maker.id, actionType, JSON.stringify(payload || {})]
    );

    const approval = res.rows[0];
    await logAuditEvent({
      userId: maker.id,
      actorRole: maker.role,
      action: "APPROVAL_REQUEST_CREATED",
      resourceType: "approval_request",
      resourceId: approval.id,
      ipAddress: ip,
      status: "SUCCESS",
      details: { actionType },
    });

    return approval;
  }

  static async listApprovals(status?: string) {
    let sql = "SELECT * FROM approval_requests";
    const params: any[] = [];
    if (status) {
      sql += " WHERE status = $1";
      params.push(status);
    }
    sql += " ORDER BY created_at DESC";

    const res = await query(sql, params);
    return res.rows;
  }

  static async reviewApproval(
    approvalId: string,
    decision: "approved" | "rejected",
    reason: string,
    checker: any,
    ip: string
  ) {
    const res = await query("SELECT * FROM approval_requests WHERE id = $1", [approvalId]);
    if (res.rows.length === 0) {
      throw { statusCode: 404, code: "APPROVAL_NOT_FOUND", message: "Approval request not found" };
    }

    const approval = res.rows[0];

    if (approval.status !== "pending") {
      throw {
        statusCode: 400,
        code: "ALREADY_PROCESSED",
        message: `Approval request is already ${approval.status}`,
      };
    }

    // 🔒 Dual Control / Maker-Checker Rule (ADR-006)
    if (approval.maker_user_id === checker.id) {
      await logAuditEvent({
        userId: checker.id,
        actorRole: checker.role,
        action: "MAKER_CHECKER_SELF_APPROVAL_ATTEMPT",
        resourceType: "approval_request",
        resourceId: approvalId,
        ipAddress: ip,
        status: "DENIED",
      });
      throw {
        statusCode: 403,
        code: "FORBIDDEN",
        message: "Dual Control violation: The maker is strictly forbidden from approving their own request.",
      };
    }

    // Update in database (also guaranteed by DB check constraint: chk_maker_not_checker)
    const updateRes = await query(
      `UPDATE approval_requests 
       SET checker_user_id = $1, status = $2, decision_reason = $3, reviewed_at = NOW()
       WHERE id = $4
       RETURNING *`,
      [checker.id, decision, reason, approvalId]
    );

    await logAuditEvent({
      userId: checker.id,
      actorRole: checker.role,
      action: `APPROVAL_REQUEST_${decision.toUpperCase()}`,
      resourceType: "approval_request",
      resourceId: approvalId,
      ipAddress: ip,
      status: "SUCCESS",
      details: { decision, reason },
    });

    return updateRes.rows[0];
  }
}
