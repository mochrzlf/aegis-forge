import { Request, Response } from "express";
import { AuthService } from "./auth.service.js";
import { registerSchema, loginSchema } from "./auth.schemas.js";
import { successResponse, errorResponse } from "../../core/envelope.js";
import { env } from "../../config/index.js";

const COOKIE_OPTIONS = {
  httpOnly: true,
  secure: env.NODE_ENV === "production",
  sameSite: "strict" as const,
  maxAge: 7 * 24 * 60 * 60 * 1000,
  path: "/auth",
};

export class AuthController {
  static async register(req: Request, res: Response) {
    const parse = registerSchema.safeParse(req.body);
    if (!parse.success) {
      return errorResponse(res, "VALIDATION_ERROR", "Invalid input data", 422, parse.error.format());
    }

    try {
      const user = await AuthService.register(
        parse.data.email,
        parse.data.password,
        req.ip || "127.0.0.1"
      );
      return successResponse(res, user, {}, 201);
    } catch (err: any) {
      return errorResponse(res, err.code || "REGISTRATION_FAILED", err.message, err.statusCode || 400);
    }
  }

  static async login(req: Request, res: Response) {
    const parse = loginSchema.safeParse(req.body);
    if (!parse.success) {
      return errorResponse(res, "VALIDATION_ERROR", "Invalid input data", 422, parse.error.format());
    }

    try {
      const result = await AuthService.login(
        parse.data.email,
        parse.data.password,
        req.ip || "127.0.0.1"
      );

      res.cookie("refreshToken", result.refreshToken, COOKIE_OPTIONS);
      return successResponse(res, {
        accessToken: result.accessToken,
        user: result.user,
      });
    } catch (err: any) {
      return errorResponse(
        res,
        err.code || "LOGIN_FAILED",
        err.message,
        err.statusCode || 401,
        err.details
      );
    }
  }

  static async refresh(req: Request, res: Response) {
    const refreshToken = req.cookies?.refreshToken;
    if (!refreshToken) {
      return errorResponse(res, "UNAUTHORIZED", "Missing refresh token cookie", 401);
    }

    try {
      const result = await AuthService.refresh(refreshToken, req.ip || "127.0.0.1");
      res.cookie("refreshToken", result.newRefreshToken, COOKIE_OPTIONS);
      return successResponse(res, {
        accessToken: result.accessToken,
      });
    } catch (err: any) {
      res.clearCookie("refreshToken", { path: "/auth" });
      return errorResponse(res, err.code || "REFRESH_FAILED", err.message, err.statusCode || 401);
    }
  }

  static async logout(req: Request, res: Response) {
    const refreshToken = req.cookies?.refreshToken;
    await AuthService.logout(refreshToken);
    res.clearCookie("refreshToken", { path: "/auth" });
    return successResponse(res, { message: "Logged out successfully" });
  }

  static async me(req: Request, res: Response) {
    return successResponse(res, req.user);
  }
}
