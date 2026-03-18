import pytest
from app.services.engine import PatternScouter
from app.services.permutation_engine import PermutationScouter

def test_pattern_scouter_odds_evens():
    scouter_config = {
        "valid_odd_counts": [2, 3],
        "max_consecutive": 2,
        "max_start_ball": 34
    }
    # Valid: 2 odds (23, 55), 3 evens (10, 12, 44)
    assert PatternScouter.is_valid_pattern((10, 12, 23, 44, 55), scouter_config) == True
    
    # Invalid: 0 odds (all evens)
    assert PatternScouter.is_valid_pattern((10, 12, 24, 44, 56), scouter_config) == False

def test_pattern_scouter_consecutives():
    scouter_config = {
        "valid_odd_counts": [2, 3],
        "max_consecutive": 2,
        "max_start_ball": 34
    }
    # Invalid: 3 consecutive (10, 11, 12)
    assert PatternScouter.is_valid_pattern((10, 11, 12, 44, 55), scouter_config) == False
    
    # Valid: 2 consecutive (10, 11)
    assert PatternScouter.is_valid_pattern((10, 11, 23, 44, 55), scouter_config) == True

def test_pattern_scouter_start_ball():
    scouter_config = {
        "valid_odd_counts": [2, 3],
        "max_consecutive": 2,
        "max_start_ball": 20
    }
    # Invalid: Starts > 20
    assert PatternScouter.is_valid_pattern((21, 22, 25, 44, 55), scouter_config) == False

def test_permutation_scouter_sum():
    scouter_config = {
        "min_sum": 11,
        "max_sum": 16,
        "max_repeats": 2
    }
    # Valid: sum = 12 (3+4+5)
    assert PermutationScouter.is_valid_pattern((3, 4, 5), scouter_config) == True
    
    # Invalid: sum = 27 (9+9+9)
    assert PermutationScouter.is_valid_pattern((9, 9, 9), scouter_config) == False
    
    # Invalid: sum = 6 (1+2+3)
    assert PermutationScouter.is_valid_pattern((1, 2, 3), scouter_config) == False

def test_permutation_scouter_repeats():
    scouter_config = {
        "min_sum": 0,
        "max_sum": 27,
        "max_repeats": 2
    }
    # Valid: 1 repeat (all unique)
    assert PermutationScouter.is_valid_pattern((1, 2, 3), scouter_config) == True
    
    # Invalid: 2 repeats (e.g. doubles) when max_repeats is set to 2 (meaning max allowed is strictly less than 2, wait let's check code logic)
    # The code says: if max_repeats_found >= max_repeats: return False
    # So if max_repeats is 2, a double (2) will be >= 2 and return False.
    assert PermutationScouter.is_valid_pattern((3, 3, 5), scouter_config) == False
