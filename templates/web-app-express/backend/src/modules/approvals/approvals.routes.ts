import { Router } from "express";
import { ApprovalsController } from "./approvals.controller.js";
import { requireAuth } from "../../middleware/auth.js";

const router = Router();

router.post("/", requireAuth, ApprovalsController.create);
router.get("/", requireAuth, ApprovalsController.list);
router.post("/:id/review", requireAuth, ApprovalsController.review);

export const approvalsRouter = router;
