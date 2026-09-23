import { Request, Response } from "express";
import { UsersService } from "./users.service.js";
import { successResponse, errorResponse } from "../../core/envelope.js";

export class UsersController {
  static async getUser(req: Request, res: Response) {
    try {
      const user = await UsersService.getUser(req.params.id, req.user);
      return successResponse(res, user);
    } catch (err: any) {
      return errorResponse(res, err.code || "USER_ERROR", err.message, err.statusCode || 400);
    }
  }

  static async updateStatus(req: Request, res: Response) {
    const { status } = req.body;
    if (!status) {
      return errorResponse(res, "VALIDATION_ERROR", "Field 'status' is required", 422);
    }

    try {
      const result = await UsersService.updateStatus(
        req.params.id,
        status,
        req.user,
        req.ip || "127.0.0.1"
      );
      return successResponse(res, result);
    } catch (err: any) {
      return errorResponse(res, err.code || "UPDATE_ERROR", err.message, err.statusCode || 400);
    }
  }

  static async unlockUser(req: Request, res: Response) {
    try {
      const result = await UsersService.unlockUser(req.params.id, req.user, req.ip || "127.0.0.1");
      return successResponse(res, result);
    } catch (err: any) {
      return errorResponse(res, err.code || "UNLOCK_ERROR", err.message, err.statusCode || 400);
    }
  }
}
