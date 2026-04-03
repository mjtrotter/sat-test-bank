"""
Deterministic problem→skill node tagger (Phase 1).

Classifies problems into skill nodes using:
  1. Keyword-based domain detection from problem text
  2. Contest metadata → difficulty level estimation
  3. (domain, level) → candidate skill nodes with confidence scoring

No LLM inference required — pure heuristic matching.
"""

import re
from dataclasses import dataclass

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.tables import Problem, ProblemSkillTag, SkillNode


# ── Domain Classification ────────────────────────────────────────────────────

# Keywords ordered roughly by specificity (more specific first)
DOMAIN_KEYWORDS: dict[str, list[re.Pattern]] = {
    "GEO": [
        re.compile(r"\b(triangle|triangles|equilateral|isosceles|scalene)\b", re.I),
        re.compile(r"\b(circle|circles|radius|radii|diameter|circumference|semicircle)\b", re.I),
        re.compile(r"\b(rectangle|square|parallelogram|trapezoid|rhombus|quadrilateral)\b", re.I),
        re.compile(r"\b(polygon|pentagon|hexagon|octagon|decagon)\b", re.I),
        re.compile(r"\b(angle|angles|degrees?|perpendicular|bisect)\b", re.I),
        re.compile(r"\b(area|perimeter|surface area|volume)\b", re.I),
        re.compile(r"\b(congruent|similar|reflection|rotation|translation)\b", re.I),
        re.compile(r"\b(pythagorean|hypotenuse|leg|altitude|median)\b", re.I),
        re.compile(r"\b(tangent|chord|arc|sector|inscribed|circumscribed)\b", re.I),
        re.compile(r"\b(coordinate|slope|midpoint|distance formula)\b", re.I),
        re.compile(r"\b(cube|sphere|cylinder|cone|prism|pyramid)\b", re.I),
        re.compile(r"\b(diagonal|vertex|vertices)\b", re.I),
    ],
    "COUNT": [
        re.compile(r"\b(probability|probabilities|likely|likelihood)\b", re.I),
        re.compile(r"\b(how many ways|in how many|number of ways)\b", re.I),
        re.compile(r"\b(how many distinct|how many different|how many ordered)\b", re.I),
        re.compile(r"\b(combination|combinations|choose|selection)\b", re.I),
        re.compile(r"\b(permutation|permutations|arrange|arrangement)\b", re.I),
        re.compile(r"\b(dice|die|coin|coins|flip|toss|cards?|deck)\b", re.I),
        re.compile(r"\b(factorial|pascal|binomial)\b", re.I),
        re.compile(r"\b(Venn diagram|inclusion.exclusion)\b", re.I),
        re.compile(r"\b(expected value|random|randomly)\b", re.I),
        re.compile(r"\b(outcomes?|sample space|favorable)\b", re.I),
        re.compile(r"\b(paths?.*grid|lattice path)\b", re.I),
        re.compile(r"\b(how many (?:lines|triangles|segments|pairs|subsets|ways))\b", re.I),
        re.compile(r"\b(ordered (?:triples?|pairs?|tuples?))\b", re.I),
    ],
    "NT": [
        re.compile(r"\b(prime|primes|composite)\b", re.I),
        re.compile(r"\b(factor|factors|divisor|divisors|divisible)\b", re.I),
        re.compile(r"\b(GCD|LCM|greatest common|least common)\b", re.I),
        re.compile(r"\b(modular|modulo|mod\s+\d|remainder)\b", re.I),
        re.compile(r"\b(digit sum|digits? of|units? digit|tens? digit)\b", re.I),
        re.compile(r"\b(even|odd)\s+(number|integer)\b", re.I),
        re.compile(r"\b(perfect square|perfect cube)\b", re.I),
        re.compile(r"\b(Euler|totient|Fermat.*theorem)\b", re.I),
        re.compile(r"\b(base\s+\d|binary|ternary)\b", re.I),
        re.compile(r"\b(consecutive\s+integers?)\b", re.I),
        re.compile(r"\b(positive integers?.*product|product.*positive integers?)\b", re.I),
        re.compile(r"\b(distinct positive integers?)\b", re.I),
        re.compile(r"\b(sum of.*squares|squares?.*sum)\b", re.I),
    ],
    "ALG": [
        re.compile(r"\b(equation|equations|solve for|solving)\b", re.I),
        re.compile(r"\b(polynomial|quadratic|cubic|quartic)\b", re.I),
        re.compile(r"\b(function|functions|f\(x\)|domain|range)\b", re.I),
        re.compile(r"\b(variable|variables|expression|simplify)\b", re.I),
        re.compile(r"\b(inequality|inequalities)\b", re.I),
        re.compile(r"\b(sequence|series|arithmetic progression|geometric progression)\b", re.I),
        re.compile(r"\b(logarithm|log|exponent|exponential)\b", re.I),
        re.compile(r"\b(system of|simultaneous)\b", re.I),
        re.compile(r"\b(factor.*expression|expand|foil)\b", re.I),
        re.compile(r"\b(root|roots|zero|zeros)\b", re.I),
        re.compile(r"\b(value of|find.*value)\b", re.I),
        re.compile(r"\b(what is.*\$|if.*=.*what)\b", re.I),
        re.compile(r"\b(sum of.*first \d+|first \d+.*positive)\b", re.I),
    ],
    "ARITH": [
        re.compile(r"\b(fraction|fractions|numerator|denominator)\b", re.I),
        re.compile(r"\b(decimal|decimals|percent|percentage)\b", re.I),
        re.compile(r"\b(ratio|ratios|proportion|proportional)\b", re.I),
        re.compile(r"\b(average|mean|median|mode)\b", re.I),
        re.compile(r"\b(unit conversion|convert.*to)\b", re.I),
        re.compile(r"\b(rate|speed|distance|time)\b", re.I),
        re.compile(r"\b(profit|loss|discount|tax|interest|cost|price)\b", re.I),
        re.compile(r"\b(inches|feet|meters|pounds|gallons|miles)\b", re.I),
        re.compile(r"\b(grows|grows.*per|per year|per hour|per day)\b", re.I),
        re.compile(r"\b(total|altogether|combined|each|every)\b", re.I),
    ],
    "LOGIC": [
        re.compile(r"\b(if and only if|necessary and sufficient)\b", re.I),
        re.compile(r"\b(truth table|logical|contrapositive)\b", re.I),
        re.compile(r"\b(pigeonhole|invariant|parity argument)\b", re.I),
        re.compile(r"\b(strategy|game theory|optimal play)\b", re.I),
    ],
}


@dataclass
class DomainScore:
    domain: str
    score: float  # 0.0–1.0, based on keyword match density


def classify_domain(text: str) -> list[DomainScore]:
    """Classify problem text into math domains by keyword density.

    Returns domains sorted by score descending. Multiple domains can score
    if a problem spans topics (e.g., geometric probability).
    """
    results = []
    for domain, patterns in DOMAIN_KEYWORDS.items():
        matches = sum(1 for p in patterns if p.search(text))
        if matches > 0:
            # Normalize by pattern count for that domain
            score = min(matches / max(len(patterns) * 0.3, 1), 1.0)
            results.append(DomainScore(domain=domain, score=round(score, 3)))

    results.sort(key=lambda d: d.score, reverse=True)
    return results


# ── Difficulty Level Estimation ──────────────────────────────────────────────

# Maps (contest_family, contest_level, problem_number_range) → estimated level
LEVEL_RULES: list[tuple[dict, int]] = [
    # GSM8K → L1 arithmetic
    ({"contest_family": "gsm8k"}, 1),
    # MATHCOUNTS chapter
    ({"contest_family": "mathcounts", "contest_level": "chapter"}, 1),
    # MATHCOUNTS state
    ({"contest_family": "mathcounts", "contest_level": "state"}, 2),
    # MATHCOUNTS national
    ({"contest_family": "mathcounts", "contest_level": "national"}, 3),
    # AMC 8
    ({"contest_family": "amc8"}, 1),
    # AMC 10 — problem number determines difficulty
    ({"contest_family": "amc10"}, 2),
    # AMC 12
    ({"contest_family": "amc12"}, 3),
    # AIME
    ({"contest_family": "amc_aime"}, 4),
    # Orca math → L1 word problems
    ({"contest_family": "orca_math"}, 1),
    # SAT → L1-L2
    ({"contest_family": "sat"}, 1),
    # Generic math competition
    ({"contest_family": "math_competition"}, 2),
]

# Problem number → level bump for AMC contests
AMC_NUMBER_BUMPS = {
    "amc8": [(1, 15, 0), (16, 20, 1), (21, 25, 1)],
    "amc10": [(1, 10, 0), (11, 20, 1), (21, 25, 2)],
    "amc12": [(1, 10, 0), (11, 20, 1), (21, 25, 2)],
    "amc_aime": [(1, 5, 0), (6, 10, 1), (11, 15, 1)],
}


def estimate_level(
    contest_family: str | None,
    contest_level: str | None,
    problem_number: int | None,
) -> int:
    """Estimate difficulty level (1-5) from contest metadata."""
    base_level = 2  # default

    for rule_match, level in LEVEL_RULES:
        match = True
        for k, v in rule_match.items():
            if k == "contest_family" and contest_family != v:
                match = False
            elif k == "contest_level" and contest_level != v:
                match = False
        if match:
            base_level = level
            break

    # Apply problem number bump for AMC-style contests
    if contest_family in AMC_NUMBER_BUMPS and problem_number:
        for lo, hi, bump in AMC_NUMBER_BUMPS[contest_family]:
            if lo <= problem_number <= hi:
                base_level += bump
                break

    return max(1, min(base_level, 5))


# ── Skill Node Matching ─────────────────────────────────────────────────────

@dataclass
class TagCandidate:
    skill_node_id: str
    confidence: float
    reason: str


async def match_skill_nodes(
    session: AsyncSession,
    domain: str,
    level: int,
    domain_confidence: float,
) -> list[TagCandidate]:
    """Find matching skill nodes for a (domain, level) pair.

    Assigns all nodes at the matching level in the domain. If no exact level
    match, tries adjacent levels. Confidence reflects domain classifier
    certainty and level precision.
    """
    # Try exact level, then +/-1
    for level_offset in [0, -1, 1]:
        target_level = max(1, min(level + level_offset, 5))
        nodes = (await session.execute(
            select(SkillNode.id).where(
                SkillNode.domain == domain,
                SkillNode.level == target_level,
            )
        )).scalars().all()

        if nodes:
            # Base confidence from domain classifier, reduced for level mismatch
            level_penalty = 0.15 * abs(level_offset)
            conf = round(max(0.1, domain_confidence * 0.6 - level_penalty), 3)
            reason = f"keyword:{domain}/L{target_level}"
            if level_offset != 0:
                reason += f"(shifted from L{level})"
            return [TagCandidate(nid, conf, reason) for nid in nodes]

    return []


# ── Batch Tagger ─────────────────────────────────────────────────────────────

async def tag_problem(
    session: AsyncSession,
    problem: Problem,
) -> list[TagCandidate]:
    """Tag a single problem with skill nodes. Returns candidates."""
    domains = classify_domain(problem.problem_text or "")
    if not domains:
        return []

    level = estimate_level(
        problem.contest_family,
        problem.contest_level,
        problem.problem_number,
    )

    # Tag with top 2 domains (many problems span multiple)
    all_candidates = []
    for ds in domains[:2]:
        candidates = await match_skill_nodes(session, ds.domain, level, ds.score)
        all_candidates.extend(candidates)

    return all_candidates


async def batch_tag(
    session: AsyncSession,
    source_filter: list[str] | None = None,
    limit: int | None = None,
    skip_tagged: bool = True,
    dry_run: bool = False,
) -> dict:
    """Tag problems in batch. Returns stats dict."""
    query = select(Problem).where(
        Problem.answer.isnot(None),
        Problem.problem_text.isnot(None),
    )

    if source_filter:
        query = query.where(Problem.contest_family.in_(source_filter))

    if skip_tagged:
        # Only tag problems that don't have any tags yet
        already_tagged = select(ProblemSkillTag.problem_id).distinct()
        query = query.where(Problem.id.notin_(already_tagged))

    query = query.order_by(Problem.id)
    if limit:
        query = query.limit(limit)

    problems = (await session.execute(query)).scalars().all()

    stats = {"total": len(problems), "tagged": 0, "skipped": 0, "tags_created": 0}

    for i, problem in enumerate(problems):
        candidates = await tag_problem(session, problem)

        if not candidates:
            stats["skipped"] += 1
            continue

        if not dry_run:
            # Pick top candidates (limit to avoid flooding — max 5 per problem)
            top = sorted(candidates, key=lambda c: c.confidence, reverse=True)[:5]
            for c in top:
                tag = ProblemSkillTag(
                    problem_id=problem.id,
                    skill_node_id=c.skill_node_id,
                    confidence=c.confidence,
                    tagged_by="auto",
                )
                session.add(tag)
                stats["tags_created"] += 1

        stats["tagged"] += 1

        if (i + 1) % 1000 == 0:
            if not dry_run:
                await session.flush()
            print(f"  [{i+1}/{len(problems)}] tagged={stats['tagged']}, tags={stats['tags_created']}")

    if not dry_run:
        await session.commit()

    return stats
