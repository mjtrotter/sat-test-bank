import pytest
import os
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import text, select

from src.models.tables import Base, SkillNode, Problem, ProblemSkillTag
from src.services.skill_tagger import (
    classify_domain,
    estimate_level,
    match_skill_nodes,
    tag_problem,
    batch_tag,
    LEVEL_RULES,
)

DATABASE_URL = "sqlite+aiosqlite:///:memory:"

@pytest.fixture(scope="module")
async def async_engine():
    engine = create_async_engine(DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()

@pytest.fixture(scope="function")
async def async_session(async_engine):
    async_session_maker = async_sessionmaker(async_engine, expire_on_commit=False)
    async with async_session_maker() as session:
        yield session
        # Clean up data after each test
        await session.execute(text(f"DELETE FROM {ProblemSkillTag.__tablename__}"))
        await session.execute(text(f"DELETE FROM {Problem.__tablename__}"))
        await session.execute(text(f"DELETE FROM {SkillNode.__tablename__}"))
        await session.commit()

@pytest.fixture
async def seeded_session(async_session):
    # Seed 20 representative skill nodes
    nodes = [
        # ALG
        SkillNode(id="ALG_L1_EQ", name="Linear Equations", domain="ALG", level=1, prerequisites=[], source_mapping=[]),
        SkillNode(id="ALG_L2_QUAD", name="Quadratic Equations", domain="ALG", level=2, prerequisites=[], source_mapping=[]),
        SkillNode(id="ALG_L3_POLY", name="Polynomials", domain="ALG", level=3, prerequisites=[], source_mapping=[]),
        SkillNode(id="ALG_L4_SEQ", name="Sequences", domain="ALG", level=4, prerequisites=[], source_mapping=[]),
        SkillNode(id="ALG_L5_FUNC", name="Advanced Functions", domain="ALG", level=5, prerequisites=[], source_mapping=[]),
        # GEO
        SkillNode(id="GEO_L1_ANG", name="Angles", domain="GEO", level=1, prerequisites=[], source_mapping=[]),
        SkillNode(id="GEO_L2_TRI", name="Triangles", domain="GEO", level=2, prerequisites=[], source_mapping=[]),
        SkillNode(id="GEO_L3_CIRC", name="Circles", domain="GEO", level=3, prerequisites=[], source_mapping=[]),
        SkillNode(id="GEO_L4_POLY", name="Polygons", domain="GEO", level=4, prerequisites=[], source_mapping=[]),
        SkillNode(id="GEO_L5_3D", name="3D Geometry", domain="GEO", level=5, prerequisites=[], source_mapping=[]),
        # COUNT
        SkillNode(id="COUNT_L1_PROB", name="Basic Probability", domain="COUNT", level=1, prerequisites=[], source_mapping=[]),
        SkillNode(id="COUNT_L2_COMB", name="Combinations", domain="COUNT", level=2, prerequisites=[], source_mapping=[]),
        SkillNode(id="COUNT_L3_PERM", name="Permutations", domain="COUNT", level=3, prerequisites=[], source_mapping=[]),
        SkillNode(id="COUNT_L4_EXP", name="Expected Value", domain="COUNT", level=4, prerequisites=[], source_mapping=[]),
        # NT
        SkillNode(id="NT_L1_FACT", name="Factors", domain="NT", level=1, prerequisites=[], source_mapping=[]),
        SkillNode(id="NT_L2_PRIME", name="Primes", domain="NT", level=2, prerequisites=[], source_mapping=[]),
        SkillNode(id="NT_L3_MOD", name="Modular Arithmetic", domain="NT", level=3, prerequisites=[], source_mapping=[]),
        # ARITH
        SkillNode(id="ARITH_L1_FRAC", name="Fractions", domain="ARITH", level=1, prerequisites=[], source_mapping=[]),
        SkillNode(id="ARITH_L2_DEC", name="Decimals", domain="ARITH", level=2, prerequisites=[], source_mapping=[]),
        # LOGIC
        SkillNode(id="LOGIC_L1_TRUTH", name="Truth Tables", domain="LOGIC", level=1, prerequisites=[], source_mapping=[]),
    ]

    problems = [
        Problem(
            id=1,
            contest_family="amc10",
            contest_level=None,
            problem_number=25,
            problem_text="Find the roots of the quadratic equation polynomial x^2 - 5x + 6 = 0.",
            answer="2, 3",
        ),
        Problem(
            id=2,
            contest_family="gsm8k",
            contest_level=None,
            problem_number=1,
            problem_text="A triangle has angles 30, 60, 90. What is the ratio of sides?",
            answer="1:sqrt(3):2",
        ),
        Problem(
            id=3,
            contest_family="mathcounts",
            contest_level="state",
            problem_number=5,
            problem_text="What is the probability of picking a triangle with prime area?",
            answer="1/3",
        )
    ]

    async_session.add_all(nodes)
    async_session.add_all(problems)
    await async_session.commit()

    return async_session

# --- Domain Classification ---

def test_classify_domain_expected_problems():
    # ALG
    res_alg = classify_domain("Solve the equation for x in the polynomial.")
    assert res_alg and res_alg[0].domain == "ALG"

    # GEO
    res_geo = classify_domain("What is the area of the equilateral triangle?")
    assert res_geo and res_geo[0].domain == "GEO"

    # COUNT
    res_count = classify_domain("What is the probability of rolling a pair of dice?")
    assert res_count and res_count[0].domain == "COUNT"

    # NT
    res_nt = classify_domain("Find the greatest common divisor of the two prime numbers.")
    assert res_nt and res_nt[0].domain == "NT"

    # ARITH
    res_arith = classify_domain("What is the average speed of the train?")
    assert res_arith and res_arith[0].domain == "ARITH"

    # LOGIC
    res_logic = classify_domain("Construct a truth table for the logical statement.")
    assert res_logic and res_logic[0].domain == "LOGIC"


def test_classify_domain_multi_domain():
    text = "What is the probability that a randomly chosen triangle has a prime area and roots?"
    res = classify_domain(text)
    # Match COUNT (probability, randomly), GEO (triangle, area), NT (prime), ALG (roots)
    domains = [d.domain for d in res]
    assert "COUNT" in domains
    assert "GEO" in domains
    assert "NT" in domains
    assert "ALG" in domains
    # Order depends on keyword density (COUNT has 2: probability, randomly, GEO has 2: triangle, area)
    assert len(domains) >= 2


def test_classify_domain_empty_none():
    assert classify_domain("") == []
    assert classify_domain(None) == []


def test_classify_domain_latex():
    # Latex formatting shouldn't hide the keywords
    text = r"Given a \triangle ABC, find the \text{area} if the \text{probability} of picking point $P$ is prime."
    res = classify_domain(text)
    domains = [d.domain for d in res]
    assert "GEO" in domains # triangle, area
    assert "COUNT" in domains # probability
    assert "NT" in domains # prime

def test_classify_domain_score_normalization():
    # Provide many keywords for a single domain to test if score is capped at 1.0
    text = "triangle circle square pentagon angle area congruent pythagorean tangent coordinate cube diagonal"
    res = classify_domain(text)
    assert res[0].domain == "GEO"
    assert 0.0 < res[0].score <= 1.0

# --- Difficulty Level Estimation ---

def test_estimate_level_all_rules():
    assert estimate_level("gsm8k", None, None) == 1
    assert estimate_level("mathcounts", "chapter", None) == 1
    assert estimate_level("mathcounts", "state", None) == 2
    assert estimate_level("mathcounts", "national", None) == 3
    assert estimate_level("amc8", None, None) == 1
    assert estimate_level("amc10", None, None) == 2
    assert estimate_level("amc12", None, None) == 3
    assert estimate_level("amc_aime", None, None) == 4
    assert estimate_level("orca_math", None, None) == 1
    assert estimate_level("sat", None, None) == 1
    assert estimate_level("math_competition", None, None) == 2

def test_estimate_level_amc_bumps():
    # amc8
    assert estimate_level("amc8", None, 10) == 1 + 0
    assert estimate_level("amc8", None, 18) == 1 + 1
    assert estimate_level("amc8", None, 25) == 1 + 1

    # amc10
    assert estimate_level("amc10", None, 5) == 2 + 0
    assert estimate_level("amc10", None, 15) == 2 + 1
    assert estimate_level("amc10", None, 25) == 2 + 2 # level 4

    # amc_aime
    assert estimate_level("amc_aime", None, 3) == 4 + 0
    assert estimate_level("amc_aime", None, 8) == 4 + 1
    assert estimate_level("amc_aime", None, 15) == 4 + 1 # 5

def test_estimate_level_missing_metadata():
    assert estimate_level(None, None, None) == 2
    assert estimate_level("unknown_contest", None, None) == 2

def test_estimate_level_clamping():
    # Ensure it doesn't go below 1 or above 5
    assert estimate_level("amc_aime", None, 15) == 5

# --- Skill Node Matching ---

@pytest.mark.asyncio
async def test_match_skill_nodes_exact_match(seeded_session):
    candidates = await match_skill_nodes(seeded_session, "ALG", 2, 1.0)
    assert len(candidates) == 1
    assert candidates[0].skill_node_id == "ALG_L2_QUAD"
    assert candidates[0].confidence > 0

@pytest.mark.asyncio
async def test_match_skill_nodes_adjacent_fallback(seeded_session):
    # Suppose we ask for ARITH at level 3, but we only have L1 and L2.
    # Level 3 - 1 = Level 2 (ARITH_L2_DEC)
    candidates = await match_skill_nodes(seeded_session, "ARITH", 3, 1.0)
    assert len(candidates) == 1
    assert candidates[0].skill_node_id == "ARITH_L2_DEC"

@pytest.mark.asyncio
async def test_match_skill_nodes_confidence_decreases(seeded_session):
    # Compare exact match vs offset match
    cand_exact = await match_skill_nodes(seeded_session, "ARITH", 2, 1.0)
    cand_offset = await match_skill_nodes(seeded_session, "ARITH", 3, 1.0)

    assert cand_exact[0].confidence > cand_offset[0].confidence
    assert "shifted" in cand_offset[0].reason

@pytest.mark.asyncio
async def test_match_skill_nodes_invalid_domain(seeded_session):
    candidates = await match_skill_nodes(seeded_session, "UNKNOWN", 2, 1.0)
    assert len(candidates) == 0

# --- Batch Tagger Integration ---

@pytest.mark.asyncio
async def test_tag_problem_valid_candidates(seeded_session):
    # Problem 1: ALG, AMC10 #25 -> Level 4
    problem = (await seeded_session.execute(select(Problem).where(Problem.id == 1))).scalar_one()
    candidates = await tag_problem(seeded_session, problem)
    assert len(candidates) > 0
    assert any(c.skill_node_id == "ALG_L4_SEQ" for c in candidates)

@pytest.mark.asyncio
async def test_batch_tag_dry_run(seeded_session):
    stats = await batch_tag(seeded_session, dry_run=True, skip_tagged=False)
    assert stats["total"] > 0
    assert stats["tags_created"] == 0

    # Verify no db records were created
    tags = (await seeded_session.execute(select(ProblemSkillTag))).scalars().all()
    assert len(tags) == 0

@pytest.mark.asyncio
async def test_batch_tag_no_dry_run(seeded_session):
    stats = await batch_tag(seeded_session, dry_run=False, skip_tagged=False)
    assert stats["tagged"] > 0

    # Verify db records were created
    tags = (await seeded_session.execute(select(ProblemSkillTag))).scalars().all()
    assert len(tags) > 0

@pytest.mark.asyncio
async def test_batch_tag_skip_tagged(seeded_session):
    # First run without dry_run to tag problems
    await batch_tag(seeded_session, dry_run=False, skip_tagged=False)

    # Second run with skip_tagged=True
    stats = await batch_tag(seeded_session, dry_run=False, skip_tagged=True)

    # Since all problems were tagged in the first run, the second run should process 0 problems
    assert stats["total"] == 0
