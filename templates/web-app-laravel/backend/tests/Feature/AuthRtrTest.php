<?php

namespace Tests\Feature;

use Tests\TestCase;
use App\Models\User;
use App\Models\RefreshToken;
use Illuminate\Foundation\Testing\RefreshDatabase;

class AuthRtrTest extends TestCase
{
    use RefreshDatabase;

    public function test_full_auth_rtr_and_replay_detection_flow(): void
    {
        // 1. Register
        $reg = $this->postJson('/api/auth/register', [
            'email' => 'bob@example.com',
            'password' => 'Password123!',
        ]);
        $reg->assertStatus(201)
            ->assertJsonPath('success', true)
            ->assertJsonPath('data.email', 'bob@example.com');

        // 2. Login
        $login = $this->postJson('/api/auth/login', [
            'email' => 'bob@example.com',
            'password' => 'Password123!',
        ]);

        $login->assertStatus(200)
            ->assertJsonPath('success', true)
            ->assertCookie('refreshToken');

        $initialCookie = $login->getCookie('refreshToken', false)->getValue();

        // 3. Normal Refresh (RTR)
        $refresh = $this->withHeader('X-Refresh-Token', $initialCookie)
            ->postJson('/api/auth/refresh');

        $refresh->assertStatus(200)
            ->assertJsonPath('success', true)
            ->assertCookie('refreshToken');

        $rotatedCookie = $refresh->getCookie('refreshToken', false)->getValue();
        $this->assertNotEquals($initialCookie, $rotatedCookie);

        // 4. Replay Attack Simulation (Attacker re-uses the revoked initialCookie)
        $replay = $this->withHeader('X-Refresh-Token', $initialCookie)
            ->postJson('/api/auth/refresh');

        $replay->assertStatus(401)
            ->assertJsonPath('error.code', 'TOKEN_REPLAY_DETECTED');

        // 5. Verify family was destroyed (Even new rotatedCookie is now revoked)
        $token = RefreshToken::where('token_hash', hash('sha256', $rotatedCookie))->first();
        $this->assertTrue($token->is_revoked);
    }
}
