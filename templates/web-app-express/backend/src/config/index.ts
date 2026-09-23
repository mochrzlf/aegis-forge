import dotenv from "dotenv";
import { z } from "zod";

dotenv.config();

const envSchema = z.object({
  PORT: z.coerce.number().default(8000),
  NODE_ENV: z.enum(["development", "test", "production"]).default("development"),
  DATABASE_URL: z.string().default("postgres://postgres:postgres@localhost:5432/aegis_db"),
  REDIS_URL: z.string().default("redis://localhost:6379"),
  JWT_ACCESS_SECRET: z.string().min(32).default("default_super_secret_jwt_access_key_min_32_bytes_long"),
  JWT_REFRESH_SECRET: z.string().min(32).default("default_super_secret_jwt_refresh_key_min_32_bytes_long"),
  CORS_ORIGIN: z.string().default("*"),
});

const _env = envSchema.safeParse(process.env);

if (!_env.success) {
  console.error("❌ Invalid environment variables:", _env.error.format());
  process.exit(1);
}

export const env = _env.data;
