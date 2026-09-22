import { describe, it, expect, beforeEach } from "vitest";
import request from "supertest";
import { app } from "../src/app.js";
import { testDb } from "./mockDb.js";
import { createAccessToken } from "../src/core/crypto.js";

describe("JML Instant Session Kill-Switch (ADR-005)", () => {
  let adminUser: any;
  let regularUser: any;
  let adminToken: string;
  let userToken: string;

  beforeEach(() => {
    testDb.reset();
    testDb.install();

    adminUser = {
      id: "usr_admin_001",
      email: "admin@enterprise.com",
      password_hash: "hash",
      role: "admin",
      status: "active",
      failed_login_attempts: 0,
      locked_until: null,
      created_at: new Date(),
    };

    regularUser = {
      id: "usr_employee_002",
      email: "employee@enterprise.com",
      password_hash: "hash",
      role: "user",
      status: "active",
      failed_login_attempts: 0,
      locked_until: null,
      created_at: new Date(),
    };

    testDb.users.push(adminUser, regularUser);

    // Setup active refresh token session for regular user
    testDb.refreshTokens.push({
      id: "tok_session_1",
      user_id: regularUser.id,
      token_hash: "hash_active_token",
      family_id: "fam_001",
      is_revoked: false,
      expires_at: new Date(Date.now() + 86400000),
    });

    adminToken = createAccessToken({ userId: adminUser.id, role: adminUser.role });
    userToken = createAccessToken({ userId: regularUser.id, role: regularUser.role });
  });

  it("admin revokes all sessions upon updating status to suspended", async () => {
    // 1. Admin suspends employee (Leaver / Terminated)
    const res = await request(app)
      .put(`/users/${regularUser.id}/status`)
      .set("Authorization", `Bearer ${adminToken}`)
      .send({ status: "suspended" });

    expect(res.status).toBe(200);
    expect(res.body.success).toBe(true);
    expect(res.body.data.status).toBe("suspended");
    expect(res.body.data.revokedSessions).toBe(1);

    // Verify token in DB was immediately revoked
    const token = testDb.refreshTokens.find((t) => t.user_id === regularUser.id);
    expect(token?.is_revoked).toBe(true);

    // 2. Employee subsequent access is immediately blocked by kill-switch
    const accessRes = await request(app)
      .get("/auth/me")
      .set("Authorization", `Bearer ${userToken}`);

    expect(accessRes.status).toBe(403);
    expect(accessRes.body.error.code).toBe("ACCOUNT_DISABLED");
  });

  it("forbids administrator from suspending themselves", async () => {
    const res = await request(app)
      .put(`/users/${adminUser.id}/status`)
      .set("Authorization", `Bearer ${adminToken}`)
      .send({ status: "suspended" });

    expect(res.status).toBe(400);
    expect(res.body.error.code).toBe("INVALID_ACTION");
    expect(res.body.error.message).toContain("cannot suspend or terminate their own account");
  });
});
