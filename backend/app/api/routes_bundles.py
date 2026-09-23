from fastapi import APIRouter
from typing import List
from ..models.schema import BundleEvaluation
from ..services.block_planner import planner_service

router = APIRouter(prefix="/api/bundles", tags=["Bundles"])


@router.get("", response_model=List[BundleEvaluation])
def get_bundle_evaluations():
    """Returns Auto-Shadow bundling evaluations with WHY BUNDLE / WHY NOT reasons."""
    return planner_service.get_bundle_candidates()
