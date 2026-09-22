import express, { Request, Response, NextFunction } from "express";
import helmet from "helmet";
import cors from "cors";
import cookieParser from "cookie-parser";
import { env } from "./config/index.js";
import { errorResponse } from "./core/envelope.js";
import { healthRouter } from "./modules/health/health.routes.js";
import { authRouter } from "./modules/auth/auth.routes.js";
import { usersRouter } from "./modules/users/users.routes.js";
import { approvalsRouter } from "./modules/approvals/approvals.routes.js";

const app = express();

// 1. Security Headers & Middleware
app.use(helmet());
app.use(
  cors({
    origin: env.CORS_ORIGIN === "*" ? true : env.CORS_ORIGIN,
    credentials: true,
  })
);
app.use(cookieParser());
app.use(express.json());

// 2. Route Mounts
app.use("/health", healthRouter);
app.use("/auth", authRouter);
app.use("/users", usersRouter);
app.use("/approvals", approvalsRouter);

// 3. 404 Handler
app.use((_req: Request, res: Response) => {
  return errorResponse(res, "NOT_FOUND", "The requested resource was not found", 404);
});

// 4. Global Error Handler
app.use((err: any, _req: Request, res: Response, _next: NextFunction) => {
  if (env.NODE_ENV !== "test") {
    console.error("❌ Unhandled server error:", err);
  }
  return errorResponse(
    res,
    err.code || "INTERNAL_SERVER_ERROR",
    err.message || "An unexpected error occurred",
    err.statusCode || 500
  );
});

export { app };
