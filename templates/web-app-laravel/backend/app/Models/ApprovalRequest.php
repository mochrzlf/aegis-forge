<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Concerns\HasUuids;
use Illuminate\Database\Eloquent\Model;

class ApprovalRequest extends Model
{
    use HasUuids;

    public $timestamps = false;

    protected $fillable = [
        'maker_user_id',
        'checker_user_id',
        'action_type',
        'payload',
        'status',
        'decision_reason',
        'created_at',
        'reviewed_at',
    ];

    protected function casts(): array
    {
        return [
            'payload' => 'array',
            'created_at' => 'datetime',
            'reviewed_at' => 'datetime',
        ];
    }
}
