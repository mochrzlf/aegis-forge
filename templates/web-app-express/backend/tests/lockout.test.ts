import { describe, it, expect, beforeEach } from "vitest";
import request from "supertest";
import { app } from "../src/app.js";
import { testDb } from "./mockDb.js";
import { redis } from "../src/core/redis.js";
import { hashPassword, createAccessToken } from "../src/core/crypto.js";

describe("Account Lockout Protection (ADR-004)", () => {
  let targetUser: any;
  let adminUser: any;
  let adminToken: string;

  beforeEach(async () => {
    await redis.flushall();
    testDb.reset();
    testDb.install();

    const hashedPassword = await hashPassword("ValidPassword123!");
    targetUser = {
      id: "usr_target_123",
      email: "victim@example.com",
      password_hash: hashedPassword,
      role: "user",
      status: "active",
      failed_login_attempts: 0,
      locked_until: null,
      created_at: new Date(),
    };

    adminUser = {
      id: "usr_admin_999",
      email: "admin@example.com",
      password_hash: hashedPassword,
      role: "admin",
      status: "active",
      failed_login_attempts: 0,
      locked_until: null,
      created_at: new Date(),
    };

    testDb.users.push(targetUser, adminUser);
    adminToken = createAccessToken({ userId: adminUser.id, role: adminUser.role });
  });

  it("locks account after 5 consecutive failed login attempts (423 Locked)", async () => {
    // 4 failed attempts
    for (let i = 0; i < 4; i++) {
      const res = await request(app)
        .post("/auth/login")
        .send({ email: targetUser.email, password: "WrongPassword!" });
      expect(res.status).toBe(401);
      expect(res.body.error.code).toBe("INVALID_CREDENTIALS");
    }

    // 5th attempt -> triggers lockout
    const fifthRes = await request(app)
      .post("/auth/login")
      .send({ email: targetUser.email, password: "WrongPassword!" });

    expect(fifthRes.status).toBe(423);
    expect(fifthRes.body.error.code).toBe("ACCOUNT_LOCKED");
    expect(fifthRes.body.error.message).toContain("Account locked for 15 minutes");

    // Flush IP limiter to isolate account lockout verification
    await redis.flushall();

    // 6th attempt (even with CORRECT password) is rejected while locked
    const sixthRes = await request(app)
      .post("/auth/login")
      .send({ email: targetUser.email, password: "ValidPassword123!" });

    expect(sixthRes.status).toBe(423);
    expect(sixthRes.body.error.code).toBe("ACCOUNT_LOCKED");
  });

  it("allows admin to manually unlock a locked user", async () => {
    // Manually set user as locked
    targetUser.failed_login_attempts = 5;
    targetUser.locked_until = new Date(Date.now() + 10 * 60 * 1000);

    // Admin unlocks user
    const unlockRes = await request(app)
      .post(`/users/${targetUser.id}/unlock`)
      .set("Authorization", `Bearer ${adminToken}`);

    expect(unlockRes.status).toBe(200);
    expect(unlockRes.body.success).toBe(true);

    // User can now log in with correct password
    const loginRes = await request(app)
      .post("/auth/login")
      .send({ email: targetUser.email, password: "ValidPassword123!" });

    expect(loginRes.status).toBe(200);
    expect(loginRes.body.success).toBe(true);
    expect(loginRes.body.data.accessToken).toBeDefined();
  });
});
