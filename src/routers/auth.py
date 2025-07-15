from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from src.db.session import get_async_session
from src.shemas.users import UserCreate
from src.services.auth import AuthService

router = APIRouter(
    prefix="/auth"
)


def _auth_service(
    session: AsyncSession = Depends(get_async_session),
) -> AuthService:
    return AuthService(session)


@router.post("/register", status_code=201)
async def register(
    data: UserCreate,
    svc: AuthService = Depends(_auth_service),
):
    return {"access_token": await svc.register(data), "token_type": "bearer"}


@router.post("/login")
async def login(
    form: OAuth2PasswordRequestForm = Depends(),
    svc: AuthService = Depends(_auth_service),
):
    token = await svc.authenticate(form.username, form.password)
    if token is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Incorrect credentials")
    return {"access_token": token, "token_type": "bearer"}
