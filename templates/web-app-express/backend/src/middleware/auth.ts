import { Request, Response, NextFunction } from "express";
import { verifyAccessToken } from "../core/crypto.js";
import { query } from "../core/db.js";
import { errorResponse } from "../core/envelope.js";

declare global {
  namespace Express {
    interface Request {
      user?: {
        id: string;
        email: string;
        role: string;
        status: string;
      };
    }
  }
}

export async function requireAuth(req: Request, res: Response, next: NextFunction) {
  const authHeader = req.headers.authorization;
  if (!authHeader || !authHeader.startsWith("Bearer ")) {
    return errorResponse(res, "UNAUTHORIZED", "Missing or invalid authorization header", 401);
  }

  const token = authHeader.split(" ")[1];
  try {
    const decoded = verifyAccessToken(token);
    if (!decoded || !decoded.userId) {
      return errorResponse(res, "UNAUTHORIZED", "Invalid token claims", 401);
    }

    // In-memory or DB lookup
    const result = await query("SELECT id, email, role, status FROM users WHERE id = $1", [
      decoded.userId,
    ]);

    if (result.rows.length === 0) {
      return errorResponse(res, "USER_NOT_FOUND", "User not found", 404);
    }

    const user = result.rows[0];

    // JML Session Kill-switch check
    if (user.status !== "active") {
      return errorResponse(
        res,
        "ACCOUNT_DISABLED",
        "Account is inactive, suspended, or terminated",
        403
      );
    }

    req.user = user;
    next();
  } catch (err) {
    return errorResponse(res, "INVALID_TOKEN", "Expired or invalid access token", 401);
  }
}

export function requireRole(...roles: string[]) {
  return (req: Request, res: Response, next: NextFunction) => {
    if (!req.user) {
      return errorResponse(res, "UNAUTHORIZED", "Authentication required", 401);
    }

    if (!roles.includes(req.user.role)) {
      return errorResponse(
        res,
        "FORBIDDEN",
        `Access denied. Requires one of roles: [${roles.join(", ")}]`,
        403
      );
    }

    next();
  };
}
