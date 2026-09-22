import { Router } from "express";
import { UsersController } from "./users.controller.js";
import { requireAuth, requireRole } from "../../middleware/auth.js";

const router = Router();

router.get("/:id", requireAuth, UsersController.getUser);
router.put("/:id/status", requireAuth, requireRole("admin"), UsersController.updateStatus);
router.post("/:id/unlock", requireAuth, requireRole("admin"), UsersController.unlockUser);

export const usersRouter = router;
