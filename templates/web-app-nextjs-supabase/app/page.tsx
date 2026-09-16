import Link from "next/link";

export default function Home() {
  return (
    <main className="mx-auto flex min-h-screen max-w-2xl flex-col items-start justify-center gap-6 p-8">
      <h1 className="text-3xl font-bold">Aegis Web App</h1>
      <p className="text-neutral-600 dark:text-neutral-300">
        Next.js + Supabase starter (opt-in alternative). Read the README before
        choosing this over the default FastAPI skeleton.
      </p>
      <div className="flex gap-4">
        <Link href="/login" className="rounded bg-black px-4 py-2 text-white dark:bg-white dark:text-black">
          Log in
        </Link>
        <Link href="/register" className="rounded border px-4 py-2">
          Register
        </Link>
      </div>
    </main>
  );
}
