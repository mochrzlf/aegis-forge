import { describe, it, expect, beforeEach } from "vitest";
import request from "supertest";
import { app } from "../src/app.js";
import { testDb } from "./mockDb.js";
import { redis } from "../src/core/redis.js";

describe("Authentication, Refresh Token Rotation & Replay Detection", () => {
  beforeEach(async () => {
    await redis.flushall();
    testDb.reset();
    testDb.install();
  });

  it("completes registration, login with HttpOnly cookie, token rotation, and replay detection", async () => {
    // 1. Register
    const regRes = await request(app)
      .post("/auth/register")
      .send({ email: "alice@example.com", password: "Password123!" });

    expect(regRes.status).toBe(201);
    expect(regRes.body.success).toBe(true);
    expect(regRes.body.data.email).toBe("alice@example.com");

    // 2. Login
    const loginRes = await request(app)
      .post("/auth/login")
      .send({ email: "alice@example.com", password: "Password123!" });

    expect(loginRes.status).toBe(200);
    expect(loginRes.body.success).toBe(true);
    expect(loginRes.body.data.accessToken).toBeDefined();

    // Verify Refresh Token was set ONLY in HttpOnly cookie
    const cookies = loginRes.headers["set-cookie"];
    expect(cookies).toBeDefined();
    const refreshCookie = (cookies as string[]).find((c) => c.startsWith("refreshToken="));
    expect(refreshCookie).toBeDefined();
    expect(refreshCookie).toContain("HttpOnly");
    expect(refreshCookie).toContain("SameSite=Strict");

    // 3. Normal Rotation (Refresh)
    const refreshRes = await request(app)
      .post("/auth/refresh")
      .set("Cookie", [refreshCookie!]);

    expect(refreshRes.status).toBe(200);
    expect(refreshRes.body.success).toBe(true);
    expect(refreshRes.body.data.accessToken).toBeDefined();

    const newCookies = refreshRes.headers["set-cookie"];
    const rotatedCookie = (newCookies as string[]).find((c) => c.startsWith("refreshToken="));
    expect(rotatedCookie).toBeDefined();
    expect(rotatedCookie).not.toBe(refreshCookie);

    // 4. 🚨 Replay Attack Simulation: Attacker tries to reuse the old revoked refreshCookie!
    const replayRes = await request(app)
      .post("/auth/refresh")
      .set("Cookie", [refreshCookie!]);

    expect(replayRes.status).toBe(401);
    expect(replayRes.body.error.code).toBe("TOKEN_REPLAY_DETECTED");
    expect(replayRes.body.error.message).toContain("Compromised token reuse detected");

    // 5. Verify the entire family was revoked: Even the new rotated token is now dead!
    const deadRes = await request(app)
      .post("/auth/refresh")
      .set("Cookie", [rotatedCookie!]);

    expect(deadRes.status).toBe(401);
  });
});
