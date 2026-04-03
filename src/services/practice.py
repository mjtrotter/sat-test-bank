"""
Practice session orchestration — ties Glicko-2, adaptive selection, and DB together.

Core gameplay loop: student starts session → gets problems → submits answers → ratings update.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import select, func as sa_func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.engine.adaptive import (
    ProblemCandidate,
    SelectionResult,
    estimate_session_difficulty,
    select_next_problem,
)
from src.engine.glicko2 import Rating, update_rating_single
from src.models.tables import (
    Answer,
    ItemRating,
    PracticeSession,
    Problem,
    ProblemSkillTag,
    Student,
    StudentDomainRating,
    StudentGlobalRating,
    StudentRating,
)


def _ensure_utc(dt: datetime) -> datetime:
    """Normalize naive datetimes (from SQLite) to UTC-aware."""
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt


class PracticeService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def start_session(
        self, student_id: uuid.UUID, domain: str | None = None
    ) -> tuple[PracticeSession, Problem]:
        student = await self.db.get(Student, student_id)
        if not student:
            raise ValueError("Student not found")

        # Get student's rating for selection
        student_rating = await self._get_student_rating(student_id, domain)

        # Build candidate pool
        candidates = await self._build_candidates(student_id, domain)
        if not candidates:
            raise ValueError("No problems available")

        # Recently seen problem IDs (last 7 days)
        recent_ids = await self._recently_seen_ids(student_id)

        # Mastered skill node IDs
        mastered = await self._mastered_skill_ids(student_id)

        # Select first problem
        selection = select_next_problem(
            student_rating, candidates, domain, recent_ids, mastered,
        )
        if selection is None:
            raise ValueError("No suitable problems after filtering")

        problem = await self.db.get(Problem, int(selection.problem.id))

        # Create session
        session = PracticeSession(
            student_id=student_id,
            domain=domain,
            rating_before=student_rating.mu,
        )
        self.db.add(session)
        await self.db.flush()

        return session, problem

    async def submit_answer(
        self,
        session_id: uuid.UUID,
        problem_id: int,
        student_answer: str,
        time_spent: int | None = None,
    ) -> tuple[bool, float, Problem | None]:
        session = await self.db.get(PracticeSession, session_id)
        if not session:
            raise ValueError("Session not found")
        if session.ended_at is not None:
            raise ValueError("Session already ended")

        problem = await self.db.get(Problem, problem_id)
        if not problem:
            raise ValueError("Problem not found")

        # Check answer
        is_correct = self._check_answer(problem.answer or "", student_answer)

        # Get current student rating (domain-level or global)
        student_rating = await self._get_student_rating(session.student_id, session.domain)
        rating_before = student_rating.mu

        # Get problem difficulty rating
        item_rating = await self._get_item_rating(problem_id)
        problem_rating = Rating(
            mu=item_rating.difficulty_rating,
            phi=item_rating.difficulty_rd,
            sigma=item_rating.difficulty_volatility,
        )

        # Update student rating via Glicko-2
        score = 1.0 if is_correct else 0.0
        new_rating = update_rating_single(student_rating, problem_rating, score)
        rating_change = new_rating.mu - rating_before

        # Persist rating update
        await self._update_student_rating(session.student_id, session.domain, new_rating)

        # Record answer
        answer = Answer(
            session_id=session_id,
            problem_id=problem_id,
            student_answer=student_answer,
            is_correct=is_correct,
            time_spent_seconds=time_spent,
            rating_before=rating_before,
            rating_after=new_rating.mu,
        )
        self.db.add(answer)

        # Update session counters
        session.problems_attempted += 1
        if is_correct:
            session.problems_correct += 1

        # Select next problem
        candidates = await self._build_candidates(session.student_id, session.domain)
        recent_ids = await self._recently_seen_ids(session.student_id)
        mastered = await self._mastered_skill_ids(session.student_id)

        selection = select_next_problem(
            new_rating, candidates, session.domain, recent_ids, mastered,
        )
        next_problem = None
        if selection:
            next_problem = await self.db.get(Problem, int(selection.problem.id))

        await self.db.flush()

        return is_correct, rating_change, next_problem

    async def end_session(self, session_id: uuid.UUID) -> dict:
        session = await self.db.get(PracticeSession, session_id)
        if not session:
            raise ValueError("Session not found")

        session.ended_at = datetime.now(timezone.utc)

        # Get current rating for after-snapshot
        student_rating = await self._get_student_rating(session.student_id, session.domain)
        session.rating_after = student_rating.mu

        # Load answers for summary
        result = await self.db.execute(
            select(Answer).where(Answer.session_id == session_id)
        )
        answers = result.scalars().all()

        attempted = session.problems_attempted
        correct = session.problems_correct
        accuracy = correct / attempted if attempted > 0 else 0.0

        # Difficulty assessment
        answer_tuples = []
        for a in answers:
            prob = await self.db.get(Problem, a.problem_id)
            if prob:
                item_r = await self._get_item_rating(a.problem_id)
                pc = ProblemCandidate(
                    id=str(a.problem_id),
                    difficulty=Rating(mu=item_r.difficulty_rating, phi=item_r.difficulty_rd),
                    domain=session.domain or "",
                    skill_node_ids=[],
                )
                answer_tuples.append((pc, a.is_correct))

        difficulty = estimate_session_difficulty(student_rating, answer_tuples)

        duration = None
        if session.started_at and session.ended_at:
            duration = int((_ensure_utc(session.ended_at) - _ensure_utc(session.started_at)).total_seconds())

        await self.db.flush()

        return {
            "session_id": str(session.id),
            "problems_attempted": attempted,
            "problems_correct": correct,
            "accuracy": round(accuracy, 3),
            "rating_before": session.rating_before,
            "rating_after": session.rating_after,
            "rating_change": round((session.rating_after or 0) - (session.rating_before or 0), 2),
            "difficulty_assessment": difficulty,
            "duration_seconds": duration,
        }

    # ── Private helpers ──────────────────────────────────────────────────────

    async def _get_student_rating(
        self, student_id: uuid.UUID, domain: str | None
    ) -> Rating:
        if domain:
            result = await self.db.execute(
                select(StudentDomainRating).where(
                    StudentDomainRating.student_id == student_id,
                    StudentDomainRating.domain == domain,
                )
            )
            dr = result.scalar_one_or_none()
            if dr:
                return Rating(mu=dr.rating, phi=dr.rating_deviation, sigma=dr.volatility)

        result = await self.db.execute(
            select(StudentGlobalRating).where(
                StudentGlobalRating.student_id == student_id
            )
        )
        gr = result.scalar_one_or_none()
        if gr:
            return Rating(mu=gr.rating, phi=gr.rating_deviation, sigma=gr.volatility)

        return Rating()  # defaults

    async def _update_student_rating(
        self, student_id: uuid.UUID, domain: str | None, new_rating: Rating
    ) -> None:
        now = datetime.now(timezone.utc)

        if domain:
            result = await self.db.execute(
                select(StudentDomainRating).where(
                    StudentDomainRating.student_id == student_id,
                    StudentDomainRating.domain == domain,
                )
            )
            dr = result.scalar_one_or_none()
            if dr:
                dr.rating = new_rating.mu
                dr.rating_deviation = new_rating.phi
                dr.volatility = new_rating.sigma
                dr.last_updated = now
            else:
                self.db.add(StudentDomainRating(
                    student_id=student_id,
                    domain=domain,
                    rating=new_rating.mu,
                    rating_deviation=new_rating.phi,
                    volatility=new_rating.sigma,
                    last_updated=now,
                ))

        # Always update global
        result = await self.db.execute(
            select(StudentGlobalRating).where(
                StudentGlobalRating.student_id == student_id
            )
        )
        gr = result.scalar_one_or_none()
        if gr:
            gr.rating = new_rating.mu
            gr.rating_deviation = new_rating.phi
            gr.volatility = new_rating.sigma
            gr.last_updated = now
        else:
            self.db.add(StudentGlobalRating(
                student_id=student_id,
                rating=new_rating.mu,
                rating_deviation=new_rating.phi,
                volatility=new_rating.sigma,
                last_updated=now,
            ))

    async def _get_item_rating(self, problem_id: int) -> ItemRating:
        result = await self.db.execute(
            select(ItemRating).where(ItemRating.problem_id == problem_id)
        )
        ir = result.scalar_one_or_none()
        if ir:
            return ir
        # No calibrated rating yet — return defaults
        default = ItemRating(
            problem_id=problem_id,
            difficulty_rating=1500.0,
            difficulty_rd=300.0,
            difficulty_volatility=0.06,
        )
        return default

    async def _build_candidates(
        self, student_id: uuid.UUID, domain: str | None
    ) -> list[ProblemCandidate]:
        query = select(Problem).outerjoin(ItemRating)
        if domain:
            query = query.where(Problem.primary_domain == domain)

        result = await self.db.execute(query)
        problems = result.scalars().all()

        candidates = []
        for p in problems:
            # Get item rating
            ir_result = await self.db.execute(
                select(ItemRating).where(ItemRating.problem_id == p.id)
            )
            ir = ir_result.scalar_one_or_none()

            diff_mu = ir.difficulty_rating if ir else 1500.0
            diff_phi = ir.difficulty_rd if ir else 300.0
            disc = ir.discrimination if ir else 1.0
            guess = ir.guessing if ir else 0.0

            # Get skill tags
            tags_result = await self.db.execute(
                select(ProblemSkillTag.skill_node_id).where(
                    ProblemSkillTag.problem_id == p.id
                )
            )
            skill_ids = [row[0] for row in tags_result.all()]

            # Get last_seen_days
            ans_result = await self.db.execute(
                select(sa_func.max(Answer.answered_at)).where(
                    Answer.problem_id == p.id,
                    Answer.session_id.in_(
                        select(PracticeSession.id).where(
                            PracticeSession.student_id == student_id
                        )
                    ),
                )
            )
            last_answered = ans_result.scalar_one_or_none()
            last_seen_days = None
            if last_answered:
                last_seen_days = (datetime.now(timezone.utc) - _ensure_utc(last_answered)).days

            candidates.append(ProblemCandidate(
                id=str(p.id),
                difficulty=Rating(mu=diff_mu, phi=diff_phi),
                domain=p.primary_domain or "",
                skill_node_ids=skill_ids,
                discrimination=disc,
                guessing=guess,
                last_seen_days=last_seen_days,
            ))

        return candidates

    async def _recently_seen_ids(self, student_id: uuid.UUID) -> set[str]:
        result = await self.db.execute(
            select(Answer.problem_id, Answer.answered_at)
            .join(PracticeSession)
            .where(PracticeSession.student_id == student_id)
        )
        cutoff = datetime.now(timezone.utc)
        return {
            str(row[0])
            for row in result.all()
            if row[1] and (cutoff - _ensure_utc(row[1])).days < 7
        }

    async def _mastered_skill_ids(self, student_id: uuid.UUID) -> set[str]:
        result = await self.db.execute(
            select(StudentRating.skill_node_id).where(
                StudentRating.student_id == student_id,
                StudentRating.mastery_state.in_(["proficient", "mastered"]),
            )
        )
        return {row[0] for row in result.all()}

    @staticmethod
    def _check_answer(correct: str, submitted: str) -> bool:
        return correct.strip().lower() == submitted.strip().lower()
