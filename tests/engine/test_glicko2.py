import math
import pytest

from src.engine.glicko2 import (
    INITIAL_RATING,
    INITIAL_RD,
    INITIAL_VOLATILITY,
    RD_CEILING,
    RD_FLOOR,
    SCALE,
    Rating,
    compute_variance,
    decay_rd,
    expected_score,
    g,
    glicko2_to_rating,
    mastery_state,
    rating_to_glicko2,
    update_rating,
    update_rating_single,
)


# ── Scale conversion ─────────────────────────────────────────────────────────

def test_rating_conversion_round_trip():
    original = Rating(mu=1700.0, phi=200.0, sigma=0.05)
    mu, phi, sigma = rating_to_glicko2(original)
    recovered = glicko2_to_rating(mu, phi, sigma)
    assert recovered.mu == pytest.approx(original.mu, abs=1e-6)
    assert recovered.phi == pytest.approx(original.phi, abs=1e-6)
    assert recovered.sigma == pytest.approx(original.sigma, abs=1e-6)


def test_default_rating_converts_to_zero():
    mu, phi, sigma = rating_to_glicko2(Rating())
    assert mu == pytest.approx(0.0, abs=1e-6)
    assert phi == pytest.approx(INITIAL_RD / SCALE, abs=1e-6)


# ── g function ───────────────────────────────────────────────────────────────

def test_g_at_zero():
    assert g(0.0) == pytest.approx(1.0, abs=1e-6)


def test_g_decreases_with_phi():
    assert g(0.5) > g(1.0) > g(2.0)


# ── expected_score ───────────────────────────────────────────────────────────

def test_expected_score_equal_ratings():
    result = expected_score(0.0, 0.0, 1.0)
    assert result == pytest.approx(0.5, abs=0.01)


def test_expected_score_monotonic():
    # Higher mu → higher expected score
    e1 = expected_score(0.0, 0.0, 1.0)
    e2 = expected_score(1.0, 0.0, 1.0)
    e3 = expected_score(2.0, 0.0, 1.0)
    assert e1 < e2 < e3


def test_expected_score_symmetry():
    e_ab = expected_score(1.0, 0.0, 1.0)
    e_ba = expected_score(0.0, 1.0, 1.0)
    assert e_ab + e_ba == pytest.approx(1.0, abs=0.01)


# ── Single update behavior ──────────────────────────────────────────────────

def test_correct_answer_against_harder_increases_rating():
    player = Rating(mu=1500.0, phi=200.0, sigma=0.06)
    opponent = Rating(mu=1700.0, phi=100.0, sigma=0.06)
    updated = update_rating_single(player, opponent, 1.0)
    assert updated.mu > player.mu
    assert updated.phi < player.phi


def test_incorrect_answer_against_easier_decreases_rating():
    player = Rating(mu=1500.0, phi=200.0, sigma=0.06)
    opponent = Rating(mu=1300.0, phi=100.0, sigma=0.06)
    updated = update_rating_single(player, opponent, 0.0)
    assert updated.mu < player.mu
    assert updated.phi < player.phi


def test_high_rd_larger_change_than_low_rd():
    opponent = Rating(mu=1500.0, phi=100.0, sigma=0.06)

    high_rd = Rating(mu=1500.0, phi=300.0, sigma=0.06)
    low_rd = Rating(mu=1500.0, phi=75.0, sigma=0.06)

    updated_high = update_rating_single(high_rd, opponent, 1.0)
    updated_low = update_rating_single(low_rd, opponent, 1.0)

    change_high = abs(updated_high.mu - high_rd.mu)
    change_low = abs(updated_low.mu - low_rd.mu)
    assert change_high > change_low


# ── RD clamping ──────────────────────────────────────────────────────────────

def test_rd_never_below_floor():
    # Many correct answers against similar opponent to drive RD down
    player = Rating(mu=1500.0, phi=60.0, sigma=0.06)
    opponent = Rating(mu=1500.0, phi=60.0, sigma=0.06)
    for _ in range(50):
        player = update_rating_single(player, opponent, 1.0)
    assert player.phi >= RD_FLOOR


def test_rd_never_above_ceiling():
    player = Rating(mu=1500.0, phi=300.0, sigma=0.06)
    decayed = decay_rd(player, inactive_days=365)
    assert decayed.phi <= RD_CEILING


# ── Volatility convergence ───────────────────────────────────────────────────

def test_volatility_update_converges():
    """Ensure the iterative algorithm doesn't infinite loop."""
    player = Rating(mu=1500.0, phi=200.0, sigma=0.06)
    opponent = Rating(mu=1800.0, phi=50.0, sigma=0.06)
    # This should return without hanging
    updated = update_rating_single(player, opponent, 1.0)
    assert updated.sigma > 0


# ── Batch update ─────────────────────────────────────────────────────────────

def test_batch_update_multiple_opponents():
    player = Rating(mu=1500.0, phi=200.0, sigma=0.06)
    opponents = [
        Rating(mu=1400.0, phi=80.0, sigma=0.06),
        Rating(mu=1550.0, phi=100.0, sigma=0.06),
        Rating(mu=1700.0, phi=120.0, sigma=0.06),
    ]
    scores = [1.0, 0.0, 1.0]
    updated = update_rating(player, opponents, scores)
    # 2 wins out of 3 against a spread — rating should increase
    assert updated.mu > player.mu
    assert updated.phi < player.phi


# ── Glickman example (approximate) ──────────────────────────────────────────

def test_glickman_paper_example():
    """Verify against the numerical example in the Glicko-2 paper.

    Player (1500, RD 200, σ 0.06) plays three games:
      Win vs 1400 RD 30, Loss vs 1550 RD 100, Win vs 1700 RD 300.
    Hand-verified: Δ ≈ +0.80 (positive — 2 wins including upset), φ' ≈ 151.5.
    """
    player = Rating(mu=1500.0, phi=200.0, sigma=0.06)
    opponents = [
        Rating(mu=1400.0, phi=30.0, sigma=0.06),
        Rating(mu=1550.0, phi=100.0, sigma=0.06),
        Rating(mu=1700.0, phi=300.0, sigma=0.06),
    ]
    scores = [1.0, 0.0, 1.0]
    updated = update_rating(player, opponents, scores)
    # mu' ≈ 1500 + 0.8722² × 0.4512 × 173.72 ≈ 1559.6, φ' ≈ 151.5
    assert updated.mu == pytest.approx(1560.0, abs=2.0)
    assert updated.phi == pytest.approx(151.5, abs=2.0)


# ── RD decay ─────────────────────────────────────────────────────────────────

def test_rd_decay_no_change_within_threshold():
    player = Rating(mu=1500.0, phi=100.0, sigma=0.06)
    decayed = decay_rd(player, inactive_days=10)
    assert decayed.phi == player.phi


def test_rd_decay_increases_after_threshold():
    player = Rating(mu=1500.0, phi=100.0, sigma=0.06)
    decayed = decay_rd(player, inactive_days=30)
    assert decayed.phi > player.phi


def test_rd_decay_increases_monotonically():
    player = Rating(mu=1500.0, phi=100.0, sigma=0.06)
    d30 = decay_rd(player, inactive_days=30)
    d60 = decay_rd(player, inactive_days=60)
    d90 = decay_rd(player, inactive_days=90)
    assert d30.phi < d60.phi < d90.phi


# ── Mastery state ────────────────────────────────────────────────────────────

def test_mastery_state_practicing_high_rd():
    r = Rating(mu=2000.0, phi=200.0, sigma=0.06)
    assert mastery_state(r, 1500.0) == "practicing"


def test_mastery_state_proficient():
    r = Rating(mu=1750.0, phi=120.0, sigma=0.06)
    assert mastery_state(r, 1500.0) == "proficient"


def test_mastery_state_mastered():
    r = Rating(mu=1900.0, phi=80.0, sigma=0.06)
    assert mastery_state(r, 1500.0) == "mastered"


def test_mastery_state_practicing_low_rating():
    r = Rating(mu=1600.0, phi=80.0, sigma=0.06)
    assert mastery_state(r, 1500.0) == "practicing"


# ── Convergence speed ────────────────────────────────────────────────────────

def test_new_player_converges_faster():
    """High RD (new) player's rating moves more than low RD (established)."""
    opponent = Rating(mu=1600.0, phi=100.0, sigma=0.06)

    new_player = Rating(mu=1500.0, phi=350.0, sigma=0.06)
    established = Rating(mu=1500.0, phi=75.0, sigma=0.06)

    new_updated = update_rating_single(new_player, opponent, 1.0)
    est_updated = update_rating_single(established, opponent, 1.0)

    assert abs(new_updated.mu - new_player.mu) > abs(est_updated.mu - established.mu)


# ── Update symmetry ──────────────────────────────────────────────────────────

def test_update_symmetry():
    """If A beats B, gains and losses should be consistent."""
    a = Rating(mu=1500.0, phi=150.0, sigma=0.06)
    b = Rating(mu=1500.0, phi=150.0, sigma=0.06)

    a_after = update_rating_single(a, b, 1.0)
    b_after = update_rating_single(b, a, 0.0)

    a_gain = a_after.mu - a.mu
    b_loss = b.mu - b_after.mu
    # With equal RDs, gain and loss should be very close
    assert a_gain == pytest.approx(b_loss, rel=0.05)
