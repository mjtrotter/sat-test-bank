from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.models.tables import Problem

router = APIRouter()


class ProblemResponse(BaseModel):
    id: int
    contest_family: str
    contest_year: int | None
    contest_round: str | None
    contest_level: str | None
    problem_number: int | None
    problem_text: str
    answer: str | None
    primary_domain: str | None
    difficulty_band: int | None

    model_config = {"from_attributes": True}


DB = Annotated[AsyncSession, Depends(get_db)]


@router.get("/", response_model=list[ProblemResponse])
async def list_problems(
    db: DB,
    contest_family: str | None = None,
    contest_year: int | None = None,
    primary_domain: str | None = None,
    limit: int = Query(default=50, le=200),
    offset: int = 0,
):
    stmt = select(Problem)
    if contest_family:
        stmt = stmt.where(Problem.contest_family == contest_family)
    if contest_year:
        stmt = stmt.where(Problem.contest_year == contest_year)
    if primary_domain:
        stmt = stmt.where(Problem.primary_domain == primary_domain)
    stmt = stmt.offset(offset).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.get("/{problem_id}", response_model=ProblemResponse)
async def get_problem(problem_id: int, db: DB):
    problem = await db.get(Problem, problem_id)
    if not problem:
        raise HTTPException(404, "Problem not found")
    return problem
