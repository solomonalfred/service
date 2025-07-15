from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID

from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.repositories.users import UserRepository
from src.shemas.users import UserCreate
from src.core.hasher import PasswordManager
from src.core.config import get_settings


class AuthService:
    def __init__(self, session: AsyncSession) -> None:
        self._repo = UserRepository(session)
        self._pwd_mgr = PasswordManager()
        self._settings = get_settings()

    async def register(self, data: UserCreate) -> str:
        user = await self._repo.add(data)
        return self._create_access_token({"sub": str(user.id)})

    async def authenticate(self, name: str, password: str) -> Optional[str]:
        user = await self._repo.get_by_name(name)
        if user is None:
            return None
        orm = await self._repo.session.scalar(
            select(User).where(User.id == user.id)
        )
        if not self._pwd_mgr.verify_password(password, orm.password_hash):
            return None
        return self._create_access_token({"sub": str(user.id)})

    def _create_access_token(self, payload: dict,
                             expires_delta: timedelta | None = None) -> str:
        expire = datetime.utcnow() + (
            expires_delta or timedelta(minutes=self._settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        to_encode = {**payload, "exp": expire}
        return jwt.encode(
            to_encode,
            self._settings.SECRET_KEY.get_secret_value(),
            algorithm=self._settings.ALGORITHM,
        )

    def decode_token(self, token: str) -> Optional[dict]:
        try:
            return jwt.decode(
                token,
                self._settings.SECRET_KEY.get_secret_value(),
                algorithms=[self._settings.ALGORITHM],
            )
        except JWTError:
            return None
