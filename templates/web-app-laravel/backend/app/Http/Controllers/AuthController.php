<?php

namespace App\Http\Controllers;

use App\Models\User;
use App\Models\RefreshToken;
use App\Services\AuditService;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Hash;
use Illuminate\Support\Str;

class AuthController extends Controller
{
    public function register(Request $request)
    {
        $validated = $request->validate([
            'email' => 'required|email|unique:users,email',
            'password' => 'required|string|min:8',
        ]);

        $user = User::create([
            'email' => $validated['email'],
            'password' => $validated['password'],
            'role' => 'user',
            'status' => 'active',
        ]);

        AuditService::log(
            $user->id,
            'user',
            'USER_REGISTERED',
            'user',
            $user->id,
            $request->ip() ?? '127.0.0.1',
            'SUCCESS'
        );

        return response()->json([
            'success' => true,
            'data' => [
                'id' => $user->id,
                'email' => $user->email,
                'role' => $user->role,
                'status' => $user->status,
            ],
            'meta' => ['timestamp' => now()->toIso8601String()]
        ], 201);
    }

    public function login(Request $request)
    {
        $validated = $request->validate([
            'email' => 'required|email',
            'password' => 'required|string',
        ]);

        $user = User::where('email', $validated['email'])->first();

        if (!$user) {
            return response()->json([
                'success' => false,
                'error' => ['code' => 'INVALID_CREDENTIALS', 'message' => 'Invalid email or password']
            ], 401);
        }

        // 1. Account Lockout check (ADR-004)
        if ($user->locked_until && $user->locked_until->isFuture()) {
            $remaining = $user->locked_until->diffInSeconds(now());
            return response()->json([
                'success' => false,
                'error' => [
                    'code' => 'ACCOUNT_LOCKED',
                    'message' => "Account is temporarily locked. Try again in {$remaining} seconds.",
                    'details' => ['retryAfter' => $remaining]
                ]
            ], 423);
        }

        // 2. JML Status check (ADR-005)
        if ($user->status !== 'active') {
            return response()->json([
                'success' => false,
                'error' => ['code' => 'ACCOUNT_DISABLED', 'message' => 'Account is suspended or terminated']
            ], 403);
        }

        // 3. Password Verification
        if (!Hash::check($validated['password'], $user->password)) {
            $attempts = $user->failed_login_attempts + 1;

            if ($attempts >= 5) {
                $user->update([
                    'failed_login_attempts' => $attempts,
                    'locked_until' => now()->addMinutes(15),
                ]);

                AuditService::log(
                    $user->id,
                    $user->role,
                    'ACCOUNT_LOCKED_FAILED_ATTEMPTS',
                    'user',
                    $user->id,
                    $request->ip() ?? '127.0.0.1',
                    'FAILURE',
                    ['attempts' => $attempts]
                );

                return response()->json([
                    'success' => false,
                    'error' => [
                        'code' => 'ACCOUNT_LOCKED',
                        'message' => 'Account locked for 15 minutes due to 5 consecutive failed login attempts.',
                        'details' => ['retryAfter' => 900]
                    ]
                ], 423);
            }

            $user->update(['failed_login_attempts' => $attempts]);
            AuditService::log(
                $user->id,
                $user->role,
                'LOGIN_FAILED',
                'user',
                $user->id,
                $request->ip() ?? '127.0.0.1',
                'FAILURE',
                ['attempts' => $attempts]
            );

            return response()->json([
                'success' => false,
                'error' => ['code' => 'INVALID_CREDENTIALS', 'message' => 'Invalid email or password']
            ], 401);
        }

        // 4. Reset lockout counter on success
        $user->update([
            'failed_login_attempts' => 0,
            'locked_until' => null,
        ]);

        // 5. Issue Tokens & RTR Session
        $familyId = (string) Str::uuid();
        $refreshTokenRaw = Str::random(64);
        $tokenHash = hash('sha256', $refreshTokenRaw);

        RefreshToken::create([
            'user_id' => $user->id,
            'token_hash' => $tokenHash,
            'family_id' => $familyId,
            'expires_at' => now()->addDays(7),
        ]);

        AuditService::log(
            $user->id,
            $user->role,
            'LOGIN_SUCCESS',
            'user',
            $user->id,
            $request->ip() ?? '127.0.0.1',
            'SUCCESS'
        );

        $cookie = cookie(
            'refreshToken',
            $refreshTokenRaw,
            7 * 24 * 60, // minutes
            '/api/auth',
            null,
            app()->environment('production'),
            true, // HttpOnly
            false,
            'Strict'
        );

        return response()->json([
            'success' => true,
            'data' => [
                'accessToken' => 'token_' . Str::random(32),
                'user' => [
                    'id' => $user->id,
                    'email' => $user->email,
                    'role' => $user->role,
                    'status' => $user->status,
                ]
            ],
            'meta' => ['timestamp' => now()->toIso8601String()]
        ])->withCookie($cookie);
    }

    public function refresh(Request $request)
    {
        $refreshTokenRaw = $request->cookie('refreshToken') ?? $request->header('X-Refresh-Token');
        if (!$refreshTokenRaw) {
            return response()->json([
                'success' => false,
                'error' => ['code' => 'UNAUTHORIZED', 'message' => 'Missing refresh token cookie']
            ], 401);
        }

        $tokenHash = hash('sha256', $refreshTokenRaw);
        $record = RefreshToken::where('token_hash', $tokenHash)->first();

        if (!$record) {
            return response()->json([
                'success' => false,
                'error' => ['code' => 'INVALID_TOKEN', 'message' => 'Token not found']
            ], 401);
        }

        // 🚨 Replay Detection
        if ($record->is_revoked) {
            RefreshToken::where('family_id', $record->family_id)->update(['is_revoked' => true]);

            AuditService::log(
                $record->user_id,
                'user',
                'TOKEN_REPLAY_DETECTED_ALL_REVOKED',
                'refresh_token',
                $record->family_id,
                $request->ip() ?? '127.0.0.1',
                'DENIED'
            );

            return response()->json([
                'success' => false,
                'error' => [
                    'code' => 'TOKEN_REPLAY_DETECTED',
                    'message' => 'Security violation: Compromised token reuse detected. All active sessions revoked.'
                ]
            ], 401)->withoutCookie('refreshToken', '/api/auth');
        }

        // Revoke old token
        $record->update(['is_revoked' => true]);

        // Check user active
        $user = User::find($record->user_id);
        if (!$user || $user->status !== 'active') {
            return response()->json([
                'success' => false,
                'error' => ['code' => 'ACCOUNT_DISABLED', 'message' => 'Account is no longer active']
            ], 403);
        }

        // Issue new rotated token
        $newRefreshTokenRaw = Str::random(64);
        RefreshToken::create([
            'user_id' => $user->id,
            'token_hash' => hash('sha256', $newRefreshTokenRaw),
            'family_id' => $record->family_id,
            'expires_at' => now()->addDays(7),
        ]);

        $cookie = cookie(
            'refreshToken',
            $newRefreshTokenRaw,
            7 * 24 * 60,
            '/api/auth',
            null,
            app()->environment('production'),
            true,
            false,
            'Strict'
        );

        return response()->json([
            'success' => true,
            'data' => [
                'accessToken' => 'token_' . Str::random(32),
            ],
            'meta' => ['timestamp' => now()->toIso8601String()]
        ])->withCookie($cookie);
    }
}
