from datetime import datetime, timedelta, timezone
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import RefreshToken
from app.repositories import count_active_refresh_tokens, create_user, revoke_all_refresh_tokens


@pytest.mark.asyncio
async def test_killswitch_revokes_all_active_sessions(db_session: AsyncSession):
    victim = await create_user(db_session, "victim@example.com", "hashed")
    other = await create_user(db_session, "other@example.com", "hashed")
    expiry = datetime.now(timezone.utc) + timedelta(days=30)

    # 2 live sessions for victim
    db_session.add(RefreshToken(user_id=victim.id, token_hash="live-1", expires_at=expiry))
    db_session.add(RefreshToken(user_id=victim.id, token_hash="live-2", expires_at=expiry))
    # 1 already revoked for victim
    db_session.add(
        RefreshToken(
            user_id=victim.id,
            token_hash="stale",
            expires_at=expiry,
            revoked_at=datetime.now(timezone.utc) - timedelta(hours=1),
        )
    )
    # 1 live session for other user
    db_session.add(RefreshToken(user_id=other.id, token_hash="other-live", expires_at=expiry))
    await db_session.commit()

    assert await count_active_refresh_tokens(db_session, victim.id) == 2

    # Kill-switch
    revoked = await revoke_all_refresh_tokens(db_session, victim.id)
    assert revoked == 2
    assert await count_active_refresh_tokens(db_session, victim.id) == 0

    # Other user sessions untouched
    assert await count_active_refresh_tokens(db_session, other.id) == 1

    # Idempotent re-invocation
    assert await revoke_all_refresh_tokens(db_session, victim.id) == 0
