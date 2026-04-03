import random

import pytest

from src.engine.adaptive import (
    ProblemCandidate,
    SelectionResult,
    estimate_session_difficulty,
    fisher_information,
    probability_correct,
    select_next_problem,
    select_problem_batch,
)
from src.engine.glicko2 import Rating


def _make_problem(
    id: str = "p1",
    mu: float = 1500.0,
    phi: float = 100.0,
    domain: str = "algebra",
    skills: list[str] | None = None,
    disc: float = 1.0,
    guess: float = 0.0,
    last_seen: int | None = None,
) -> ProblemCandidate:
    return ProblemCandidate(
        id=id,
        difficulty=Rating(mu=mu, phi=phi),
        domain=domain,
        skill_node_ids=skills or ["skill_1"],
        discrimination=disc,
        guessing=guess,
        last_seen_days=last_seen,
    )


# ── probability_correct ─────────────────────────────────────────────────────

def test_prob_equal_ratings_no_guessing():
    student = Rating(mu=1500.0, phi=100.0)
    prob = _make_problem(mu=1500.0, guess=0.0)
    p = probability_correct(student, prob)
    assert p == pytest.approx(0.5, abs=0.05)


def test_prob_approaches_guessing_when_much_weaker():
    student = Rating(mu=800.0, phi=100.0)
    prob = _make_problem(mu=2200.0, guess=0.25)
    p = probability_correct(student, prob)
    assert p == pytest.approx(0.25, abs=0.05)


def test_prob_approaches_one_when_much_stronger():
    student = Rating(mu=2200.0, phi=100.0)
    prob = _make_problem(mu=800.0, guess=0.0)
    p = probability_correct(student, prob)
    assert p > 0.95


def test_higher_discrimination_steeper_curve():
    student = Rating(mu=1600.0, phi=100.0)
    p_low = probability_correct(student, _make_problem(mu=1500.0, disc=0.5))
    p_high = probability_correct(student, _make_problem(mu=1500.0, disc=2.0))
    # Higher discrimination → more separation from 0.5
    assert p_high > p_low


# ── fisher_information ───────────────────────────────────────────────────────

def test_information_maximized_near_half():
    student = Rating(mu=1500.0, phi=100.0)
    # Problem at same level (P ≈ 0.5) should have more info than easy problem
    info_matched = fisher_information(student, _make_problem(mu=1500.0))
    info_easy = fisher_information(student, _make_problem(mu=1000.0))
    assert info_matched > info_easy


# ── select_next_problem ─────────────────────────────────────────────────────

def test_filters_by_domain():
    student = Rating(mu=1500.0, phi=100.0)
    candidates = [
        _make_problem(id="alg1", domain="algebra"),
        _make_problem(id="geo1", domain="geometry"),
    ]
    result = select_next_problem(student, candidates, domain="geometry", rng=random.Random(42))
    assert result is not None
    assert result.problem.domain == "geometry"


def test_excludes_recently_seen():
    student = Rating(mu=1500.0, phi=100.0)
    candidates = [
        _make_problem(id="seen", last_seen=3),
        _make_problem(id="fresh", last_seen=10),
    ]
    result = select_next_problem(student, candidates, recently_seen_ids=set(), rng=random.Random(42))
    assert result is not None
    assert result.problem.id == "fresh"


def test_excludes_by_id_set():
    student = Rating(mu=1500.0, phi=100.0)
    candidates = [
        _make_problem(id="seen"),
        _make_problem(id="unseen"),
    ]
    result = select_next_problem(student, candidates, recently_seen_ids={"seen"}, rng=random.Random(42))
    assert result is not None
    assert result.problem.id == "unseen"


def test_high_rd_gets_uncertainty_reduction():
    student = Rating(mu=1500.0, phi=300.0)
    candidates = [
        _make_problem(id="close", mu=1510.0),
        _make_problem(id="far", mu=2000.0),
    ]
    result = select_next_problem(student, candidates, rng=random.Random(42))
    assert result is not None
    assert result.selection_reason == "uncertainty_reduction"
    assert result.problem.id == "close"


def test_low_rd_gets_zpd():
    student = Rating(mu=1500.0, phi=100.0)
    # Create problems spanning a range, some in ZPD
    candidates = [
        _make_problem(id="easy", mu=1000.0),
        _make_problem(id="zpd", mu=1550.0),   # slight stretch, ~60-75% correct
        _make_problem(id="hard", mu=2200.0),
    ]
    result = select_next_problem(student, candidates, rng=random.Random(42))
    assert result is not None
    assert result.selection_reason == "zpd"


def test_review_items_appear():
    """Over many selections with seeded RNG, review should appear ~20% of the time."""
    student = Rating(mu=1500.0, phi=100.0)
    candidates = [
        _make_problem(id="learn", skills=["unmastered"]),
        _make_problem(id="review", skills=["mastered_skill"]),
    ]
    mastered = {"mastered_skill"}

    review_count = 0
    n = 200
    for i in range(n):
        result = select_next_problem(
            student, candidates, mastered_skill_ids=mastered, rng=random.Random(i),
        )
        if result and result.selection_reason == "review":
            review_count += 1

    ratio = review_count / n
    assert 0.10 < ratio < 0.35  # ~20% with statistical wiggle room


def test_returns_none_for_empty_candidates():
    student = Rating(mu=1500.0, phi=100.0)
    result = select_next_problem(student, [], rng=random.Random(42))
    assert result is None


# ── select_problem_batch ─────────────────────────────────────────────────────

def test_batch_no_duplicates():
    student = Rating(mu=1500.0, phi=100.0)
    candidates = [_make_problem(id=f"p{i}", mu=1400 + i * 30) for i in range(20)]
    results = select_problem_batch(student, candidates, batch_size=10, rng=random.Random(42))
    ids = [r.problem.id for r in results]
    assert len(ids) == len(set(ids))


def test_batch_returns_fewer_if_pool_small():
    student = Rating(mu=1500.0, phi=100.0)
    candidates = [_make_problem(id="only1")]
    results = select_problem_batch(student, candidates, batch_size=5, rng=random.Random(42))
    assert len(results) == 1


# ── estimate_session_difficulty ──────────────────────────────────────────────

def test_difficulty_too_easy():
    prob = _make_problem()
    results = [(prob, True)] * 9 + [(prob, False)]  # 90% correct
    assert estimate_session_difficulty(Rating(), results) == "too_easy"


def test_difficulty_too_hard():
    prob = _make_problem()
    results = [(prob, True)] * 3 + [(prob, False)] * 7  # 30% correct
    assert estimate_session_difficulty(Rating(), results) == "too_hard"


def test_difficulty_appropriate():
    prob = _make_problem()
    results = [(prob, True)] * 7 + [(prob, False)] * 3  # 70% correct
    assert estimate_session_difficulty(Rating(), results) == "appropriate"


def test_problem_uncertainty_reduces_discrimination():
    """High difficulty RD reduces effective impact via g(phi)."""
    student = Rating(mu=1600.0, phi=100.0)
    certain = _make_problem(mu=1500.0, phi=50.0)
    uncertain = _make_problem(mu=1500.0, phi=300.0)
    # Certain problem → g close to 1 → steeper curve → more information
    assert fisher_information(student, certain) > fisher_information(student, uncertain)
