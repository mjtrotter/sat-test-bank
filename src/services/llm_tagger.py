"""
LLM-assisted problem→skill node tagger (Phase 2).

Uses Claude API to classify math problems into specific atomic skill nodes.
Designed for batch processing — groups problems and classifies in bulk
to minimize API calls. No local GPU required.

Usage:
    python -m src.cli tag-problems-llm --source mathcounts --limit 100
"""

import asyncio
import json
import re
import time
from dataclasses import dataclass

from sqlalchemy import select, distinct
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.tables import Problem, ProblemSkillTag, SkillNode


# ── Taxonomy context builder ────────────────────────────────────────────────

async def build_taxonomy_context(session: AsyncSession) -> str:
    """Build a compact taxonomy reference for the LLM prompt.

    Groups nodes by domain and level for efficient context.
    """
    nodes = (await session.execute(
        select(SkillNode.id, SkillNode.name, SkillNode.domain, SkillNode.level)
        .order_by(SkillNode.domain, SkillNode.level, SkillNode.id)
    )).all()

    lines = ["# Skill Node Taxonomy", ""]
    current_domain = None
    current_level = None

    for nid, name, domain, level in nodes:
        if domain != current_domain:
            current_domain = domain
            current_level = None
            lines.append(f"\n## {domain}")
        if level != current_level:
            current_level = level
            lines.append(f"### Level {level}")
        lines.append(f"- {nid}: {name}")

    return "\n".join(lines)


# ── Classification prompt ────────────────────────────────────────────────────

CLASSIFY_SYSTEM = """You are a math education expert classifying competition math problems into a skill taxonomy.

For each problem, identify the 1-3 most relevant skill nodes from the taxonomy. Consider:
- What mathematical concept is PRIMARILY tested?
- What prerequisite skills are needed?
- What difficulty level matches the problem?

Respond with valid JSON only. No explanation."""

CLASSIFY_USER = """Given this skill taxonomy:

{taxonomy}

---

Classify these problems. For each, return the top 1-3 skill node IDs with confidence (0.0-1.0).

{problems_block}

Respond with JSON array:
[
  {{"problem_id": 123, "tags": [{{"skill_node_id": "COUNT_L2_COMB_NCR", "confidence": 0.9}}, ...]}},
  ...
]"""


def format_problems_block(problems: list[dict]) -> str:
    """Format a batch of problems for the classification prompt."""
    lines = []
    for p in problems:
        text = p["problem_text"][:500]  # truncate long problems
        lines.append(f"Problem {p['id']}:\n{text}\n")
    return "\n".join(lines)


# ── API caller ───────────────────────────────────────────────────────────────

@dataclass
class TagResult:
    problem_id: int
    skill_node_id: str
    confidence: float


async def classify_batch_claude(
    problems: list[dict],
    taxonomy_context: str,
    api_key: str,
    model: str = "claude-sonnet-4-20250514",
    max_retries: int = 2,
) -> list[TagResult]:
    """Classify a batch of problems using Claude API.

    Args:
        problems: List of dicts with 'id' and 'problem_text'.
        taxonomy_context: Pre-built taxonomy string.
        api_key: Anthropic API key.
        model: Claude model to use.

    Returns:
        List of TagResult with skill node assignments.
    """
    import anthropic

    client = anthropic.AsyncAnthropic(api_key=api_key)

    user_prompt = CLASSIFY_USER.format(
        taxonomy=taxonomy_context,
        problems_block=format_problems_block(problems),
    )

    for attempt in range(max_retries + 1):
        try:
            response = await client.messages.create(
                model=model,
                max_tokens=4096,
                system=CLASSIFY_SYSTEM,
                messages=[{"role": "user", "content": user_prompt}],
            )

            # Parse JSON from response
            text = response.content[0].text
            # Extract JSON array — handle markdown code blocks
            json_match = re.search(r"\[.*\]", text, re.DOTALL)
            if not json_match:
                if attempt < max_retries:
                    continue
                return []

            data = json.loads(json_match.group())
            results = []
            for item in data:
                pid = item.get("problem_id")
                for tag in item.get("tags", []):
                    results.append(TagResult(
                        problem_id=pid,
                        skill_node_id=tag["skill_node_id"],
                        confidence=min(1.0, max(0.0, float(tag["confidence"]))),
                    ))
            return results

        except json.JSONDecodeError:
            if attempt < max_retries:
                continue
            return []
        except Exception as e:
            if attempt < max_retries:
                await asyncio.sleep(2 ** attempt)
                continue
            print(f"  Error classifying batch: {e}")
            return []


# ── Batch orchestrator ───────────────────────────────────────────────────────

async def batch_tag_llm(
    session: AsyncSession,
    api_key: str,
    source_filter: list[str] | None = None,
    limit: int | None = None,
    batch_size: int = 20,
    skip_tagged: bool = True,
    model: str = "claude-sonnet-4-20250514",
    dry_run: bool = False,
    rate_limit_delay: float = 1.0,
) -> dict:
    """Tag problems using LLM classification.

    Args:
        session: DB session.
        api_key: Anthropic API key.
        source_filter: Restrict to these contest families.
        limit: Max problems to process.
        batch_size: Problems per API call (20 is a good balance).
        skip_tagged: Skip problems already tagged by LLM.
        model: Claude model to use.
        dry_run: Print plan without making API calls.
        rate_limit_delay: Seconds between API batches (default 1.0).

    Returns:
        Stats dict.
    """
    # Build taxonomy context once
    taxonomy_context = await build_taxonomy_context(session)

    # Load valid skill node IDs for validation
    valid_ids = set((await session.execute(select(SkillNode.id))).scalars().all())

    # Build problem query
    query = select(Problem.id, Problem.problem_text).where(
        Problem.answer.isnot(None),
        Problem.problem_text.isnot(None),
    )

    if source_filter:
        query = query.where(Problem.contest_family.in_(source_filter))

    if skip_tagged:
        # Skip problems already tagged by LLM
        llm_tagged = (
            select(distinct(ProblemSkillTag.problem_id))
            .where(ProblemSkillTag.tagged_by == "llm")
        )
        query = query.where(Problem.id.notin_(llm_tagged))

    query = query.order_by(Problem.id)
    if limit:
        query = query.limit(limit)

    rows = (await session.execute(query)).all()
    problems = [{"id": r[0], "problem_text": r[1]} for r in rows]

    stats = {
        "total": len(problems),
        "batches": 0,
        "tagged": 0,
        "tags_created": 0,
        "invalid_nodes": 0,
    }

    if dry_run:
        print(f"  Would process {len(problems)} problems in {(len(problems) + batch_size - 1) // batch_size} batches")
        print(f"  Taxonomy context: {len(taxonomy_context)} chars")
        print(f"  Model: {model}")
        return stats

    total_batches = (len(problems) + batch_size - 1) // batch_size
    start_time = time.time()

    # Process in batches
    for i in range(0, len(problems), batch_size):
        batch = problems[i : i + batch_size]
        stats["batches"] += 1

        results = await classify_batch_claude(
            batch, taxonomy_context, api_key, model=model,
        )

        # Use ON CONFLICT DO NOTHING to handle re-runs gracefully
        from sqlalchemy.dialects.postgresql import insert as pg_insert

        for r in results:
            if r.skill_node_id not in valid_ids:
                print(f"  Invalid skill node ID from LLM: {r.skill_node_id}")
                stats["invalid_nodes"] += 1
                continue

            stmt = pg_insert(ProblemSkillTag).values(
                problem_id=r.problem_id,
                skill_node_id=r.skill_node_id,
                confidence=r.confidence,
                tagged_by="llm",
            ).on_conflict_do_nothing()
            await session.execute(stmt)
            stats["tags_created"] += 1

        stats["tagged"] += len(set(r.problem_id for r in results))

        # Progress logging with ETA
        elapsed = time.time() - start_time
        avg_per_batch = elapsed / stats["batches"]
        eta_seconds = (total_batches - stats["batches"]) * avg_per_batch
        eta_str = time.strftime("%H:%M:%S", time.gmtime(eta_seconds))

        print(
            f"  [{i + len(batch)}/{len(problems)}] "
            f"batches={stats['batches']}/{total_batches}, "
            f"tagged={stats['tagged']}, "
            f"tags={stats['tags_created']}, "
            f"ETA={eta_str}"
        )

        if stats["batches"] % 5 == 0:
            await session.commit()

        # Rate limiting between batches
        if stats["batches"] < total_batches:
            await asyncio.sleep(rate_limit_delay)

    await session.commit()
    return stats
