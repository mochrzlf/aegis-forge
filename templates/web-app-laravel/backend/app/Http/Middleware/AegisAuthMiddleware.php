<?php

namespace App\Http\Middleware;

use App\Models\User;
use Closure;
use Illuminate\Http\Request;
use Symfony\Component\HttpFoundation\Response;

class AegisAuthMiddleware
{
    public function handle(Request $request, Closure $next): Response
    {
        $authHeader = $request->header('Authorization');
        if (!$authHeader || !str_starts_with($authHeader, 'Bearer ')) {
            return response()->json([
                'success' => false,
                'error' => ['code' => 'UNAUTHORIZED', 'message' => 'Missing or invalid authorization header']
            ], 401);
        }

        $token = substr($authHeader, 7);
        // Header mock format: Bearer <user_id> or Bearer token_<string>
        $userId = $token;
        if (str_starts_with($token, 'user_id:')) {
            $userId = substr($token, 8);
        }

        $user = User::find($userId);
        if (!$user) {
            return response()->json([
                'success' => false,
                'error' => ['code' => 'UNAUTHORIZED', 'message' => 'Invalid authentication token']
            ], 401);
        }

        // JML Kill-switch check
        if ($user->status !== 'active') {
            return response()->json([
                'success' => false,
                'error' => ['code' => 'ACCOUNT_DISABLED', 'message' => 'Account is suspended or terminated']
            ], 403);
        }

        $request->attributes->set('auth_user', $user);

        return $next($request);
    }
}
