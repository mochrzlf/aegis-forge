<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('audit_logs', function (Blueprint $table) {
            $table->uuid('id')->primary();
            $table->string('user_id_hash', 64);
            $table->string('actor_role', 50);
            $table->string('action', 100);
            $table->string('resource_type', 100);
            $table->string('resource_id', 255)->nullable();
            $table->string('ip_hash', 64);
            $table->string('status', 50);
            $table->json('details')->nullable();
            $table->timestamp('created_at')->useCurrent();
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('audit_logs');
    }
};
