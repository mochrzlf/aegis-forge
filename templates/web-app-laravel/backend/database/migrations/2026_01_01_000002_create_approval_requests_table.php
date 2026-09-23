<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;
use Illuminate\Support\Facades\DB;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('approval_requests', function (Blueprint $table) {
            $table->uuid('id')->primary();
            $table->foreignUuid('maker_user_id')->constrained('users');
            $table->foreignUuid('checker_user_id')->nullable()->constrained('users');
            $table->string('action_type', 100);
            $table->json('payload');
            $table->string('status', 50)->default('pending'); // pending, approved, rejected
            $table->text('decision_reason')->nullable();
            $table->timestamp('created_at')->useCurrent();
            $table->timestamp('reviewed_at')->nullable();
        });

        // Add Four-Eyes Principle check constraint if supported
        try {
            DB::statement('ALTER TABLE approval_requests ADD CONSTRAINT chk_maker_not_checker CHECK (maker_user_id <> checker_user_id)');
        } catch (\Throwable $e) {
            // SQLite in memory handles checks in table definitions or triggers
        }
    }

    public function down(): void
    {
        Schema::dropIfExists('approval_requests');
    }
};
