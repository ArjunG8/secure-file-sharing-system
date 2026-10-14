import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_admin
from app.core.database import get_db
from app.core.errors import NotImplementedFeature
from app.models import User
from app.modules.audit import MODULE_INFO, service
from app.modules.audit.schemas import AuditLogOut, ChainVerification
from app.schemas.common import Page, PageParams, page_params

router = APIRouter()


@router.get("/logs", response_model=Page[AuditLogOut])
def list_logs(
    event_type: str | None = Query(None, max_length=64),
    actor_id: uuid.UUID | None = None,
    since: datetime | None = None,
    until: datetime | None = None,
    page: PageParams = Depends(page_params),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Page[AuditLogOut]:
    """Admins see all events; other users only events where they are the actor."""
    raise NotImplementedFeature(MODULE_INFO, "Audit log listing")


@router.get("/verify", response_model=ChainVerification)
def verify(
    admin: User = Depends(require_admin), db: Session = Depends(get_db)
) -> ChainVerification:
    return service.verify_chain(db)
