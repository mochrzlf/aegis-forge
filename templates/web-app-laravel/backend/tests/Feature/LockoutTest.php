<?php

namespace Tests\Feature;

use Tests\TestCase;
use App\Models\User;
use Illuminate\Foundation\Testing\RefreshDatabase;

class LockoutTest extends TestCase
{
    use RefreshDatabase;

    protected $user;
    protected $admin;

    protected function setUp(): void
    {
        parent::setUp();

        $this->user = User::create([
            'email' => 'victim@example.com',
            'password' => 'Password123!',
            'role' => 'user',
            'status' => 'active',
        ]);

        $this->admin = User::create([
            'email' => 'admin@example.com',
            'password' => 'Password123!',
            'role' => 'admin',
            'status' => 'active',
        ]);
    }

    public function test_locks_account_after_5_failed_attempts(): void
    {
        $this->withoutMiddleware(\Illuminate\Routing\Middleware\ThrottleRequests::class);

        for ($i = 0; $i < 4; $i++) {
            $res = $this->postJson('/api/auth/login', [
                'email' => $this->user->email,
                'password' => 'WrongPassword',
            ]);
            $res->assertStatus(401);
        }

        // 5th failed attempt -> Locks account (423)
        $fifth = $this->postJson('/api/auth/login', [
            'email' => $this->user->email,
            'password' => 'WrongPassword',
        ]);

        $fifth->assertStatus(423)
            ->assertJsonPath('error.code', 'ACCOUNT_LOCKED');

        // Subsequent attempt with CORRECT password is still locked
        $sixth = $this->postJson('/api/auth/login', [
            'email' => $this->user->email,
            'password' => 'Password123!',
        ]);

        $sixth->assertStatus(423);
    }

    public function test_admin_can_manually_unlock_locked_user(): void
    {
        $this->user->update([
            'failed_login_attempts' => 5,
            'locked_until' => now()->addMinutes(15),
        ]);

        $res = $this->withHeader('Authorization', 'Bearer ' . $this->admin->id)
            ->postJson("/api/users/{$this->user->id}/unlock");

        $res->assertStatus(200)
            ->assertJsonPath('success', true)
            ->assertJsonPath('data.locked', false);

        // Login works again
        $loginRes = $this->postJson('/api/auth/login', [
            'email' => $this->user->email,
            'password' => 'Password123!',
        ]);

        $loginRes->assertStatus(200);
    }
}
