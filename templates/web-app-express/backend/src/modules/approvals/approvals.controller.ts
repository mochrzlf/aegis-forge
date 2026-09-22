import { Request, Response } from "express";
import { ApprovalsService } from "./approvals.service.js";
import { successResponse, errorResponse } from "../../core/envelope.js";

export class ApprovalsController {
  static async create(req: Request, res: Response) {
    const { action_type, payload } = req.body;
    if (!action_type) {
      return errorResponse(res, "VALIDATION_ERROR", "Field 'action_type' is required", 422);
    }

    try {
      const approval = await ApprovalsService.createApproval(
        action_type,
        payload,
        req.user,
        req.ip || "127.0.0.1"
      );
      return successResponse(res, approval, {}, 201);
    } catch (err: any) {
      return errorResponse(res, err.code || "APPROVAL_ERROR", err.message, err.statusCode || 400);
    }
  }

  static async list(req: Request, res: Response) {
    try {
      const approvals = await ApprovalsService.listApprovals(req.query.status as string);
      return successResponse(res, approvals);
    } catch (err: any) {
      return errorResponse(res, err.code || "APPROVAL_ERROR", err.message, err.statusCode || 400);
    }
  }

  static async review(req: Request, res: Response) {
    const { decision, reason } = req.body;
    if (!decision || !["approved", "rejected"].includes(decision)) {
      return errorResponse(res, "VALIDATION_ERROR", "Field 'decision' must be 'approved' or 'rejected'", 422);
    }

    try {
      const approval = await ApprovalsService.reviewApproval(
        req.params.id,
        decision,
        reason || "",
        req.user,
        req.ip || "127.0.0.1"
      );
      return successResponse(res, approval);
    } catch (err: any) {
      return errorResponse(res, err.code || "APPROVAL_ERROR", err.message, err.statusCode || 400);
    }
  }
}
