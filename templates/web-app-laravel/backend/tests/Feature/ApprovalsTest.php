<?php

namespace Tests\Feature;

use Tests\TestCase;
use App\Models\User;
use App\Models\ApprovalRequest;
use Illuminate\Foundation\Testing\RefreshDatabase;

class ApprovalsTest extends TestCase
{
    use RefreshDatabase;

    protected $maker;
    protected $checker;

    protected function setUp(): void
    {
        parent::setUp();

        $this->maker = User::create([
            'email' => 'maker@example.com',
            'password' => 'Password123!',
            'role' => 'user',
            'status' => 'active',
        ]);

        $this->checker = User::create([
            'email' => 'checker@example.com',
            'password' => 'Password123!',
            'role' => 'admin',
            'status' => 'active',
        ]);
    }

    public function test_maker_can_create_pending_approval(): void
    {
        $response = $this->withHeader('Authorization', 'Bearer ' . $this->maker->id)
            ->postJson('/api/approvals', [
                'action_type' => 'role_promotion',
                'payload' => ['target_user' => 'u1', 'new_role' => 'admin'],
            ]);

        $response->assertStatus(201)
            ->assertJsonPath('success', true)
            ->assertJsonPath('data.status', 'pending')
            ->assertJsonPath('data.maker_user_id', $this->maker->id);
    }

    public function test_maker_cannot_approve_own_request_four_eyes_principle(): void
    {
        // 1. Maker creates request
        $approval = ApprovalRequest::create([
            'maker_user_id' => $this->maker->id,
            'action_type' => 'fund_disbursement',
            'payload' => ['amount' => 5000000],
            'status' => 'pending',
            'created_at' => now(),
        ]);

        // 2. Maker attempts to approve own request
        $response = $this->withHeader('Authorization', 'Bearer ' . $this->maker->id)
            ->postJson("/api/approvals/{$approval->id}/review", [
                'decision' => 'approved',
                'reason' => 'Self approving my own request',
            ]);

        $response->assertStatus(403)
            ->assertJsonPath('success', false)
            ->assertJsonPath('error.code', 'FORBIDDEN');
    }

    public function test_checker_can_approve_request(): void
    {
        $approval = ApprovalRequest::create([
            'maker_user_id' => $this->maker->id,
            'action_type' => 'fund_disbursement',
            'payload' => ['amount' => 5000000],
            'status' => 'pending',
            'created_at' => now(),
        ]);

        $response = $this->withHeader('Authorization', 'Bearer ' . $this->checker->id)
            ->postJson("/api/approvals/{$approval->id}/review", [
                'decision' => 'approved',
                'reason' => 'Compliant with policy',
            ]);

        $response->assertStatus(200)
            ->assertJsonPath('success', true)
            ->assertJsonPath('data.status', 'approved')
            ->assertJsonPath('data.checker_user_id', $this->checker->id);
    }
}
