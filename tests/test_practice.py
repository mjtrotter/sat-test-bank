import uuid

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.api.app import create_app
from src.core.database import Base, get_db
from src.models.tables import (
    ItemRating,
    Problem,
    ProblemSkillTag,
    PracticeSession,
    SkillNode,
    Student,
)
from src.services.practice import PracticeService

# ── Test DB setup ────────────────────────────────────────────────────────────

TEST_DB_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture
async def engine():
    eng = create_async_engine(TEST_DB_URL, echo=False)
    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield eng
    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await eng.dispose()


@pytest_asyncio.fixture
async def db_session(engine):
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as session:
        yield session


@pytest_asyncio.fixture
async def seeded_db(db_session):
    """Seed the DB with a student, skill nodes, problems, and item ratings."""
    student = Student(
        id=uuid.UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"),
        display_name="Test Student",
        grade_level=7,
    )
    db_session.add(student)

    skill = SkillNode(
        id="ALG_LINEAR_EQ",
        name="Linear Equations",
        domain="algebra",
        level=2,
    )
    db_session.add(skill)

    problems = []
    for i in range(5):
        p = Problem(
            id=100 + i,
            contest_family="mathcounts",
            contest_year=2024,
            contest_round="sprint",
            problem_number=i + 1,
            problem_text=f"What is {i+1} + {i+2}?",
            answer=str(2 * i + 3),
            primary_domain="algebra",
        )
        problems.append(p)
        db_session.add(p)

    await db_session.flush()

    for p in problems:
        db_session.add(ProblemSkillTag(
            problem_id=p.id,
            skill_node_id="ALG_LINEAR_EQ",
        ))
        db_session.add(ItemRating(
            problem_id=p.id,
            difficulty_rating=1400.0 + p.problem_number * 50,
            difficulty_rd=100.0,
        ))

    await db_session.commit()
    return db_session


@pytest_asyncio.fixture
async def client(engine):
    """HTTPX async client wired to test DB."""
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async def _test_db():
        async with session_factory() as session:
            yield session

    app = create_app()
    app.dependency_overrides[get_db] = _test_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


# ── Service-level tests ─────────────────────────────────────────────────────

STUDENT_ID = uuid.UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa")


@pytest.mark.asyncio
async def test_start_session_creates_row(seeded_db):
    svc = PracticeService(seeded_db)
    session, problem = await svc.start_session(STUDENT_ID, domain="algebra")
    assert session.id is not None
    assert session.student_id == STUDENT_ID
    assert problem.problem_text is not None


@pytest.mark.asyncio
async def test_start_session_invalid_student(seeded_db):
    svc = PracticeService(seeded_db)
    with pytest.raises(ValueError, match="Student not found"):
        await svc.start_session(uuid.uuid4())


@pytest.mark.asyncio
async def test_submit_correct_answer_increases_rating(seeded_db):
    svc = PracticeService(seeded_db)
    session, problem = await svc.start_session(STUDENT_ID, domain="algebra")

    is_correct, change, next_prob = await svc.submit_answer(
        session.id, problem.id, problem.answer,
    )
    assert is_correct is True
    assert change > 0
    assert next_prob is not None


@pytest.mark.asyncio
async def test_submit_incorrect_answer_decreases_rating(seeded_db):
    svc = PracticeService(seeded_db)
    session, problem = await svc.start_session(STUDENT_ID, domain="algebra")

    is_correct, change, _ = await svc.submit_answer(
        session.id, problem.id, "wrong answer",
    )
    assert is_correct is False
    assert change < 0


@pytest.mark.asyncio
async def test_end_session_returns_summary(seeded_db):
    svc = PracticeService(seeded_db)
    session, problem = await svc.start_session(STUDENT_ID, domain="algebra")
    await svc.submit_answer(session.id, problem.id, problem.answer)

    summary = await svc.end_session(session.id)
    assert summary["problems_attempted"] == 1
    assert summary["problems_correct"] == 1
    assert summary["accuracy"] == 1.0
    assert summary["difficulty_assessment"] in ("too_easy", "appropriate", "too_hard")


@pytest.mark.asyncio
async def test_cannot_submit_to_ended_session(seeded_db):
    svc = PracticeService(seeded_db)
    session, problem = await svc.start_session(STUDENT_ID, domain="algebra")
    await svc.end_session(session.id)

    with pytest.raises(ValueError, match="already ended"):
        await svc.submit_answer(session.id, problem.id, "42")


# ── API-level tests ──────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_api_start_session(client, seeded_db):
    resp = await client.post("/api/v1/sessions/start", json={
        "student_id": str(STUDENT_ID),
        "domain": "algebra",
    })
    assert resp.status_code == 201
    data = resp.json()
    assert "session_id" in data
    assert "first_problem" in data


@pytest.mark.asyncio
async def test_api_invalid_student_404(client, seeded_db):
    resp = await client.post("/api/v1/sessions/start", json={
        "student_id": str(uuid.uuid4()),
    })
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_api_full_flow(client, seeded_db):
    # Start
    resp = await client.post("/api/v1/sessions/start", json={
        "student_id": str(STUDENT_ID),
        "domain": "algebra",
    })
    assert resp.status_code == 201
    start_data = resp.json()
    session_id = start_data["session_id"]
    problem = start_data["first_problem"]

    # Answer correctly
    resp = await client.post("/api/v1/sessions/answer", json={
        "session_id": session_id,
        "problem_id": problem["id"],
        "student_answer": "3",  # answer to first problem (1+2=3)
    })
    assert resp.status_code == 200
    answer_data = resp.json()
    assert "is_correct" in answer_data
    assert "rating_change" in answer_data

    # End session
    resp = await client.post("/api/v1/sessions/end", json={
        "session_id": session_id,
    })
    assert resp.status_code == 200
    summary = resp.json()
    assert summary["problems_attempted"] == 1
