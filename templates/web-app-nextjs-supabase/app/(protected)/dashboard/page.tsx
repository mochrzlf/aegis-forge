import { redirect } from "next/navigation";
import { createClient } from "@/lib/supabase/server";

export default async function DashboardPage() {
  const supabase = await createClient();
  const {
    data: { user },
  } = await supabase.auth.getUser();
  if (!user) redirect("/login");

  // RLS constrains this to the caller's own row (see migration 0001_init.sql).
  const { data: profile } = await supabase
    .from("profiles")
    .select("id, email, role, created_at")
    .eq("id", user.id)
    .single();

  async function signOut() {
    "use server";
    const supabase = await createClient();
    await supabase.auth.signOut();
    redirect("/login");
  }

  return (
    <main className="mx-auto flex min-h-screen max-w-2xl flex-col justify-center gap-6 p-8">
      <h1 className="text-3xl font-bold">Dashboard</h1>
      <p className="text-neutral-600 dark:text-neutral-300">
        Signed in as <strong>{user.email}</strong>
      </p>
      <section className="rounded border p-4">
        <h2 className="mb-2 font-semibold">Your profile (RLS-protected)</h2>
        <pre className="overflow-auto text-sm">
          {JSON.stringify(profile ?? { note: "no profile row yet" }, null, 2)}
        </pre>
      </section>
      <form action={signOut}>
        <button className="rounded border px-4 py-2">Sign out</button>
      </form>
    </main>
  );
}
