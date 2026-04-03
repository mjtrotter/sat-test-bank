import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.types import JSON # Use generic JSON type
from sqlalchemy.orm import Mapped, mapped_column, relationship # Added this line

from src.core.database import Base
from src.models.enums import MasteryState, CalibrationSource, ContestFamily, RoundType, Domain, AnswerType, GradeBand, TextFormat

# ── Students ──────────────────────────────────────────────────────────────────

class Student(Base):
    __tablename__ = "students"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    display_name: Mapped[str] = mapped_column(String(50))
    grade_level: Mapped[int] = mapped_column(Integer)
    school: Mapped[str | None] = mapped_column(String(200))
    roast_preference: Mapped[float] = mapped_column(Float, default=0.0)
    mini_game_preference: Mapped[str | None] = mapped_column(String(50))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    last_active: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    ratings: Mapped[list["StudentRating"]] = relationship(back_populates="student")
    domain_ratings: Mapped[list["StudentDomainRating"]] = relationship(back_populates="student")
    global_rating: Mapped["StudentGlobalRating | None"] = relationship(back_populates="student")


# ── Skill Nodes (Taxonomy) ───────────────────────────────────────────────────

class SkillNode(Base):
    __tablename__ = "skill_nodes"

    id: Mapped[str] = mapped_column(String(80), primary_key=True)  # e.g. 'COMB_GRID_PATHS'
    name: Mapped[str] = mapped_column(String(200))
    description: Mapped[str | None] = mapped_column(Text)
    domain: Mapped[str] = mapped_column(String(30), index=True)
    level: Mapped[int] = mapped_column(Integer, index=True)
    prerequisites: Mapped[list | None] = mapped_column(JSON)  # list of prerequisite node IDs
    source_mapping: Mapped[list | None] = mapped_column(JSON)  # book + chapter references
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    tags: Mapped[list["ProblemSkillTag"]] = relationship(back_populates="skill_node")
    lesson: Mapped["Lesson | None"] = relationship(back_populates="skill_node")


# ── Problems ─────────────────────────────────────────────────────────────────

class Problem(Base):
    __tablename__ = "problems"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    external_id: Mapped[str | None] = mapped_column(String(40), unique=True, index=True)  # v3 UUID for dedup
    contest_family: Mapped[str] = mapped_column(String(50), index=True)
    contest_year: Mapped[int | None] = mapped_column(Integer, index=True)
    contest_round: Mapped[str | None] = mapped_column(String(30))
    contest_level: Mapped[str | None] = mapped_column(String(30))  # chapter/state/national
    problem_number: Mapped[int | None] = mapped_column(Integer)
    problem_text: Mapped[str] = mapped_column(Text)
    text_format: Mapped[str] = mapped_column(String(10), default="plain")  # plain, latex
    answer: Mapped[str | None] = mapped_column(Text)
    answer_type: Mapped[str | None] = mapped_column(String(30), index=True)  # numeric, multiple_choice, expression
    choices: Mapped[list | None] = mapped_column(JSON)  # MC options: [{"l":"A","t":"...","c":true}]
    official_solution: Mapped[str | None] = mapped_column(Text)
    mark_explanation: Mapped[str | None] = mapped_column(Text)
    mark_audio_url: Mapped[str | None] = mapped_column(String(500))
    mark_diagram_url: Mapped[str | None] = mapped_column(String(500))
    personality_variants: Mapped[dict | None] = mapped_column(JSON)
    explanation_rating: Mapped[float | None] = mapped_column(Float)
    explanation_flags: Mapped[int] = mapped_column(Integer, server_default="0")
    latex_content: Mapped[str | None] = mapped_column(Text)
    difficulty_band: Mapped[int | None] = mapped_column(Integer)  # 1-5
    difficulty_source: Mapped[str | None] = mapped_column(String(30))
    primary_domain: Mapped[str | None] = mapped_column(String(50), index=True)
    subject: Mapped[str | None] = mapped_column(String(100), index=True)  # algebra, geometry, etc.
    grade_band: Mapped[str | None] = mapped_column(String(20), index=True)  # ms, hs, ap, col, grad
    problem_style: Mapped[str | None] = mapped_column(String(50))
    requires_visual: Mapped[bool] = mapped_column(Boolean, default=False)
    source_dataset: Mapped[str | None] = mapped_column(String(50), index=True)  # numinamath_cot, gsm8k, etc.
    source_path: Mapped[str | None] = mapped_column(String(500))
    source_url: Mapped[str | None] = mapped_column(String(500))
    extraction_method: Mapped[str | None] = mapped_column(String(50))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index("ix_problems_source_lookup", "contest_family", "contest_year", "contest_round", "problem_number"),
        Index("ix_problems_difficulty_domain", "primary_domain", "difficulty_band"),
        Index("ix_problems_grade_subject", "grade_band", "subject"),
    )

    figures: Mapped[list["ProblemFigure"]] = relationship(back_populates="problem", cascade="all, delete-orphan")
    skill_tags: Mapped[list["ProblemSkillTag"]] = relationship(back_populates="problem", cascade="all, delete-orphan")
    item_rating: Mapped["ItemRating | None"] = relationship(back_populates="problem", cascade="all, delete-orphan")


class ProblemFigure(Base):
    __tablename__ = "problem_figures"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    problem_id: Mapped[int] = mapped_column(ForeignKey("problems.id", ondelete="CASCADE"), index=True)
    figure_path: Mapped[str] = mapped_column(String(500))
    figure_type: Mapped[str | None] = mapped_column(String(30))  # diagram, chart, graph
    page_number: Mapped[int | None] = mapped_column(Integer)

    problem: Mapped["Problem"] = relationship(back_populates="figures")


class ProblemSkillTag(Base):
    __tablename__ = "problem_skill_tags"

    problem_id: Mapped[int] = mapped_column(ForeignKey("problems.id", ondelete="CASCADE"), primary_key=True)
    skill_node_id: Mapped[str] = mapped_column(ForeignKey("skill_nodes.id"), primary_key=True)
    confidence: Mapped[float] = mapped_column(Float, default=1.0)  # 1.0 = primary, 0.5 = secondary
    tagged_by: Mapped[str] = mapped_column(String(30), default="auto")  # auto, manual, llm

    problem: Mapped["Problem"] = relationship(back_populates="skill_tags") # Corrected
    skill_node: Mapped["SkillNode"] = relationship(back_populates="tags")


# ── Student Ratings (Glicko-2) ───────────────────────────────────────────────

class StudentRating(Base):
    __tablename__ = "student_ratings"

    student_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("students.id", ondelete="CASCADE"), primary_key=True
    )
    skill_node_id: Mapped[str] = mapped_column(
        ForeignKey("skill_nodes.id"), primary_key=True
    )
    domain: Mapped[str] = mapped_column(String(30), index=True)
    rating: Mapped[float] = mapped_column(Float, default=1500.0)
    rating_deviation: Mapped[float] = mapped_column(Float, default=350.0)
    volatility: Mapped[float] = mapped_column(Float, default=0.06)
    mastery_state: Mapped[str] = mapped_column(String(20), default=MasteryState.LOCKED.value)
    total_attempts: Mapped[int] = mapped_column(Integer, default=0)
    last_updated: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    student: Mapped["Student"] = relationship(back_populates="ratings")


class StudentDomainRating(Base):
    __tablename__ = "student_domain_ratings"

    student_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("students.id", ondelete="CASCADE"), primary_key=True
    )
    domain: Mapped[str] = mapped_column(String(30), primary_key=True)
    rating: Mapped[float] = mapped_column(Float, default=1500.0)
    rating_deviation: Mapped[float] = mapped_column(Float, default=350.0)
    volatility: Mapped[float] = mapped_column(Float, default=0.06)
    last_updated: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    student: Mapped["Student"] = relationship(back_populates="domain_ratings")


class StudentGlobalRating(Base):
    __tablename__ = "student_global_ratings"

    student_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("students.id", ondelete="CASCADE"), primary_key=True
    )
    rating: Mapped[float] = mapped_column(Float, default=1500.0)
    rating_deviation: Mapped[float] = mapped_column(Float, default=350.0)
    volatility: Mapped[float] = mapped_column(Float, default=0.06)
    nodes_proficient: Mapped[int] = mapped_column(Integer, default=0)
    nodes_mastered: Mapped[int] = mapped_column(Integer, default=0)
    last_updated: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    student: Mapped["Student"] = relationship(back_populates="global_rating")


# ── Item Difficulty Ratings ──────────────────────────────────────────────────

class ItemRating(Base):
    __tablename__ = "item_ratings"

    problem_id: Mapped[int] = mapped_column(
        ForeignKey("problems.id", ondelete="CASCADE"), primary_key=True
    )
    difficulty_rating: Mapped[float] = mapped_column(Float, default=1500.0)
    difficulty_rd: Mapped[float] = mapped_column(Float, default=300.0)
    difficulty_volatility: Mapped[float] = mapped_column(Float, default=0.06)
    solve_rate: Mapped[float | None] = mapped_column(Float)
    discrimination: Mapped[float] = mapped_column(Float, default=1.0)  # IRT 'a'
    guessing: Mapped[float] = mapped_column(Float, default=0.25)  # IRT 'c'
    calibration_source: Mapped[str | None] = mapped_column(String(30))
    mini_model_solve_rate: Mapped[float | None] = mapped_column(Float)
    total_attempts: Mapped[int] = mapped_column(Integer, default=0)
    last_calibrated: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    problem: Mapped["Problem"] = relationship(back_populates="item_rating")


# ── Lessons ──────────────────────────────────────────────────────────────────

class Lesson(Base):
    __tablename__ = "lessons"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    skill_node_id: Mapped[str] = mapped_column(
        ForeignKey("skill_nodes.id"), unique=True, index=True
    )
    lesson_type: Mapped[str] = mapped_column(String(30), default="text")  # text, video, recording
    content: Mapped[str | None] = mapped_column(Text)  # markdown + LaTeX
    worked_examples: Mapped[dict | None] = mapped_column(JSON)
    visual_aids: Mapped[dict | None] = mapped_column(JSON)
    mark_recording_url: Mapped[str | None] = mapped_column(String(500))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    skill_node: Mapped["SkillNode"] = relationship(back_populates="lesson")


# ── Practice Sessions ───────────────────────────────────────────────────────

class PracticeSession(Base):
    __tablename__ = "practice_sessions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("students.id", ondelete="CASCADE"), index=True
    )
    domain: Mapped[str | None] = mapped_column(String(30))
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    problems_attempted: Mapped[int] = mapped_column(Integer, default=0)
    problems_correct: Mapped[int] = mapped_column(Integer, default=0)
    rating_before: Mapped[float | None] = mapped_column(Float)
    rating_after: Mapped[float | None] = mapped_column(Float)

    student: Mapped["Student"] = relationship()
    answers: Mapped[list["Answer"]] = relationship(back_populates="session")


class Answer(Base):
    __tablename__ = "answers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("practice_sessions.id", ondelete="CASCADE"), index=True
    )
    problem_id: Mapped[int] = mapped_column(ForeignKey("problems.id"), index=True)
    student_answer: Mapped[str] = mapped_column(String(500))
    is_correct: Mapped[bool] = mapped_column(Boolean)
    time_spent_seconds: Mapped[int | None] = mapped_column(Integer)
    rating_before: Mapped[float] = mapped_column(Float)
    rating_after: Mapped[float] = mapped_column(Float)
    answered_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    session: Mapped["PracticeSession"] = relationship(back_populates="answers")
    problem: Mapped["Problem"] = relationship()


# ── Calibration Pipeline ───────────────────────────────────────────────────

class CalibrationRun(Base):
    __tablename__ = "calibration_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    status: Mapped[str] = mapped_column(String(20), default="running")  # running, completed, failed
    model_count: Mapped[int] = mapped_column(Integer, default=0)
    problem_count: Mapped[int] = mapped_column(Integer, default=0)
    config: Mapped[dict | None] = mapped_column(JSON)  # band configs, prompt template version, routing
    notes: Mapped[str | None] = mapped_column(Text)

    responses: Mapped[list["CalibrationResponse"]] = relationship(
        back_populates="run", cascade="all, delete-orphan"
    )


class CalibrationResponse(Base):
    __tablename__ = "calibration_responses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    run_id: Mapped[int] = mapped_column(ForeignKey("calibration_runs.id", ondelete="CASCADE"), index=True)
    model_id: Mapped[str] = mapped_column(String(120), index=True)  # e.g. 'Qwen2.5-0.5B-Instruct-4bit'
    model_band: Mapped[int] = mapped_column(Integer, index=True)
    problem_id: Mapped[int] = mapped_column(ForeignKey("problems.id", ondelete="CASCADE"), index=True)
    prompt_tokens: Mapped[int | None] = mapped_column(Integer)
    completion_tokens: Mapped[int | None] = mapped_column(Integer)
    response_text: Mapped[str | None] = mapped_column(Text)  # full CoT output — the "solution"
    extracted_answer: Mapped[str | None] = mapped_column(String(500))
    is_correct: Mapped[bool | None] = mapped_column(Boolean)
    latency_ms: Mapped[int | None] = mapped_column(Integer)
    error: Mapped[str | None] = mapped_column(Text)  # null if successful
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        UniqueConstraint("run_id", "model_id", "problem_id", name="uq_run_model_problem"),
        Index("ix_calibration_model_correct", "model_id", "is_correct"),
    )

    run: Mapped["CalibrationRun"] = relationship(back_populates="responses")
    problem: Mapped["Problem"] = relationship()