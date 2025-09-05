from typing import AsyncGenerator

from fastapi import Depends

from worker_safety_service.models import AsyncSession, with_session


async def with_autocommit_session(
    session: AsyncSession = Depends(with_session),
) -> AsyncGenerator[AsyncSession, None]:
    yield session
    await session.commit()
