<?php

namespace Database\Seeders;

use App\Models\User;
use Illuminate\Database\Seeder;

class DatabaseSeeder extends Seeder
{
    /**
     * Seed the application's database with initial administrative accounts.
     */
    public function run(): void
    {
        $adminEmail = env('SEED_ADMIN_EMAIL', 'superadmin@aegisforge.dev');
        $adminPassword = env('SEED_ADMIN_PASSWORD', 'SuperAdmin@Aegis123!');

        $checkerEmail = env('SEED_CHECKER_EMAIL', 'checker@aegisforge.dev');
        $checkerPassword = env('SEED_CHECKER_PASSWORD', 'CheckerAdmin@Aegis123!');

        // 1. Superadmin (Maker / Root Admin)
        $admin = User::firstOrCreate(
            ['email' => $adminEmail],
            [
                'password' => $adminPassword,
                'role' => 'superadmin',
                'status' => 'active',
            ]
        );

        // 2. Checker (Reviewer / Approver)
        $checker = User::firstOrCreate(
            ['email' => $checkerEmail],
            [
                'password' => $checkerPassword,
                'role' => 'admin',
                'status' => 'active',
            ]
        );

        if ($this->command) {
            $this->command->info("🌱 Seeding administrative users for Aegis Forge (Laravel)...");
            $this->command->info("  ✅ Superadmin: {$admin->email} (Role: superadmin)");
            $this->command->info("  ✅ Checker   : {$checker->email} (Role: admin)");
            $this->command->info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
            $this->command->info("🔑 INITIAL CREDENTIALS (DEV ONLY):");
            $this->command->info("   • Superadmin : {$adminEmail} | {$adminPassword}");
            $this->command->info("   • Checker    : {$checkerEmail} | {$checkerPassword}");
            $this->command->info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
        }
    }
}
