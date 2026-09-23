import { vi } from "vitest";
import { pool } from "../src/core/db.js";

export interface MockUser {
  id: string;
  email: string;
  password_hash: string;
  role: string;
  status: string;
  failed_login_attempts: number;
  locked_until: Date | null;
  created_at: Date;
}

export interface MockToken {
  id: string;
  user_id: string;
  token_hash: string;
  family_id: string;
  is_revoked: boolean;
  expires_at: Date;
}

export interface MockApproval {
  id: string;
  maker_user_id: string;
  checker_user_id: string | null;
  action_type: string;
  payload: any;
  status: string;
  decision_reason: string | null;
  created_at: Date;
  reviewed_at: Date | null;
}

export class TestDatabase {
  users: MockUser[] = [];
  refreshTokens: MockToken[] = [];
  approvals: MockApproval[] = [];
  auditLogs: any[] = [];

  reset() {
    this.users = [];
    this.refreshTokens = [];
    this.approvals = [];
    this.auditLogs = [];
  }

  install() {
    vi.spyOn(pool, "query").mockImplementation(async (text: any, params?: any): Promise<any> => {
      const sql = (typeof text === "string" ? text : text.text || "").trim();

      // 1. Users Queries
      if (sql.includes("SELECT") && sql.includes("FROM users WHERE email = $1")) {
        const u = this.users.find((x) => x.email === params[0]);
        return { rows: u ? [u] : [], rowCount: u ? 1 : 0 };
      }

      if (sql.includes("SELECT") && sql.includes("FROM users WHERE id = $1")) {
        const u = this.users.find((x) => x.id === params[0]);
        return { rows: u ? [u] : [], rowCount: u ? 1 : 0 };
      }

      if (sql.includes("INSERT INTO users")) {
        const email = params[0];
        const password_hash = params[1];
        const role = params[2] || "user";
        const status = params[3] || "active";
        const newUser: MockUser = {
          id: `usr_${Date.now()}_${Math.random().toString(36).substring(2, 7)}`,
          email,
          password_hash,
          role,
          status,
          failed_login_attempts: 0,
          locked_until: null,
          created_at: new Date(),
        };
        this.users.push(newUser);
        return { rows: [newUser], rowCount: 1 };
      }

      if (sql.includes("UPDATE users SET failed_login_attempts = $1, locked_until = $2")) {
        const u = this.users.find((x) => x.id === params[2]);
        if (u) {
          u.failed_login_attempts = params[0];
          u.locked_until = params[1];
        }
        return { rows: [], rowCount: u ? 1 : 0 };
      }

      if (sql.includes("UPDATE users SET failed_login_attempts = $1 WHERE id = $2")) {
        const u = this.users.find((x) => x.id === params[1]);
        if (u) {
          u.failed_login_attempts = params[0];
        }
        return { rows: [], rowCount: u ? 1 : 0 };
      }

      if (sql.includes("UPDATE users SET failed_login_attempts = 0, locked_until = NULL")) {
        const u = this.users.find((x) => x.id === params[0]);
        if (u) {
          u.failed_login_attempts = 0;
          u.locked_until = null;
        }
        return { rows: [], rowCount: u ? 1 : 0 };
      }

      if (sql.includes("UPDATE users SET status = $1")) {
        const u = this.users.find((x) => x.id === params[1]);
        if (u) {
          u.status = params[0];
        }
        return { rows: [], rowCount: u ? 1 : 0 };
      }

      // 2. Refresh Tokens Queries
      if (sql.includes("INSERT INTO refresh_tokens")) {
        const user_id = params[0];
        const token_hash = params[1];
        const family_id = params[2];
        const expires_at = params[3];
        const token: MockToken = {
          id: `tok_${Date.now()}_${Math.random().toString(36).substring(2, 7)}`,
          user_id,
          token_hash,
          family_id,
          is_revoked: false,
          expires_at,
        };
        this.refreshTokens.push(token);
        return { rows: [token], rowCount: 1 };
      }

      if (sql.includes("SELECT") && sql.includes("FROM refresh_tokens WHERE token_hash = $1")) {
        const t = this.refreshTokens.find((x) => x.token_hash === params[0]);
        return { rows: t ? [t] : [], rowCount: t ? 1 : 0 };
      }

      if (sql.includes("UPDATE refresh_tokens SET is_revoked = TRUE WHERE family_id = $1")) {
        let count = 0;
        this.refreshTokens.forEach((t) => {
          if (t.family_id === params[0]) {
            t.is_revoked = true;
            count++;
          }
        });
        return { rows: [], rowCount: count };
      }

      if (sql.includes("UPDATE refresh_tokens SET is_revoked = TRUE WHERE id = $1")) {
        const t = this.refreshTokens.find((x) => x.id === params[0]);
        if (t) t.is_revoked = true;
        return { rows: [], rowCount: t ? 1 : 0 };
      }

      if (sql.includes("UPDATE refresh_tokens SET is_revoked = TRUE WHERE user_id = $1")) {
        let count = 0;
        this.refreshTokens.forEach((t) => {
          if (t.user_id === params[0] && !t.is_revoked) {
            t.is_revoked = true;
            count++;
          }
        });
        return { rows: [], rowCount: count };
      }

      // 3. Approvals Queries
      if (sql.includes("INSERT INTO approval_requests")) {
        const newApp: MockApproval = {
          id: `appr_${Date.now()}_${Math.random().toString(36).substring(2, 7)}`,
          maker_user_id: params[0],
          checker_user_id: null,
          action_type: params[1],
          payload: typeof params[2] === "string" ? JSON.parse(params[2]) : params[2],
          status: "pending",
          decision_reason: null,
          created_at: new Date(),
          reviewed_at: null,
        };
        this.approvals.push(newApp);
        return { rows: [newApp], rowCount: 1 };
      }

      if (sql.includes("SELECT") && sql.includes("FROM approval_requests WHERE id = $1")) {
        const a = this.approvals.find((x) => x.id === params[0]);
        return { rows: a ? [a] : [], rowCount: a ? 1 : 0 };
      }

      if (sql.includes("UPDATE approval_requests")) {
        const a = this.approvals.find((x) => x.id === params[3]);
        if (a) {
          a.checker_user_id = params[0];
          a.status = params[1];
          a.decision_reason = params[2];
          a.reviewed_at = new Date();
        }
        return { rows: a ? [a] : [], rowCount: a ? 1 : 0 };
      }

      // 4. Audit Logs
      if (sql.includes("INSERT INTO audit_logs")) {
        this.auditLogs.push(params);
        return { rows: [], rowCount: 1 };
      }

      // 5. Generic Ping
      if (sql.includes("SELECT 1")) {
        return { rows: [{ "?column?": 1 }], rowCount: 1 };
      }

      return { rows: [], rowCount: 0 };
    });
  }
}

export const testDb = new TestDatabase();
