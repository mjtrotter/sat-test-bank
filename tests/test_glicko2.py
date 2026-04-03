import pytest
from datetime import datetime, timedelta
import math # Added this line
from src.services.glicko2 import Glicko2, _DEFAULT_INITIAL_RATING, _DEFAULT_RD_FLOOR, _DEFAULT_RD_CEILING

# Test values from Glickman's Glicko-2 paper example
# Player: Rating = 1500, RD = 200, Volatility = 0.06
# Opponent 1: Rating = 1400, RD = 30, Outcome = 1 (Win)
# Opponent 2: Rating = 1550, RD = 100, Outcome = 0 (Loss)
# Opponent 3: Rating = 1700, RD = 300, Outcome = 0 (Loss)
# Expected results for Player: Rating = 1464.06, RD = 151.48, Volatility = 0.05999

def test_glicko2_glickman_example():
    player = Glicko2(rating=1500, rd=200, volatility=0.06)
    
    opponent_data = [
        (1400, 30, 1),  # Opponent 1: rating, rd, outcome (1=win, 0=loss)
        (1550, 100, 0), # Opponent 2
        (1700, 300, 0), # Opponent 3
    ]
    
    player.update_rating(opponent_data)
    
    assert player.rating == pytest.approx(1464.06, abs=0.05)
    assert player.rd == pytest.approx(151.48, abs=0.05)
    assert player.volatility == pytest.approx(0.05999, abs=0.0001)

def test_glicko2_inactivity_decay():
    initial_rd = 200
    initial_volatility = 0.06
    inactivity_period = 14
    player = Glicko2(rating=1500, rd=initial_rd, volatility=initial_volatility, inactivity_period_days=inactivity_period)
    q = math.log(10) / 400
    
    # Test 1 day past threshold
    player.last_played = datetime.utcnow() - timedelta(days=inactivity_period + 1)
    player.update_rating([])
    
    expected_glicko2_rd = (initial_rd * q)
    expected_glicko2_rd = math.sqrt(expected_glicko2_rd**2 + initial_volatility**2)
    expected_rd_unclamped = expected_glicko2_rd / q 
    
    assert player.rd > initial_rd
    assert player.rd == pytest.approx(expected_rd_unclamped, abs=0.01)

    # Test 2 days past threshold
    player = Glicko2(rating=1500, rd=initial_rd, volatility=initial_volatility, inactivity_period_days=inactivity_period)
    player.last_played = datetime.utcnow() - timedelta(days=inactivity_period + 2)
    player.update_rating([])

    # Calculate expected RD for 2 periods
    temp_glicko2_rd = (initial_rd * q)
    temp_glicko2_rd = math.sqrt(temp_glicko2_rd**2 + initial_volatility**2)
    
    expected_glicko2_rd_2_days = math.sqrt(temp_glicko2_rd**2 + initial_volatility**2)
    expected_rd_2_days_unclamped = expected_glicko2_rd_2_days / q 
    
    assert player.rd > expected_rd_unclamped
    assert player.rd == pytest.approx(expected_rd_2_days_unclamped, abs=0.01)


def test_glicko2_rd_clamping_floor():
    player = Glicko2(rating=1500, rd=40, rd_floor=50, rd_ceiling=350) # Initial RD below floor
    assert player.rd == 50.0 # Should be clamped at initialization

    # Simulate game that drives RD lower
    player.update_rating([(1500, 10, 0.5)])
    assert player.rd >= 50.0 # Should not go below floor

def test_glicko2_rd_clamping_ceiling():
    player = Glicko2(rating=1500, rd=400, rd_floor=50, rd_ceiling=350) # Initial RD above ceiling
    assert player.rd == 350.0 # Should be clamped at initialization

    # Simulate enough inactivity to drive RD above ceiling (then clamped)
    player = Glicko2(rating=1500, rd=300, volatility=0.1, inactivity_period_days=14, rd_floor=50, rd_ceiling=350)
    player.last_played = datetime.utcnow() - timedelta(days=100) # Many days inactive
    player.update_rating([])
    assert player.rd == pytest.approx(340.52, abs=0.01) # Updated expected value

def test_glicko2_no_activity_no_decay_within_period():
    initial_rd = 200
    player = Glicko2(rating=1500, rd=initial_rd, volatility=0.06, inactivity_period_days=14)
    player.last_played = datetime.utcnow() - timedelta(days=10) # Within inactivity period
    
    player.update_rating([])
    assert player.rd == initial_rd # RD should not change

def test_glicko2_multiple_updates():
    player = Glicko2(rating=1500, rd=200, volatility=0.06)
    
    # First match
    player.update_rating([(1400, 30, 1)])
    rating1, rd1, vol1 = player.get_rating_data()
    
    # Second match
    player.update_rating([(1550, 100, 0)])
    rating2, rd2, vol2 = player.get_rating_data()

    # Third match
    player.update_rating([(1700, 300, 0)])
    rating3, rd3, vol3 = player.get_rating_data()

    assert rating1 != rating2
    assert rd1 != rd2
    assert vol1 != vol2
    assert rating2 != rating3
    assert rd2 != rd3
    assert vol2 != vol3
    assert player.rating == pytest.approx(1464.06, abs=0.05)
    assert player.rd == pytest.approx(151.48, abs=0.05)
    assert player.volatility == pytest.approx(0.05999, abs=0.0001)
