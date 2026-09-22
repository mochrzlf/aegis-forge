import { describe, it, expect, beforeEach } from "vitest";
import request from "supertest";
import { app } from "../src/app.js";
import { redis } from "../src/core/redis.js";

describe("Rate Limiting (Sliding Window)", () => {
  beforeEach(async () => {
    await redis.flushall();
  });

  it("enforces sliding-window rate limit on login endpoint (max 5 req/min)", async () => {
    // 5 allowed attempts
    for (let i = 0; i < 5; i++) {
      const res = await request(app)
        .post("/auth/login")
        .set("X-Forwarded-For", "192.168.1.100")
        .send({ email: "test@example.com", password: "SomePassword" });

      expect(res.status).not.toBe(429);
      expect(res.headers["x-ratelimit-limit"]).toBe("5");
    }

    // 6th attempt -> 429 Rate Limited
    const blockedRes = await request(app)
      .post("/auth/login")
      .set("X-Forwarded-For", "192.168.1.100")
      .send({ email: "test@example.com", password: "SomePassword" });

    expect(blockedRes.status).toBe(429);
    expect(blockedRes.body.error.code).toBe("RATE_LIMITED");
    expect(blockedRes.headers["retry-after"]).toBeDefined();

    // Distinct IP is not affected
    const otherIpRes = await request(app)
      .post("/auth/login")
      .set("X-Forwarded-For", "192.168.1.101")
      .send({ email: "test@example.com", password: "SomePassword" });

    expect(otherIpRes.status).not.toBe(429);
  });
});
