from fastapi import APIRouter

from src.api.v1.health import router as health_router
from src.api.v1.students import router as students_router
from src.api.v1.problems import router as problems_router
from src.api.v1.ratings import router as ratings_router
from src.api.v1.sessions import router as sessions_router
from src.api.v1.coach import router as coach_router

router = APIRouter()
router.include_router(health_router, tags=["health"])
router.include_router(students_router, prefix="/students", tags=["students"])
router.include_router(problems_router, prefix="/problems", tags=["problems"])
router.include_router(ratings_router, prefix="/ratings", tags=["ratings"])
router.include_router(sessions_router, prefix="/sessions", tags=["sessions"])
router.include_router(coach_router, prefix="/coach", tags=["coach"])
