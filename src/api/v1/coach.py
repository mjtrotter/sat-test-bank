"""
Coach dashboard API — Mark's monitoring view.

Endpoints for class-wide visibility: student list with ratings,
skill heatmap, flagged explanations, and recent activity.
"""

import uuid
from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.models.tables import (
    Answer,
    PracticeSession,
    Problem,
    Student,
    StudentDomainRating,
    StudentGlobalRating,
    StudentRating,
)

router = APIRouter()

DB = Annotated[AsyncSession, Depends(get_db)]


# ── Schemas ──────────────────────────────────────────────────────────────────


class StudentOverview(BaseModel):
    id: uuid.UUID
    display_name: str
    grade_level: int
    global_rating: float | None
    global_rd: float | None
    domains: dict[str, float]  # domain → rating
    total_sessions: int
    total_problems: int
    accuracy: float | None
    last_active: datetime | None

    model_config = {"from_attributes": True}


class SkillHeatmapEntry(BaseModel):
    skill_node_id: str
    domain: str
    avg_rating: float
    avg_rd: float
    student_count: int
    mastery_distribution: dict[str, int]  # state → count


class FlaggedExplanation(BaseModel):
    problem_id: int
    problem_text: str
    contest_family: str | None
    explanation_flags: int
    explanation_rating: float | None

    model_config = {"from_attributes": True}


class RecentActivity(BaseModel):
    session_id: uuid.UUID
    student_id: uuid.UUID
    student_name: str
    domain: str | None
    started_at: datetime
    ended_at: datetime | None
    problems_attempted: int
    problems_correct: int
    rating_before: float | None
    rating_after: float | None


# ── Endpoints ────────────────────────────────────────────────────────────────


@router.get("/students", response_model=list[StudentOverview])
async def list_students_overview(db: DB):
    """All students with global rating, per-domain ratings, session stats."""
    students = (await db.execute(
        select(Student).order_by(Student.display_name)
    )).scalars().all()

    result = []
    for s in students:
        # Global rating
        gr = (await db.execute(
            select(StudentGlobalRating).where(
                StudentGlobalRating.student_id == s.id
            )
        )).scalar_one_or_none()

        # Domain ratings
        dr_rows = (await db.execute(
            select(StudentDomainRating).where(
                StudentDomainRating.student_id == s.id
            )
        )).scalars().all()
        domains = {dr.domain: round(dr.rating, 1) for dr in dr_rows}

        # Session stats
        stats = (await db.execute(
            select(
                func.count(PracticeSession.id),
                func.sum(PracticeSession.problems_attempted),
                func.sum(PracticeSession.problems_correct),
            ).where(PracticeSession.student_id == s.id)
        )).one()

        total_sessions = stats[0] or 0
        total_problems = stats[1] or 0
        total_correct = stats[2] or 0
        accuracy = round(total_correct / total_problems, 3) if total_problems > 0 else None

        result.append(StudentOverview(
            id=s.id,
            display_name=s.display_name,
            grade_level=s.grade_level,
            global_rating=round(gr.rating, 1) if gr else None,
            global_rd=round(gr.rating_deviation, 1) if gr else None,
            domains=domains,
            total_sessions=total_sessions,
            total_problems=total_problems,
            accuracy=accuracy,
            last_active=s.last_active,
        ))

    return result


@router.get("/students/{student_id}/skills", response_model=list[dict])
async def get_student_skill_detail(student_id: uuid.UUID, db: DB):
    """Per-student skill breakdown with mastery state and attempt counts."""
    student = await db.get(Student, student_id)
    if not student:
        raise HTTPException(404, "Student not found")

    ratings = (await db.execute(
        select(StudentRating).where(StudentRating.student_id == student_id)
        .order_by(StudentRating.domain, StudentRating.skill_node_id)
    )).scalars().all()

    return [
        {
            "skill_node_id": r.skill_node_id,
            "domain": r.domain,
            "rating": round(r.rating, 1),
            "rd": round(r.rating_deviation, 1),
            "mastery_state": r.mastery_state,
            "total_attempts": r.total_attempts,
            "last_updated": r.last_updated,
        }
        for r in ratings
    ]


@router.get("/heatmap", response_model=list[SkillHeatmapEntry])
async def class_skill_heatmap(db: DB, domain: str | None = None):
    """Class-wide skill node heatmap — avg rating and mastery distribution per node."""
    query = select(
        StudentRating.skill_node_id,
        StudentRating.domain,
        func.avg(StudentRating.rating).label("avg_rating"),
        func.avg(StudentRating.rating_deviation).label("avg_rd"),
        func.count(StudentRating.student_id).label("student_count"),
    ).group_by(StudentRating.skill_node_id, StudentRating.domain)

    if domain:
        query = query.where(StudentRating.domain == domain)

    rows = (await db.execute(query)).all()

    result = []
    for row in rows:
        # Get mastery distribution for this skill
        mastery_rows = (await db.execute(
            select(
                StudentRating.mastery_state,
                func.count(StudentRating.student_id),
            ).where(
                StudentRating.skill_node_id == row.skill_node_id
            ).group_by(StudentRating.mastery_state)
        )).all()

        mastery_dist = {m[0]: m[1] for m in mastery_rows}

        result.append(SkillHeatmapEntry(
            skill_node_id=row.skill_node_id,
            domain=row.domain,
            avg_rating=round(row.avg_rating, 1),
            avg_rd=round(row.avg_rd, 1),
            student_count=row.student_count,
            mastery_distribution=mastery_dist,
        ))

    return result


@router.get("/flagged-explanations", response_model=list[FlaggedExplanation])
async def list_flagged_explanations(
    db: DB,
    min_flags: int = Query(default=1, ge=1),
    limit: int = Query(default=50, le=200),
):
    """Problems with flagged explanations, sorted by flag count descending."""
    problems = (await db.execute(
        select(Problem)
        .where(Problem.explanation_flags >= min_flags)
        .order_by(Problem.explanation_flags.desc())
        .limit(limit)
    )).scalars().all()

    return [
        FlaggedExplanation(
            problem_id=p.id,
            problem_text=p.problem_text[:200],
            contest_family=p.contest_family,
            explanation_flags=p.explanation_flags,
            explanation_rating=round(p.explanation_rating, 2) if p.explanation_rating else None,
        )
        for p in problems
    ]


@router.get("/activity", response_model=list[RecentActivity])
async def recent_activity(
    db: DB,
    limit: int = Query(default=50, le=200),
):
    """Recent practice sessions across all students, newest first."""
    sessions = (await db.execute(
        select(PracticeSession, Student.display_name)
        .join(Student, PracticeSession.student_id == Student.id)
        .order_by(PracticeSession.started_at.desc())
        .limit(limit)
    )).all()

    return [
        RecentActivity(
            session_id=s.id,
            student_id=s.student_id,
            student_name=name,
            domain=s.domain,
            started_at=s.started_at,
            ended_at=s.ended_at,
            problems_attempted=s.problems_attempted,
            problems_correct=s.problems_correct,
            rating_before=s.rating_before,
            rating_after=s.rating_after,
        )
        for s, name in sessions
    ]
