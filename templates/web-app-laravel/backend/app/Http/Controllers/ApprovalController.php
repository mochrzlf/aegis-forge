<?php

namespace App\Http\Controllers;

use App\Models\ApprovalRequest;
use App\Services\AuditService;
use Illuminate\Http\Request;

class ApprovalController extends Controller
{
    public function store(Request $request)
    {
        $actor = $request->attributes->get('auth_user');

        $validated = $request->validate([
            'action_type' => 'required|string|max:100',
            'payload' => 'required|array',
        ]);

        $approval = ApprovalRequest::create([
            'maker_user_id' => $actor->id,
            'action_type' => $validated['action_type'],
            'payload' => $validated['payload'],
            'status' => 'pending',
            'created_at' => now(),
        ]);

        AuditService::log(
            $actor->id,
            $actor->role,
            'APPROVAL_REQUEST_CREATED',
            'approval_request',
            $approval->id,
            $request->ip() ?? '127.0.0.1',
            'SUCCESS',
            ['actionType' => $validated['action_type']]
        );

        return response()->json([
            'success' => true,
            'data' => $approval,
            'meta' => ['timestamp' => now()->toIso8601String()]
        ], 201);
    }

    public function index(Request $request)
    {
        $query = ApprovalRequest::query();
        if ($request->has('status')) {
            $query->where('status', $request->query('status'));
        }

        $approvals = $query->orderBy('created_at', 'desc')->get();

        return response()->json([
            'success' => true,
            'data' => $approvals,
            'meta' => ['timestamp' => now()->toIso8601String()]
        ]);
    }

    public function review(Request $request, string $id)
    {
        $actor = $request->attributes->get('auth_user');

        $validated = $request->validate([
            'decision' => 'required|in:approved,rejected',
            'reason' => 'nullable|string',
        ]);

        $approval = ApprovalRequest::find($id);
        if (!$approval) {
            return response()->json([
                'success' => false,
                'error' => ['code' => 'APPROVAL_NOT_FOUND', 'message' => 'Approval request not found']
            ], 404);
        }

        if ($approval->status !== 'pending') {
            return response()->json([
                'success' => false,
                'error' => ['code' => 'ALREADY_PROCESSED', 'message' => "Approval request is already {$approval->status}"]
            ], 400);
        }

        // 🔒 Dual Control / Maker-Checker Rule (ADR-006)
        if ($approval->maker_user_id === $actor->id) {
            AuditService::log(
                $actor->id,
                $actor->role,
                'MAKER_CHECKER_SELF_APPROVAL_ATTEMPT',
                'approval_request',
                $id,
                $request->ip() ?? '127.0.0.1',
                'DENIED'
            );

            return response()->json([
                'success' => false,
                'error' => [
                    'code' => 'FORBIDDEN',
                    'message' => 'Dual Control violation: The maker is strictly forbidden from approving their own request.'
                ]
            ], 403);
        }

        $approval->update([
            'checker_user_id' => $actor->id,
            'status' => $validated['decision'],
            'decision_reason' => $validated['reason'] ?? null,
            'reviewed_at' => now(),
        ]);

        AuditService::log(
            $actor->id,
            $actor->role,
            'APPROVAL_REQUEST_' . strtoupper($validated['decision']),
            'approval_request',
            $id,
            $request->ip() ?? '127.0.0.1',
            'SUCCESS',
            ['decision' => $validated['decision'], 'reason' => $validated['reason'] ?? null]
        );

        return response()->json([
            'success' => true,
            'data' => $approval,
            'meta' => ['timestamp' => now()->toIso8601String()]
        ]);
    }
}
