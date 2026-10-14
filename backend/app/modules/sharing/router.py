import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.core.errors import NotImplementedFeature
from app.models import User
from app.modules.sharing import MODULE_INFO, service
from app.modules.sharing.schemas import ShareCreate, ShareOut
from app.schemas.common import Page, PageParams, page_params

router = APIRouter()


@router.post("", response_model=ShareOut, status_code=status.HTTP_201_CREATED)
def create_share(
    data: ShareCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ShareOut:
    service.share_file(
        db, user.id, data.file_id, data.recipient_email, data.expires_at, data.max_downloads
    )
    raise NotImplementedFeature(MODULE_INFO, "Share response")


@router.get("/outgoing", response_model=Page[ShareOut])
def outgoing(
    page: PageParams = Depends(page_params),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Page[ShareOut]:
    raise NotImplementedFeature(MODULE_INFO, "Outgoing share listing")


@router.get("/incoming", response_model=Page[ShareOut])
def incoming(
    page: PageParams = Depends(page_params),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Page[ShareOut]:
    raise NotImplementedFeature(MODULE_INFO, "Incoming share listing")


@router.delete("/{grant_id}", status_code=status.HTTP_204_NO_CONTENT)
def revoke(
    grant_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    service.revoke_share(db, user.id, grant_id)
