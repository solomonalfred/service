from __future__ import annotations
from typing import List, Optional
from uuid import UUID

from sqlalchemy import select, update, delete, exists
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import User
from src.shemas.users import (
    UserInfo,
    UserRead,
    UserPatch
)

class UsersRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_user(self, data: UserInfo) -> UUID:
        user = User(**data.model_dump())
        self.session.add(user)
        await self.session.flush()
        await self.session.commit()
        return user.id

    async def get_user(self, user_id: UUID) -> UserRead:
        stmt = select(User).where(User.id == user_id)
        result = await self.session.scalars(stmt)
        user = result.one_or_none()
        if user is None:
            raise KeyError("User not found")
        return UserRead.model_validate(user)
