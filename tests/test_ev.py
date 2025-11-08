"""Tests for EV calculation module."""

import pytest
import pandas as pd
import numpy as np
from src.gorillagenics.ev import (
    calculate_ev,
    calculate_win_probability,
    calculate_parlay_probability,
    evaluate_pick_ev,
    batch_ev_calculation
)


class TestEVCalculations:
    """Test cases for EV calculations."""
    
    def test_calculate_ev_positive(self):
        """Test EV calculation for positive expected value."""
        result = calculate_ev(pick_odds=2.0, win_probability=0.6, stake=100)
        
        assert result['ev'] == pytest.approx(20.0)  # (0.6 * 2.0 * 100) - 100
        assert result['ev_percentage'] == pytest.approx(20.0)
        assert result['expected_return'] == pytest.approx(120.0)
    
    def test_calculate_ev_negative(self):
        """Test EV calculation for negative expected value."""
        result = calculate_ev(pick_odds=1.5, win_probability=0.4, stake=100)
        
        assert result['ev'] == pytest.approx(-40.0)  # (0.4 * 1.5 * 100) - 100
        assert result['ev_percentage'] == pytest.approx(-40.0)
    
    def test_calculate_win_probability_neutral(self):
        """Test win probability calculation for neutral game script."""
        player_stats = {'hit_rate': 0.5, 'avg_points': 15.0, 'consistency': 0.7}
        prob = calculate_win_probability(player_stats, "neutral")
        
        assert 0.0 <= prob <= 1.0
        assert prob == pytest.approx(0.5)  # Should equal base hit rate for neutral script
    
    def test_calculate_win_probability_shootout(self):
        """Test win probability calculation for shootout game script."""
        player_stats = {'hit_rate': 0.5, 'avg_points': 15.0, 'consistency': 0.7}
        prob = calculate_win_probability(player_stats, "shootout")
        
        assert prob > 0.5  # Should be higher than neutral
        assert prob == pytest.approx(0.575)  # 0.5 * 1.15
    
    def test_calculate_parlay_probability_independent(self):
        """Test parlay probability for independent events."""
        probabilities = [0.6, 0.5, 0.7]
        result = calculate_parlay_probability(probabilities)
        
        expected = 0.6 * 0.5 * 0.7
        assert result == pytest.approx(expected)
    
    def test_evaluate_pick_ev_complete(self):
        """Test complete pick evaluation."""
        pick_data = {
            'historical_hit_rate': 0.6,
            'avg_fantasy_points': 18.0,
            'consistency_score': 0.75
        }
        
        result = evaluate_pick_ev(pick_data, 1.91, {'script': 'neutral'})
        
        assert 'ev_percentage' in result
        assert 'win_probability' in result
        assert 'value_rating' in result
        assert result['win_probability'] == pytest.approx(0.6)
    
    def test_batch_ev_calculation(self):
        """Test batch EV calculation on DataFrame."""
        data = {
            'player_name': ['Player A', 'Player B'],
            'odds': [1.91, 2.0],
            'historical_hit_rate': [0.6, 0.5],
            'avg_fantasy_points': [18.0, 15.0],
            'consistency_score': [0.75, 0.65]
        }
        df = pd.DataFrame(data)
        
        result = batch_ev_calculation(df)
        
        assert len(result) == 2
        assert 'ev_ev_percentage' in result.columns
        assert 'ev_win_probability' in result.columns


@pytest.fixture
def sample_picks_data():
    """Sample picks data for testing."""
    return pd.DataFrame({
        'player_name': ['Josh Allen', 'Stefon Diggs', 'Travis Kelce'],
        'position': ['QB', 'WR', 'TE'],
        'team': ['BUF', 'BUF', 'KC'],
        'prop_type': ['Passing Yards', 'Receiving Yards', 'Receiving Yards'],
        'line': [275.5, 75.5, 65.5],
        'odds': [1.91, 1.87, 1.95],
        'historical_hit_rate': [0.65, 0.58, 0.62],
        'avg_fantasy_points': [22.5, 18.2, 16.8],
        'consistency_score': [0.75, 0.68, 0.72]
    })


def test_batch_calculation_with_sample_data(sample_picks_data):
    """Test batch calculation with realistic sample data."""
    result = batch_ev_calculation(sample_picks_data)
    
    assert len(result) == 3
    assert all(col.startswith('ev_') for col in result.columns if col not in sample_picks_data.columns)
    
    # Check that all EV calculations are reasonable
    assert all(result['ev_win_probability'] >= 0)
    assert all(result['ev_win_probability'] <= 1)
