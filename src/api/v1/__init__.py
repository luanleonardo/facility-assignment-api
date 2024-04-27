from fastapi import APIRouter

from src.api.v1.assignment_router import router as assignment_router

router = APIRouter(prefix="/v1")
router.include_router(assignment_router)
