<?php

namespace App\Services;

use App\Models\AuditLog;

class AuditService
{
    public static function log(
        ?string $userId,
        string $actorRole,
        string $action,
        string $resourceType,
        ?string $resourceId,
        string $ipAddress,
        string $status,
        array $details = []
    ): void {
        try {
            AuditLog::create([
                'user_id_hash' => $userId ? hash('sha256', $userId) : 'anonymous',
                'actor_role' => $actorRole,
                'action' => $action,
                'resource_type' => $resourceType,
                'resource_id' => $resourceId,
                'ip_hash' => hash('sha256', $ipAddress),
                'status' => $status,
                'details' => $details,
                'created_at' => now(),
            ]);
        } catch (\Throwable $e) {
            // Fail safe, do not crash application
        }
    }
}
