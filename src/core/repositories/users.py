from __future__ import annotations
from typing import Optional
from uuid import UUID

from sqlalchemy import select, update, delete
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import User
from src.shemas.users import UserCreate, UserPatch, UserRead
from src.core.hasher import PasswordManager


class UserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self._pwd_mgr = PasswordManager()

    async def add(self, dto: UserCreate) -> UserRead:
        user = User(
            name=dto.name,
            password_hash=self._pwd_mgr.hash_password(dto.password),
            **dto.model_dump(exclude={"password"})
        )
        self.session.add(user)
        try:
            await self.session.flush()
        except IntegrityError as exc:
            await self.session.rollback()
            raise ValueError("user with same name/tin/ogrn already exists") from exc
        await self.session.commit()
        return UserRead.model_validate(user)

    async def get_by_name(self, name: str) -> Optional[UserRead]:
        res = await self.session.scalars(
            select(User).where(User.name == name)
        )
        user = res.one_or_none()
        return None if user is None else UserRead.model_validate(user)

    async def patch(self, user_id: UUID, patch: UserPatch) -> UserRead:
        if not patch.model_fields_set:
            return await self.get(user_id)
        stmt = (
            update(User)
            .where(User.id == user_id)
            .values(**patch.model_dump(exclude_unset=True))
            .returning(User)
        )
        res = await self.session.execute(stmt)
        user = res.scalar_one()
        await self.session.commit()
        return UserRead.model_validate(user)

    async def delete(self, user_id: UUID) -> None:
        await self.session.execute(delete(User).where(User.id == user_id))
        await self.session.commit()

    async def get(self, user_id: UUID) -> UserRead:
        res = await self.session.scalars(select(User).where(User.id == user_id))
        user = res.one_or_none()
        if user is None:
            raise KeyError("user not found")
        return UserRead.model_validate(user)
