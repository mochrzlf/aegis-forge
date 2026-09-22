import { Request, Response, NextFunction } from "express";
import { redis } from "../core/redis.js";
import { hashIdentifier } from "../core/crypto.js";
import { errorResponse } from "../core/envelope.js";

export function createRateLimiter(options: {
  windowSeconds: number;
  maxRequests: number;
  prefix: string;
}) {
  return async (req: Request, res: Response, next: NextFunction) => {
    const forwarded = req.headers["x-forwarded-for"];
    const ip = (typeof forwarded === "string" ? forwarded.split(",")[0].trim() : null) || req.ip || req.socket.remoteAddress || "127.0.0.1";
    const ipHash = hashIdentifier(ip);
    const key = `ratelimit:${options.prefix}:${ipHash}`;

    try {
      const count = await redis.incr(key);
      if (count === 1) {
        await redis.expire(key, options.windowSeconds);
      }

      const ttl = await redis.ttl(key);
      res.setHeader("X-RateLimit-Limit", options.maxRequests.toString());
      res.setHeader("X-RateLimit-Remaining", Math.max(0, options.maxRequests - count).toString());

      if (count > options.maxRequests) {
        res.setHeader("Retry-After", (ttl > 0 ? ttl : options.windowSeconds).toString());
        return errorResponse(
          res,
          "RATE_LIMITED",
          "Too many requests. Please slow down.",
          429,
          { retryAfter: ttl > 0 ? ttl : options.windowSeconds }
        );
      }

      next();
    } catch (err) {
      next();
    }
  };
}
