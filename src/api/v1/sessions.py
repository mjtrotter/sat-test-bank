import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.models.tables import PracticeSession, Problem
from src.services.practice import PracticeService

router = APIRouter()

DB = Annotated[AsyncSession, Depends(get_db)]


# ── Schemas ──────────────────────────────────────────────────────────────────

class StartSessionRequest(BaseModel):
    student_id: uuid.UUID
    domain: str | None = None


class ProblemResponse(BaseModel):
    id: int
    problem_text: str
    contest_family: str | None = None
    contest_round: str | None = None
    difficulty_band: int | None = None

    model_config = {"from_attributes": True}


class StartSessionResponse(BaseModel):
    session_id: uuid.UUID
    first_problem: ProblemResponse


class SubmitAnswerRequest(BaseModel):
    session_id: uuid.UUID
    problem_id: int
    student_answer: str
    time_spent_seconds: int | None = None


class SubmitAnswerResponse(BaseModel):
    is_correct: bool
    correct_answer: str
    rating_change: float
    new_rating: float
    new_rd: float
    next_problem: ProblemResponse | None = None


class EndSessionRequest(BaseModel):
    session_id: uuid.UUID


class SessionSummary(BaseModel):
    session_id: str
    problems_attempted: int
    problems_correct: int
    accuracy: float
    rating_before: float | None
    rating_after: float | None
    rating_change: float
    difficulty_assessment: str
    duration_seconds: int | None = None


# ── Endpoints ────────────────────────────────────────────────────────────────

@router.post("/start", response_model=StartSessionResponse, status_code=201)
async def start_session(data: StartSessionRequest, db: DB):
    svc = PracticeService(db)
    try:
        session, problem = await svc.start_session(data.student_id, data.domain)
    except ValueError as e:
        raise HTTPException(404 if "not found" in str(e).lower() else 400, str(e))
    await db.commit()
    return StartSessionResponse(
        session_id=session.id,
        first_problem=ProblemResponse.model_validate(problem),
    )


@router.post("/answer", response_model=SubmitAnswerResponse)
async def submit_answer(data: SubmitAnswerRequest, db: DB):
    svc = PracticeService(db)
    try:
        is_correct, rating_change, next_problem = await svc.submit_answer(
            data.session_id, data.problem_id, data.student_answer, data.time_spent_seconds,
        )
    except ValueError as e:
        msg = str(e)
        if "not found" in msg.lower():
            raise HTTPException(404, msg)
        raise HTTPException(400, msg)

    # Get updated rating for response
    session = await db.get(PracticeSession, data.session_id)
    student_rating = await svc._get_student_rating(session.student_id, session.domain)
    problem = await db.get(Problem, data.problem_id)

    await db.commit()
    return SubmitAnswerResponse(
        is_correct=is_correct,
        correct_answer=problem.answer or "",
        rating_change=round(rating_change, 2),
        new_rating=round(student_rating.mu, 2),
        new_rd=round(student_rating.phi, 2),
        next_problem=ProblemResponse.model_validate(next_problem) if next_problem else None,
    )


@router.post("/end", response_model=SessionSummary)
async def end_session(data: EndSessionRequest, db: DB):
    svc = PracticeService(db)
    try:
        summary = await svc.end_session(data.session_id)
    except ValueError as e:
        raise HTTPException(404, str(e))
    await db.commit()
    return summary


@router.get("/{session_id}", response_model=SessionSummary)
async def get_session(session_id: uuid.UUID, db: DB):
    session = await db.get(PracticeSession, session_id)
    if not session:
        raise HTTPException(404, "Session not found")
    if not session.ended_at:
        raise HTTPException(400, "Session still active — end it first")
    svc = PracticeService(db)
    summary = await svc.end_session(session_id)
    return summary
