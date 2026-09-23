<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Concerns\HasUuids;
use Illuminate\Database\Eloquent\Model;

class RefreshToken extends Model
{
    use HasUuids;

    public $timestamps = false;

    protected $fillable = [
        'user_id',
        'token_hash',
        'family_id',
        'is_revoked',
        'expires_at',
    ];

    protected function casts(): array
    {
        return [
            'is_revoked' => 'boolean',
            'expires_at' => 'datetime',
        ];
    }
}
