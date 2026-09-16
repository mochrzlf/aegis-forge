import { createBrowserClient } from "@supabase/ssr";

// Browser client — uses the public anon key. All access is constrained by RLS.
export function createClient() {
  return createBrowserClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
  );
}
