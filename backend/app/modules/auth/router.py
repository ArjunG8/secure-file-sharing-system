from fastapi import APIRouter, Depends, Request, Response, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models import User
from app.modules.auth import service
from app.modules.auth.schemas import (
    ChangePasswordRequest,
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    UserOut,
)

router = APIRouter()


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(data: RegisterRequest, db: Session = Depends(get_db)) -> UserOut:
    user = service.register_user(db, data)
    return UserOut.model_validate(user)


@router.post("/login", response_model=TokenResponse)
def login(
    data: LoginRequest, request: Request, response: Response, db: Session = Depends(get_db)
) -> TokenResponse:
    pair = service.authenticate(
        db,
        data.email,
        data.password,
        request.client.host if request.client else None,
        request.headers.get("user-agent"),
    )
    # TODO(M1): response.set_cookie("refresh_token", pair.refresh_token, httponly=True,
    #           secure=True, samesite="strict", path="/api/v1/auth")
    return pair.access


@router.post("/refresh", response_model=TokenResponse)
def refresh(request: Request, response: Response, db: Session = Depends(get_db)) -> TokenResponse:
    pair = service.refresh_session(db, request.cookies.get("refresh_token", ""))
    return pair.access


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(
    request: Request,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    service.revoke_session(db, user.id, request.cookies.get("refresh_token"))


@router.get("/me", response_model=UserOut)
def me(user: User = Depends(get_current_user)) -> UserOut:
    return UserOut.model_validate(user)


@router.post("/change-password", status_code=status.HTTP_204_NO_CONTENT)
def change_password(
    data: ChangePasswordRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    service.change_password(db, user, data.current_password, data.new_password)
