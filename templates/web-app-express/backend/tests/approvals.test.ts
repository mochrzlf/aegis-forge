import { describe, it, expect, beforeEach } from "vitest";
import request from "supertest";
import { app } from "../src/app.js";
import { testDb } from "./mockDb.js";
import { createAccessToken } from "../src/core/crypto.js";

describe("Maker-Checker / Dual Control (Approvals)", () => {
  const makerUser = {
    id: "user_maker_123",
    email: "maker@example.com",
    password_hash: "hashed",
    role: "user",
    status: "active",
    failed_login_attempts: 0,
    locked_until: null,
    created_at: new Date(),
  };

  const checkerUser = {
    id: "user_checker_456",
    email: "checker@example.com",
    password_hash: "hashed",
    role: "admin",
    status: "active",
    failed_login_attempts: 0,
    locked_until: null,
    created_at: new Date(),
  };

  let makerToken: string;
  let checkerToken: string;

  beforeEach(() => {
    testDb.reset();
    testDb.install();
    testDb.users.push(makerUser, checkerUser);
    makerToken = createAccessToken({ userId: makerUser.id, role: makerUser.role });
    checkerToken = createAccessToken({ userId: checkerUser.id, role: checkerUser.role });
  });

  it("allows maker to create a pending approval request", async () => {
    const res = await request(app)
      .post("/approvals")
      .set("Authorization", `Bearer ${makerToken}`)
      .send({
        action_type: "role_change",
        payload: { target_user: "u999", new_role: "admin" },
      });

    expect(res.status).toBe(201);
    expect(res.body.success).toBe(true);
    expect(res.body.data.status).toBe("pending");
    expect(res.body.data.maker_user_id).toBe(makerUser.id);
  });

  it("strictly forbids maker from approving their own request (Four-Eyes Principle)", async () => {
    // 1. Maker creates request
    const createRes = await request(app)
      .post("/approvals")
      .set("Authorization", `Bearer ${makerToken}`)
      .send({
        action_type: "disbursement",
        payload: { amount: 10000000 },
      });

    const approvalId = createRes.body.data.id;

    // 2. Maker tries to review/approve their own request
    const reviewRes = await request(app)
      .post(`/approvals/${approvalId}/review`)
      .set("Authorization", `Bearer ${makerToken}`)
      .send({
        decision: "approved",
        reason: "Self approval attempt",
      });

    expect(reviewRes.status).toBe(403);
    expect(reviewRes.body.success).toBe(false);
    expect(reviewRes.body.error.message).toContain("Dual Control violation");
  });

  it("allows a different checker to review and approve the request", async () => {
    // 1. Maker creates request
    const createRes = await request(app)
      .post("/approvals")
      .set("Authorization", `Bearer ${makerToken}`)
      .send({
        action_type: "disbursement",
        payload: { amount: 5000000 },
      });

    const approvalId = createRes.body.data.id;

    // 2. Checker reviews request
    const reviewRes = await request(app)
      .post(`/approvals/${approvalId}/review`)
      .set("Authorization", `Bearer ${checkerToken}`)
      .send({
        decision: "approved",
        reason: "Verified and compliant with guidelines",
      });

    expect(reviewRes.status).toBe(200);
    expect(reviewRes.body.success).toBe(true);
    expect(reviewRes.body.data.status).toBe("approved");
    expect(reviewRes.body.data.checker_user_id).toBe(checkerUser.id);
  });
});
