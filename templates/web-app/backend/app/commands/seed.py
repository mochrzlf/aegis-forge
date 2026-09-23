"""Universal Admin & Checker Seeder for Aegis Forge (FastAPI).

Generates initial administrative accounts for testing banking IAM & Maker-Checker:
1. superadmin@aegisforge.dev (Role: superadmin)
2. checker@aegisforge.dev (Role: admin)
"""
import asyncio
import os
from datetime import datetime, timezone

from app.core import security
from app.core.deps import SessionLocal
from app.repositories import create_user, get_user_by_email

ADMIN_EMAIL = os.getenv("SEED_ADMIN_EMAIL", "superadmin@aegisforge.dev")
ADMIN_PASSWORD = os.getenv("SEED_ADMIN_PASSWORD", "SuperAdmin@Aegis123!")

CHECKER_EMAIL = os.getenv("SEED_CHECKER_EMAIL", "checker@aegisforge.dev")
CHECKER_PASSWORD = os.getenv("SEED_CHECKER_PASSWORD", "CheckerAdmin@Aegis123!")


async def seed_users() -> None:
    async with SessionLocal() as db:
        print("🌱 Seeding administrative users for Aegis Forge (FastAPI)...")

        # 1. Superadmin (Maker / Root Admin)
        admin = await get_user_by_email(db, ADMIN_EMAIL)
        if not admin:
            hashed_pwd = security.hash_password(ADMIN_PASSWORD)
            admin = await create_user(db, email=ADMIN_EMAIL, hashed_password=hashed_pwd, role="superadmin")
            admin.email_verified_at = datetime.now(timezone.utc)
            admin.status = "active"
            await db.commit()
            print(f"  ✅ Created Superadmin: {ADMIN_EMAIL} (Role: superadmin)")
        else:
            print(f"  ℹ️ Superadmin already exists: {ADMIN_EMAIL}")

        # 2. Checker (Reviewer / Approver)
        checker = await get_user_by_email(db, CHECKER_EMAIL)
        if not checker:
            hashed_pwd = security.hash_password(CHECKER_PASSWORD)
            checker = await create_user(db, email=CHECKER_EMAIL, hashed_password=hashed_pwd, role="admin")
            checker.email_verified_at = datetime.now(timezone.utc)
            checker.status = "active"
            await db.commit()
            print(f"  ✅ Created Checker: {CHECKER_EMAIL} (Role: admin)")
        else:
            print(f"  ℹ️ Checker already exists: {CHECKER_EMAIL}")

        print("\n✨ Seeding completed successfully.")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print("🔑 INITIAL CREDENTIALS (DEV ONLY):")
        print(f"   • Superadmin : {ADMIN_EMAIL} | {ADMIN_PASSWORD}")
        print(f"   • Checker    : {CHECKER_EMAIL} | {CHECKER_PASSWORD}")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")


if __name__ == "__main__":
    asyncio.run(seed_users())
