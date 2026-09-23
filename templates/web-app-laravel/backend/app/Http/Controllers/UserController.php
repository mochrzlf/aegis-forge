<?php

namespace App\Http\Controllers;

use App\Models\User;
use App\Models\RefreshToken;
use App\Services\AuditService;
use Illuminate\Http\Request;

class UserController extends Controller
{
    public function show(Request $request, string $id)
    {
        $actor = $request->attributes->get('auth_user');

        // Anti-IDOR check
        if ($actor->id !== $id && $actor->role !== 'admin') {
            return response()->json([
                'success' => false,
                'error' => ['code' => 'FORBIDDEN', 'message' => 'You do not have permission to access this resource']
            ], 403);
        }

        $user = User::find($id);
        if (!$user) {
            return response()->json([
                'success' => false,
                'error' => ['code' => 'USER_NOT_FOUND', 'message' => 'User not found']
            ], 404);
        }

        return response()->json([
            'success' => true,
            'data' => [
                'id' => $user->id,
                'email' => $user->email,
                'role' => $user->role,
                'status' => $user->status,
                'failed_login_attempts' => $user->failed_login_attempts,
                'locked_until' => $user->locked_until,
                'created_at' => $user->created_at,
            ],
            'meta' => ['timestamp' => now()->toIso8601String()]
        ]);
    }

    public function updateStatus(Request $request, string $id)
    {
        $actor = $request->attributes->get('auth_user');

        if ($actor->role !== 'admin') {
            return response()->json([
                'success' => false,
                'error' => ['code' => 'FORBIDDEN', 'message' => 'Administrator privileges required']
            ], 403);
        }

        // 1. Admin self-suspension guard (ADR-005)
        if ($actor->id === $id) {
            return response()->json([
                'success' => false,
                'error' => ['code' => 'INVALID_ACTION', 'message' => 'Administrators cannot suspend or terminate their own account.']
            ], 400);
        }

        $validated = $request->validate([
            'status' => 'required|in:active,suspended,terminated',
        ]);

        $user = User::find($id);
        if (!$user) {
            return response()->json([
                'success' => false,
                'error' => ['code' => 'USER_NOT_FOUND', 'message' => 'User not found']
            ], 404);
        }

        $user->update(['status' => $validated['status']]);

        // 2. JML Session Kill-Switch
        $revokedCount = 0;
        if (in_array($validated['status'], ['suspended', 'terminated'])) {
            $revokedCount = RefreshToken::where('user_id', $id)
                ->where('is_revoked', false)
                ->update(['is_revoked' => true]);
        }

        AuditService::log(
            $actor->id,
            $actor->role,
            'USER_STATUS_UPDATED',
            'user',
            $id,
            $request->ip() ?? '127.0.0.1',
            'SUCCESS',
            ['newStatus' => $validated['status'], 'revokedSessions' => $revokedCount]
        );

        return response()->json([
            'success' => true,
            'data' => [
                'userId' => $id,
                'status' => $validated['status'],
                'revokedSessions' => $revokedCount,
            ],
            'meta' => ['timestamp' => now()->toIso8601String()]
        ]);
    }

    public function unlock(Request $request, string $id)
    {
        $actor = $request->attributes->get('auth_user');

        if ($actor->role !== 'admin') {
            return response()->json([
                'success' => false,
                'error' => ['code' => 'FORBIDDEN', 'message' => 'Administrator privileges required']
            ], 403);
        }

        $user = User::find($id);
        if (!$user) {
            return response()->json([
                'success' => false,
                'error' => ['code' => 'USER_NOT_FOUND', 'message' => 'User not found']
            ], 404);
        }

        $user->update([
            'failed_login_attempts' => 0,
            'locked_until' => null,
        ]);

        AuditService::log(
            $actor->id,
            $actor->role,
            'ACCOUNT_MANUALLY_UNLOCKED',
            'user',
            $id,
            $request->ip() ?? '127.0.0.1',
            'SUCCESS'
        );

        return response()->json([
            'success' => true,
            'data' => ['userId' => $id, 'locked' => false],
            'meta' => ['timestamp' => now()->toIso8601String()]
        ]);
    }
}
