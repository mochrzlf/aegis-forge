# Database Migration Standard

> **Purpose:** Safe, versioned, reversible schema evolution for PostgreSQL. Rule #1: **the production schema is only ever changed through migration tooling — never by hand.** `docs/schema.sql` is the *reference* of the desired end-state; migrations are the *path* to get there.

---

## 1. Tooling (choose per stack — one, not all)

| Stack | Recommended Tool | Migration Format |
|---|---|---|
| Python (FastAPI/SQLAlchemy) | **Alembic** | Python revision scripts |
| Node/TS (NestJS/TypeORM/Prisma) | **Prisma Migrate** or **TypeORM migrations** | SQL / generated |
| Go services | **golang-migrate** or **goose** | Plain `.sql` up/down |
| Polyglot / SQL-first | **Flyway** | Versioned `.sql` |

> Record the chosen tool in the project's `SETUP.md`. All are recorded as candidates in `docs/research/EXTERNAL-TOOLS.md` — pick one and standardize.

---

## 2. Core Principles

1. **Versioned & immutable.** Every change is a new, sequentially-numbered migration file. Never edit an already-applied migration.
2. **Reversible.** Every `up` has a tested `down` (or an explicit, documented reason it can't be reversed, e.g., destructive drop).
3. **One logical change per migration.** Small, reviewable units.
4. **Code-reviewed like code.** Migrations touching `docs/schema.sql` require DBA-lead review (CODEOWNERS).
5. **CI-validated.** Migrations are applied to a throwaway Postgres in CI before merge.

---

## 3. The Expand–Migrate–Contract Pattern (Zero-Downtime)

For changing existing columns/tables on a live system, **never do breaking renames/drops in one step**. Use three phases:

```
1. EXPAND   → Add the NEW structure alongside the old (new column/table).
              App writes to BOTH (dual-write). Old reads still work.
2. MIGRATE  → Backfill existing data from old → new (batched).
              Verify counts/checksums match.
3. CONTRACT → Switch reads to the new structure; after a safe window,
              drop the old structure in a separate migration.
```

This keeps `old` and `new` app versions both working during deployment (rolling deploys).

### ❌ Never in a single deploy
- `RENAME COLUMN` (breaks old app version) → expand/migrate/contract instead.
- `DROP COLUMN/TABLE` that the running app still uses → drop only after all app instances no longer reference it.
- Adding `NOT NULL` to a column with existing rows → add nullable, backfill, then add the constraint.

---

## 4. Data Migrations (large tables)

- **Batch** backfills (e.g., 1–10k rows/batch) with `WHERE id > :last` — avoid long table locks.
- Run during low-traffic windows; throttle/sleep between batches.
- Make them **idempotent** (safe to re-run) and **resumable**.
- For very large tables, consider `pg_repack`-style or shadow-table approaches rather than in-place rewrites.
- Verify: row counts, spot-checks, and checksums before switching reads.

---

## 5. Adding Indexes Concurrently

Creating an index naively locks writes. On production tables:
```sql
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_orders_user_id ON orders(user_id);
```
- `CONCURRENTLY` avoids the write lock but **cannot run inside a transaction** — configure your tool accordingly (Alembic: `transaction_per_migration=False` for that revision; golang-migrate/Flyway: dedicated non-transactional migration).

---

## 6. Migration File Template

```sql
-- +migrate Up
-- Description: add email_verified_at to users (expand phase)
ALTER TABLE users ADD COLUMN IF NOT EXISTS email_verified_at timestamptz NULL;

-- +migrate Down
ALTER TABLE users DROP COLUMN IF EXISTS email_verified_at;
```
Include: a clear description, the phase (expand/migrate/contract), and any special notes (non-transactional, batched, lock risk).

---

## 7. Pre-Deploy Checklist

- [ ] Migration is versioned, immutable, and has a tested `down`.
- [ ] Follows expand–migrate–contract (no single-step breaking change).
- [ ] `NOT NULL` only added after backfill; indexes use `CONCURRENTLY`.
- [ ] Applied successfully to a fresh Postgres in CI.
- [ ] DBA-lead reviewed; lock/timeout risk assessed for large tables.
- [ ] Rollback plan documented (how to `down` safely if deploy fails).
- [ ] `docs/schema.sql` updated to reflect the new end-state.

> A failed production migration is an incident — follow `docs/security/incident-response.md` and have the `down` migration + DB backup ready before you start.
