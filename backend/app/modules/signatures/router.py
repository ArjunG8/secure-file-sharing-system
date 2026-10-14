import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.core.errors import NotImplementedFeature
from app.models import User
from app.modules.signatures import MODULE_INFO
from app.modules.signatures.schemas import SignatureOut, SignatureVerifyResult

router = APIRouter()


@router.get("/files/{file_id}", response_model=SignatureOut)
def get_signature(
    file_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> SignatureOut:
    raise NotImplementedFeature(MODULE_INFO, "Signature retrieval")


@router.post("/files/{file_id}/verify", response_model=SignatureVerifyResult)
def verify_signature(
    file_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> SignatureVerifyResult:
    raise NotImplementedFeature(MODULE_INFO, "Signature verification")
