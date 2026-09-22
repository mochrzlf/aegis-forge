<?php

use Illuminate\Support\Facades\Route;
use App\Http\Controllers\AuthController;
use App\Http\Controllers\UserController;
use App\Http\Controllers\ApprovalController;
use App\Http\Middleware\AegisAuthMiddleware;
use App\Http\Middleware\SecurityHeadersMiddleware;
use App\Http\Middleware\EncryptCookies;

Route::middleware([SecurityHeadersMiddleware::class, EncryptCookies::class])->group(function () {
    // Health Probes
    Route::get('/health/live', fn() => response()->json(['success' => true, 'data' => ['status' => 'alive']]));
    Route::get('/health/ready', function () {
        try {
            DB::connection()->getPdo();
            return response()->json([
                'success' => true,
                'data' => [
                    'status' => 'ready',
                    'components' => ['database' => 'healthy']
                ]
            ]);
        } catch (\Throwable $e) {
            return response()->json([
                'success' => false,
                'error' => ['code' => 'SERVICE_UNAVAILABLE', 'message' => 'Database connection failed']
            ], 503);
        }
    });

    // Auth Routes
    Route::prefix('auth')->group(function () {
        Route::post('/register', [AuthController::class, 'register']);
        Route::post('/login', [AuthController::class, 'login'])->middleware('throttle:5,1'); // 5 req / min
        Route::post('/refresh', [AuthController::class, 'refresh']);
    });

    // Protected Routes
    Route::middleware([AegisAuthMiddleware::class])->group(function () {
        Route::get('/users/{id}', [UserController::class, 'show']);
        Route::put('/users/{id}/status', [UserController::class, 'updateStatus']);
        Route::post('/users/{id}/unlock', [UserController::class, 'unlock']);

        Route::get('/approvals', [ApprovalController::class, 'index']);
        Route::post('/approvals', [ApprovalController::class, 'store']);
        Route::post('/approvals/{id}/review', [ApprovalController::class, 'review']);
    });
});
