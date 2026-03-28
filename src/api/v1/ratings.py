import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.models.tables import StudentDomainRating, StudentGlobalRating, StudentRating

router = APIRouter()


class SkillRatingResponse(BaseModel):
    skill_node_id: str
    domain: str
    rating: float
    rating_deviation: float
    mastery_state: str
    total_attempts: int

    model_config = {"from_attributes": True}


class DomainRatingResponse(BaseModel):
    domain: str
    rating: float
    rating_deviation: float

    model_config = {"from_attributes": True}


class GlobalRatingResponse(BaseModel):
    rating: float
    rating_deviation: float
    nodes_proficient: int
    nodes_mastered: int

    model_config = {"from_attributes": True}


DB = Annotated[AsyncSession, Depends(get_db)]


@router.get("/students/{student_id}/skills", response_model=list[SkillRatingResponse])
async def get_skill_ratings(student_id: uuid.UUID, db: DB, domain: str | None = None):
    stmt = select(StudentRating).where(StudentRating.student_id == student_id)
    if domain:
        stmt = stmt.where(StudentRating.domain == domain)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.get("/students/{student_id}/domains", response_model=list[DomainRatingResponse])
async def get_domain_ratings(student_id: uuid.UUID, db: DB):
    stmt = select(StudentDomainRating).where(StudentDomainRating.student_id == student_id)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.get("/students/{student_id}/global", response_model=GlobalRatingResponse)
async def get_global_rating(student_id: uuid.UUID, db: DB):
    rating = await db.get(StudentGlobalRating, student_id)
    if not rating:
        raise HTTPException(404, "No global rating found for student")
    return rating
