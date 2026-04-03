import pytest
import asyncio
import json
from unittest.mock import AsyncMock, MagicMock, patch

from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from src.models.tables import Base, Problem, SkillNode, ProblemSkillTag
from src.services.llm_tagger import (
    build_taxonomy_context,
    format_problems_block,
    classify_batch_claude,
    batch_tag_llm,
    TagResult
)

DATABASE_URL = "sqlite+aiosqlite:///:memory:"

@pytest.fixture(scope="function")
async def async_session():
    engine = create_async_engine(DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session_maker = async_sessionmaker(engine, expire_on_commit=False)
    async with async_session_maker() as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()

@pytest.mark.asyncio
async def test_build_taxonomy_context(async_session):
    # Setup test data
    nodes = [
        SkillNode(id="ALG_L1", name="Algebra 1", domain="ALG", level=1),
        SkillNode(id="ALG_L2", name="Algebra 2", domain="ALG", level=2),
        SkillNode(id="GEO_L1", name="Geometry 1", domain="GEO", level=1),
    ]
    async_session.add_all(nodes)
    await async_session.commit()

    context = await build_taxonomy_context(async_session)

    assert "## ALG" in context
    assert "### Level 1" in context
    assert "- ALG_L1: Algebra 1" in context
    assert "### Level 2" in context
    assert "- ALG_L2: Algebra 2" in context
    assert "## GEO" in context
    assert "- GEO_L1: Geometry 1" in context

def test_format_problems_block():
    problems = [
        {"id": 1, "problem_text": "Short problem."},
        {"id": 2, "problem_text": "A" * 1000},  # Long problem
    ]
    block = format_problems_block(problems)

    assert "Problem 1:\nShort problem." in block
    assert "Problem 2:\n" + ("A" * 500) in block
    assert len(block) < 1000

@pytest.mark.asyncio
@patch("anthropic.AsyncAnthropic")
async def test_classify_batch_claude(mock_anthropic):
    # Setup mock
    mock_client = MagicMock()
    mock_messages = AsyncMock()

    # Valid JSON response
    mock_response_valid = MagicMock()
    mock_response_valid.content = [
        MagicMock(text='[{"problem_id": 1, "tags": [{"skill_node_id": "ALG_L1", "confidence": 0.8}]}]')
    ]
    mock_messages.create.return_value = mock_response_valid
    mock_client.messages = mock_messages
    mock_anthropic.return_value = mock_client

    problems = [{"id": 1, "problem_text": "Solve for x."}]

    results = await classify_batch_claude(problems, "Taxonomy Context", "fake_key")

    assert len(results) == 1
    assert results[0].problem_id == 1
    assert results[0].skill_node_id == "ALG_L1"
    assert results[0].confidence == 0.8

@pytest.mark.asyncio
@patch("anthropic.AsyncAnthropic")
async def test_classify_batch_claude_malformed_json(mock_anthropic):
    mock_client = MagicMock()
    mock_messages = AsyncMock()

    # Malformed JSON response
    mock_response_malformed = MagicMock()
    mock_response_malformed.content = [MagicMock(text='[{"problem_id": 1, "tags": [{"skill_node_id": "ALG_L1", "confidence": 0.8}]}')]

    mock_messages.create.return_value = mock_response_malformed
    mock_client.messages = mock_messages
    mock_anthropic.return_value = mock_client

    problems = [{"id": 1, "problem_text": "Solve for x."}]

    results = await classify_batch_claude(problems, "Taxonomy Context", "fake_key", max_retries=0)
    assert results == []

@pytest.mark.asyncio
@patch("anthropic.AsyncAnthropic")
async def test_classify_batch_claude_empty_response(mock_anthropic):
    mock_client = MagicMock()
    mock_messages = AsyncMock()

    mock_response_empty = MagicMock()
    mock_response_empty.content = [MagicMock(text='No tags found.')]

    mock_messages.create.return_value = mock_response_empty
    mock_client.messages = mock_messages
    mock_anthropic.return_value = mock_client

    problems = [{"id": 1, "problem_text": "Solve for x."}]

    results = await classify_batch_claude(problems, "Taxonomy Context", "fake_key", max_retries=0)
    assert results == []

@pytest.mark.asyncio
async def test_batch_tag_llm_dry_run(async_session):
    # Setup test data
    problems = [
        Problem(contest_family="test", problem_text="Prob 1", answer="1"),
        Problem(contest_family="test", problem_text="Prob 2", answer="2"),
    ]
    async_session.add_all(problems)
    await async_session.commit()

    stats = await batch_tag_llm(async_session, "fake_key", dry_run=True)

    assert stats["total"] == 2
    assert stats["batches"] == 0
    assert stats["tagged"] == 0

@pytest.mark.asyncio
@patch("src.services.llm_tagger.classify_batch_claude")
async def test_batch_tag_llm_invalid_skill_node(mock_classify, async_session):
    # Add problem
    async_session.add(Problem(id=1, contest_family="test", problem_text="Prob 1", answer="1"))

    # Add valid skill node
    async_session.add(SkillNode(id="VALID_NODE", name="Valid", domain="TEST", level=1))
    await async_session.commit()

    # Return 1 valid and 1 invalid node
    mock_classify.return_value = [
        TagResult(problem_id=1, skill_node_id="VALID_NODE", confidence=0.9),
        TagResult(problem_id=1, skill_node_id="INVALID_NODE", confidence=0.8),
    ]

    stats = await batch_tag_llm(async_session, "fake_key", rate_limit_delay=0)

    assert stats["tags_created"] == 1
    assert stats["invalid_nodes"] == 1

    # Check DB
    tags = (await async_session.execute(select(ProblemSkillTag))).scalars().all()
    assert len(tags) == 1
    assert tags[0].skill_node_id == "VALID_NODE"

@pytest.mark.asyncio
@patch("src.services.llm_tagger.classify_batch_claude")
async def test_batch_tag_llm_on_conflict(mock_classify, async_session):
    # Add problem
    async_session.add(Problem(id=1, contest_family="test", problem_text="Prob 1", answer="1"))
    async_session.add(SkillNode(id="NODE_1", name="Node 1", domain="TEST", level=1))
    await async_session.commit()

    # Add existing tag
    async_session.add(ProblemSkillTag(problem_id=1, skill_node_id="NODE_1", confidence=0.5, tagged_by="manual"))
    await async_session.commit()

    # Return duplicate tag
    mock_classify.return_value = [
        TagResult(problem_id=1, skill_node_id="NODE_1", confidence=0.9),
    ]

    # Should not raise integrity error because of ON CONFLICT DO NOTHING
    # Set skip_tagged to False to process the problem
    stats = await batch_tag_llm(async_session, "fake_key", skip_tagged=False, rate_limit_delay=0)

    # Tag already existed, so the insert was ignored or it overwrote
    tags = (await async_session.execute(select(ProblemSkillTag))).scalars().all()
    assert len(tags) == 1
