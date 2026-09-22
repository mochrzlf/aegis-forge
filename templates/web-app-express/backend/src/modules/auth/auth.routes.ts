import { Router } from "express";
import { AuthController } from "./auth.controller.js";
import { requireAuth } from "../../middleware/auth.js";
import { createRateLimiter } from "../../middleware/rateLimiter.js";

const router = Router();

const loginLimiter = createRateLimiter({
  windowSeconds: 60,
  maxRequests: 5,
  prefix: "auth-login",
});

const registerLimiter = createRateLimiter({
  windowSeconds: 60,
  maxRequests: 10,
  prefix: "auth-register",
});

router.post("/register", registerLimiter, AuthController.register);
router.post("/login", loginLimiter, AuthController.login);
router.post("/refresh", AuthController.refresh);
router.post("/logout", AuthController.logout);
router.get("/me", requireAuth, AuthController.me);

export const authRouter = router;
