import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import require_admin
from app.core.database import get_db
from app.core.errors import NotImplementedFeature
from app.models import User
from app.modules.llm_analysis import MODULE_INFO, service
from app.modules.llm_analysis.schemas import AnalysisOut, AnalysisRequest
from app.schemas.common import Page, PageParams, page_params

router = APIRouter()


@router.post("", response_model=AnalysisOut, status_code=status.HTTP_201_CREATED)
def run_analysis(
    data: AnalysisRequest, admin: User = Depends(require_admin), db: Session = Depends(get_db)
) -> AnalysisOut:
    return AnalysisOut.model_validate(service.analyze(db, admin.id, data))


@router.get("", response_model=Page[AnalysisOut])
def list_analyses(
    page: PageParams = Depends(page_params),
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> Page[AnalysisOut]:
    raise NotImplementedFeature(MODULE_INFO, "Analysis listing")


@router.get("/{analysis_id}", response_model=AnalysisOut)
def get_analysis(
    analysis_id: uuid.UUID, admin: User = Depends(require_admin), db: Session = Depends(get_db)
) -> AnalysisOut:
    raise NotImplementedFeature(MODULE_INFO, "Analysis retrieval")
