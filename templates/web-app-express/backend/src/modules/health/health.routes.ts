import { Router, Request, Response } from "express";
import { pool } from "../../core/db.js";
import { redis } from "../../core/redis.js";
import { successResponse, errorResponse } from "../../core/envelope.js";

const router = Router();

router.get("/live", (_req: Request, res: Response) => {
  return successResponse(res, { status: "alive" });
});

router.get("/ready", async (_req: Request, res: Response) => {
  try {
    // 1. Check PostgreSQL
    await pool.query("SELECT 1");

    // 2. Check Redis
    await redis.ping();

    return successResponse(res, {
      status: "ready",
      components: {
        database: "healthy",
        cache: "healthy",
      },
    });
  } catch (err: any) {
    return errorResponse(res, "SERVICE_UNAVAILABLE", "Service dependency failure", 503, {
      error: err.message,
    });
  }
});

export const healthRouter = router;
