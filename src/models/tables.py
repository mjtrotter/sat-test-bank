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
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database import Base
from src.models.enums import CalibrationSource, ContestFamily, Domain, MasteryState, RoundType


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
    prerequisites: Mapped[dict | None] = mapped_column(JSONB)  # list of prerequisite node IDs
    source_mapping: Mapped[dict | None] = mapped_column(JSONB)  # book + chapter references
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    tags: Mapped[list["ProblemSkillTag"]] = relationship(back_populates="skill_node")
    lesson: Mapped["Lesson | None"] = relationship(back_populates="skill_node")


# ── Problems ─────────────────────────────────────────────────────────────────

class Problem(Base):
    __tablename__ = "problems"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    contest_family: Mapped[str] = mapped_column(String(30), index=True)
    contest_year: Mapped[int | None] = mapped_column(Integer, index=True)
    contest_round: Mapped[str | None] = mapped_column(String(30))
    contest_level: Mapped[str | None] = mapped_column(String(30))  # chapter/state/national
    problem_number: Mapped[int | None] = mapped_column(Integer)
    problem_text: Mapped[str] = mapped_column(Text)
    answer: Mapped[str | None] = mapped_column(String(200))
    official_solution: Mapped[str | None] = mapped_column(Text)
    mark_explanation: Mapped[str | None] = mapped_column(Text)
    mark_audio_url: Mapped[str | None] = mapped_column(String(500))
    mark_diagram_url: Mapped[str | None] = mapped_column(String(500))
    personality_variants: Mapped[dict | None] = mapped_column(JSONB)
    explanation_rating: Mapped[float | None] = mapped_column(Float)
    explanation_flags: Mapped[int] = mapped_column(Integer, default=0)
    latex_content: Mapped[str | None] = mapped_column(Text)
    difficulty_band: Mapped[int | None] = mapped_column(Integer)  # 1-5
    primary_domain: Mapped[str | None] = mapped_column(String(30), index=True)
    problem_style: Mapped[str | None] = mapped_column(String(50))
    source_path: Mapped[str | None] = mapped_column(String(500))  # original PDF path
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index("ix_problems_source_lookup", "contest_family", "contest_year", "contest_round", "problem_number"),
    )

    figures: Mapped[list["ProblemFigure"]] = relationship(back_populates="problem")
    skill_tags: Mapped[list["ProblemSkillTag"]] = relationship(back_populates="problem")
    item_rating: Mapped["ItemRating | None"] = relationship(back_populates="problem")


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

    problem: Mapped["Problem"] = relationship(back_populates="skill_tags")
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
    worked_examples: Mapped[dict | None] = mapped_column(JSONB)
    visual_aids: Mapped[dict | None] = mapped_column(JSONB)
    mark_recording_url: Mapped[str | None] = mapped_column(String(500))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    skill_node: Mapped["SkillNode"] = relationship(back_populates="lesson")
