<?php

namespace Tests\Feature;

use Tests\TestCase;
use App\Models\User;
use App\Models\RefreshToken;
use Illuminate\Foundation\Testing\RefreshDatabase;

class KillSwitchTest extends TestCase
{
    use RefreshDatabase;

    protected $admin;
    protected $employee;

    protected function setUp(): void
    {
        parent::setUp();

        $this->admin = User::create([
            'email' => 'admin@bank.com',
            'password' => 'Password123!',
            'role' => 'admin',
            'status' => 'active',
        ]);

        $this->employee = User::create([
            'email' => 'employee@bank.com',
            'password' => 'Password123!',
            'role' => 'user',
            'status' => 'active',
        ]);

        // Create active refresh token for employee
        RefreshToken::create([
            'user_id' => $this->employee->id,
            'token_hash' => hash('sha256', 'sample_token'),
            'family_id' => (string) \Illuminate\Support\Str::uuid(),
            'is_revoked' => false,
            'expires_at' => now()->addDays(7),
        ]);
    }

    public function test_admin_suspending_user_revokes_all_active_sessions(): void
    {
        $response = $this->withHeader('Authorization', 'Bearer ' . $this->admin->id)
            ->putJson("/api/users/{$this->employee->id}/status", [
                'status' => 'suspended',
            ]);

        $response->assertStatus(200)
            ->assertJsonPath('success', true)
            ->assertJsonPath('data.status', 'suspended')
            ->assertJsonPath('data.revokedSessions', 1);

        // Verify token in database is revoked
        $token = RefreshToken::where('user_id', $this->employee->id)->first();
        $this->assertTrue($token->is_revoked);

        // Employee access is immediately blocked
        $accessRes = $this->withHeader('Authorization', 'Bearer ' . $this->employee->id)
            ->getJson("/api/users/{$this->employee->id}");

        $accessRes->assertStatus(403)
            ->assertJsonPath('error.code', 'ACCOUNT_DISABLED');
    }

    public function test_admin_cannot_suspend_themselves(): void
    {
        $response = $this->withHeader('Authorization', 'Bearer ' . $this->admin->id)
            ->putJson("/api/users/{$this->admin->id}/status", [
                'status' => 'suspended',
            ]);

        $response->assertStatus(400)
            ->assertJsonPath('error.code', 'INVALID_ACTION');
    }
}
