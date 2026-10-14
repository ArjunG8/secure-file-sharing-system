import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models import User
from app.modules.keys import service
from app.modules.keys.schemas import PublicKeyOut, RotateKeyRequest

router = APIRouter()


@router.get("/me", response_model=list[PublicKeyOut])
def my_keys(
    user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> list[PublicKeyOut]:
    return [PublicKeyOut.model_validate(k) for k in service.list_public_keys(db, user.id)]


@router.post("/rotate", response_model=PublicKeyOut)
def rotate(
    data: RotateKeyRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> PublicKeyOut:
    return PublicKeyOut.model_validate(service.rotate_keys(db, user.id, data.purpose))


@router.get("/users/{user_id}/public", response_model=list[PublicKeyOut])
def user_public_keys(
    user_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[PublicKeyOut]:
    return [PublicKeyOut.model_validate(k) for k in service.list_public_keys(db, user_id)]
