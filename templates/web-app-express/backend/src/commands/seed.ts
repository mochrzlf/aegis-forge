/**
 * Universal Admin & Checker Seeder for Aegis Forge (Express.js TypeScript).
 *
 * Generates initial administrative accounts for testing banking IAM & Maker-Checker:
 * 1. superadmin@aegisforge.dev (Role: superadmin)
 * 2. checker@aegisforge.dev (Role: admin)
 */
import { query, pool } from "../core/db.js";
import { hashPassword } from "../core/crypto.js";

const ADMIN_EMAIL = process.env.SEED_ADMIN_EMAIL || "superadmin@aegisforge.dev";
const ADMIN_PASSWORD = process.env.SEED_ADMIN_PASSWORD || "SuperAdmin@Aegis123!";

const CHECKER_EMAIL = process.env.SEED_CHECKER_EMAIL || "checker@aegisforge.dev";
const CHECKER_PASSWORD = process.env.SEED_CHECKER_PASSWORD || "CheckerAdmin@Aegis123!";

async function seed() {
  console.log("🌱 Seeding administrative users for Aegis Forge (Express.js)...");

  try {
    // 1. Superadmin (Maker / Root Admin)
    const adminCheck = await query("SELECT id, email FROM users WHERE email = $1", [ADMIN_EMAIL]);
    if (adminCheck.rows.length === 0) {
      const pwdHash = await hashPassword(ADMIN_PASSWORD);
      await query(
        `INSERT INTO users (email, password_hash, role, status, created_at, updated_at)
         VALUES ($1, $2, 'superadmin', 'active', NOW(), NOW())`,
        [ADMIN_EMAIL, pwdHash]
      );
      console.log(`  ✅ Created Superadmin: ${ADMIN_EMAIL} (Role: superadmin)`);
    } else {
      console.log(`  ℹ️ Superadmin already exists: ${ADMIN_EMAIL}`);
    }

    // 2. Checker (Reviewer / Approver)
    const checkerCheck = await query("SELECT id, email FROM users WHERE email = $1", [CHECKER_EMAIL]);
    if (checkerCheck.rows.length === 0) {
      const pwdHash = await hashPassword(CHECKER_PASSWORD);
      await query(
        `INSERT INTO users (email, password_hash, role, status, created_at, updated_at)
         VALUES ($1, $2, 'admin', 'active', NOW(), NOW())`,
        [CHECKER_EMAIL, pwdHash]
      );
      console.log(`  ✅ Created Checker: ${CHECKER_EMAIL} (Role: admin)`);
    } else {
      console.log(`  ℹ️ Checker already exists: ${CHECKER_EMAIL}`);
    }

    console.log("\n✨ Seeding completed successfully.");
    console.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
    console.log("🔑 INITIAL CREDENTIALS (DEV ONLY):");
    console.log(`   • Superadmin : ${ADMIN_EMAIL} | ${ADMIN_PASSWORD}`);
    console.log(`   • Checker    : ${CHECKER_EMAIL} | ${CHECKER_PASSWORD}`);
    console.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
  } catch (error) {
    console.error("❌ Seeding failed:", error);
    process.exit(1);
  } finally {
    await pool.end();
  }
}

seed();
