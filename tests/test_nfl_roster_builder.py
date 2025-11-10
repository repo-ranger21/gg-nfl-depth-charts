#!/usr/bin/env python3
"""
Tests for NFL Roster Builder
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
import pandas as pd

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from nfl_roster_builder import (
    NFLRosterBuilder, 
    PlayerRecord, 
    ESPN_TEAMS,
    POSITION_GROUPS,
    DEPTH_MAP
)


class TestPlayerRecord:
    """Test PlayerRecord dataclass"""
    
    def test_player_record_creation(self):
        """Test creating a basic player record"""
        record = PlayerRecord(
            player_name="Tom Brady",
            team_name="Tampa Bay Buccaneers",
            team_abbr="TB",
            position="QB",
            depth_or_status="Starter",
            position_group="Offense",
            source="ESPN Depth Chart"
        )
        
        assert record.player_name == "Tom Brady"
        assert record.team_abbr == "TB"
        assert record.position == "QB"
        assert record.depth_or_status == "Starter"
    
    def test_player_record_to_dict(self):
        """Test converting player record to dictionary"""
        record = PlayerRecord(
            player_name="Patrick Mahomes",
            team_name="Kansas City Chiefs",
            team_abbr="KC",
            position="QB",
            depth_or_status="Starter",
            position_group="Offense",
            jersey_number="15",
            source="ESPN API"
        )
        
        result = record.to_dict()
        
        assert result['Player Name'] == "Patrick Mahomes"
        assert result['Team Name'] == "Kansas City Chiefs"
        assert result['Team Abbr'] == "KC"
        assert result['Position'] == "QB"
        assert result['Depth or Status'] == "Starter"
        assert result['Jersey Number'] == "15"
    
    def test_player_record_get_key(self):
        """Test unique key generation for deduplication"""
        record1 = PlayerRecord(
            player_name="Josh Allen",
            team_name="Buffalo Bills",
            team_abbr="BUF",
            position="QB",
            depth_or_status="Starter",
        )
        
        record2 = PlayerRecord(
            player_name="Josh Allen",
            team_name="Buffalo Bills", 
            team_abbr="BUF",
            position="QB",
            depth_or_status="2nd",  # Different depth but same key
        )
        
        assert record1.get_key() == record2.get_key()
        assert record1.get_key() == "Josh Allen|BUF|QB"


class TestNFLRosterBuilder:
    """Test NFLRosterBuilder class"""
    
    def test_initialization(self):
        """Test builder initialization"""
        builder = NFLRosterBuilder()
        
        assert builder.players == []
        assert builder.session is not None
        assert 'User-Agent' in builder.session.headers
    
    def test_parse_player_text_healthy(self):
        """Test parsing healthy player text"""
        builder = NFLRosterBuilder()
        
        name, status = builder._parse_player_text("Tom Brady")
        assert name == "Tom Brady"
        assert status == "Active"
    
    def test_parse_player_text_with_status(self):
        """Test parsing player text with injury status"""
        builder = NFLRosterBuilder()
        
        # Parentheses format
        name, status = builder._parse_player_text("Mike Evans (Q)")
        assert name == "Mike Evans"
        assert status == "Q"
        
        # Full word format
        name, status = builder._parse_player_text("Rob Gronkowski (Out)")
        assert name == "Rob Gronkowski"
        assert status == "Out"
        
        # Trailing code
        name, status = builder._parse_player_text("Cooper Kupp IR")
        assert name == "Cooper Kupp"
        assert status == "IR"
    
    def test_merge_roster_deduplication(self):
        """Test merge_roster with deduplication"""
        builder = NFLRosterBuilder()
        
        # Create depth chart records
        depth_records = [
            PlayerRecord(
                player_name="Player A",
                team_name="Test Team",
                team_abbr="TST",
                position="QB",
                depth_or_status="Starter",
                source="Depth Chart"
            ),
            PlayerRecord(
                player_name="Player B",
                team_name="Test Team",
                team_abbr="TST",
                position="RB",
                depth_or_status="Starter",
                source="Depth Chart"
            )
        ]
        
        # Create API records (one duplicate, one new)
        api_records = [
            PlayerRecord(
                player_name="Player A",  # Duplicate
                team_name="Test Team",
                team_abbr="TST",
                position="QB",
                depth_or_status="Starter",
                source="API"
            ),
            PlayerRecord(
                player_name="Player C",  # New
                team_name="Test Team",
                team_abbr="TST",
                position="WR",
                depth_or_status="Starter",
                source="API"
            )
        ]
        
        merged = builder.merge_roster(depth_records, api_records)
        
        # Should have 3 unique players (A, B, C)
        assert len(merged) == 3
        
        # Verify Player A comes from depth chart (higher priority)
        player_a = [p for p in merged if p.player_name == "Player A"][0]
        assert player_a.source == "Depth Chart"
        
        # Verify Player C comes from API
        player_c = [p for p in merged if p.player_name == "Player C"][0]
        assert player_c.source == "API"
    
    def test_merge_roster_priority(self):
        """Test that depth chart data takes priority over API data"""
        builder = NFLRosterBuilder()
        
        depth_records = [
            PlayerRecord(
                player_name="John Doe",
                team_name="Test Team",
                team_abbr="TST",
                position="QB",
                depth_or_status="Starter",
                jersey_number="12",
                source="Depth Chart"
            )
        ]
        
        api_records = [
            PlayerRecord(
                player_name="John Doe",
                team_name="Test Team",
                team_abbr="TST",
                position="QB",
                depth_or_status="2nd",
                jersey_number="99",  # Different jersey
                source="API"
            )
        ]
        
        merged = builder.merge_roster(depth_records, api_records)
        
        assert len(merged) == 1
        assert merged[0].depth_or_status == "Starter"
        assert merged[0].jersey_number == "12"
        assert merged[0].source == "Depth Chart"
    
    def test_to_dataframe_empty(self):
        """Test converting empty builder to DataFrame"""
        builder = NFLRosterBuilder()
        df = builder.to_dataframe()
        
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 0
    
    def test_to_dataframe_with_data(self):
        """Test converting builder with data to DataFrame"""
        builder = NFLRosterBuilder()
        
        # Add some test records
        builder.players = [
            PlayerRecord(
                player_name="Player 1",
                team_name="Team A",
                team_abbr="TMA",
                position="QB",
                depth_or_status="Starter",
                position_group="Offense",
                source="Test"
            ),
            PlayerRecord(
                player_name="Player 2",
                team_name="Team A",
                team_abbr="TMA",
                position="RB",
                depth_or_status="2nd",
                position_group="Offense",
                source="Test"
            )
        ]
        
        df = builder.to_dataframe()
        
        assert len(df) == 2
        assert 'Player Name' in df.columns
        assert 'Team Name' in df.columns
        assert 'Depth or Status' in df.columns
        assert df.loc[0, 'Player Name'] == "Player 1"
        assert df.loc[1, 'Player Name'] == "Player 2"
    
    def test_get_statistics(self):
        """Test statistics generation"""
        builder = NFLRosterBuilder()
        
        # Add test data
        builder.players = [
            PlayerRecord(
                player_name="QB1",
                team_name="Team A",
                team_abbr="TMA",
                position="QB",
                depth_or_status="Starter",
                position_group="Offense",
                source="Depth Chart"
            ),
            PlayerRecord(
                player_name="RB1",
                team_name="Team A",
                team_abbr="TMA",
                position="RB",
                depth_or_status="Starter",
                position_group="Offense",
                source="API"
            ),
            PlayerRecord(
                player_name="QB2",
                team_name="Team B",
                team_abbr="TMB",
                position="QB",
                depth_or_status="Starter",
                position_group="Offense",
                source="Depth Chart"
            )
        ]
        
        stats = builder.get_statistics()
        
        assert stats['total_players'] == 3
        assert stats['total_teams'] == 2
        assert 'TMA' in stats['players_per_team']
        assert 'TMB' in stats['players_per_team']
        assert stats['players_per_team']['TMA'] == 2
        assert stats['players_per_team']['TMB'] == 1
    
    @patch('nfl_roster_builder.requests.Session.get')
    def test_fetch_roster_api_espn(self, mock_get):
        """Test ESPN API roster fetch"""
        builder = NFLRosterBuilder()
        
        # Mock API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'athletes': [
                {
                    'position': 'QB',
                    'items': [
                        {
                            'fullName': 'Test Player',
                            'jersey': '12',
                            'status': {'type': 'Active'}
                        }
                    ]
                }
            ]
        }
        mock_get.return_value = mock_response
        
        team_info = {
            'name': 'Test Team',
            'abbr': 'TST',
            'team_id': '1'
        }
        
        records = builder.fetch_roster_api_espn('tst', team_info)
        
        assert len(records) > 0
        assert records[0].player_name == 'Test Player'
        assert records[0].position == 'QB'
        assert records[0].jersey_number == '12'


class TestESPNTeamsConfiguration:
    """Test ESPN teams configuration"""
    
    def test_all_32_teams_present(self):
        """Test that all 32 NFL teams are configured"""
        assert len(ESPN_TEAMS) == 32
    
    def test_required_teams_included(self):
        """Test that previously missing teams (BUF, MIA) are now included"""
        assert 'buf' in ESPN_TEAMS
        assert 'mia' in ESPN_TEAMS
        
        assert ESPN_TEAMS['buf']['abbr'] == 'BUF'
        assert ESPN_TEAMS['mia']['abbr'] == 'MIA'
    
    def test_team_info_structure(self):
        """Test that each team has required fields"""
        for team_slug, team_info in ESPN_TEAMS.items():
            assert 'abbr' in team_info
            assert 'team_id' in team_info
            assert 'name' in team_info
            
            # Validate field types
            assert isinstance(team_info['abbr'], str)
            assert isinstance(team_info['team_id'], str)
            assert isinstance(team_info['name'], str)


class TestPositionGroupsMapping:
    """Test position groups configuration"""
    
    def test_offense_positions(self):
        """Test offensive positions are correctly mapped"""
        offensive_positions = ['QB', 'RB', 'WR', 'TE', 'FB', 'LT', 'LG', 'C', 'RG', 'RT']
        
        for pos in offensive_positions:
            assert pos in POSITION_GROUPS
            assert POSITION_GROUPS[pos] == "Offense"
    
    def test_defense_positions(self):
        """Test defensive positions are correctly mapped"""
        defensive_positions = ['DE', 'DT', 'NT', 'LB', 'OLB', 'MLB', 'CB', 'S', 'FS', 'SS']
        
        for pos in defensive_positions:
            assert pos in POSITION_GROUPS
            assert POSITION_GROUPS[pos] == "Defense"
    
    def test_special_teams_positions(self):
        """Test special teams positions are correctly mapped"""
        st_positions = ['K', 'P', 'PK', 'H', 'PR', 'KR', 'LS']
        
        for pos in st_positions:
            assert pos in POSITION_GROUPS
            assert POSITION_GROUPS[pos] == "Special Teams"


class TestDepthMap:
    """Test depth map configuration"""
    
    def test_depth_map_exists(self):
        """Test depth map has expected values"""
        assert "Starter" in DEPTH_MAP
        assert "2nd" in DEPTH_MAP
        assert len(DEPTH_MAP) >= 4  # At least 4 depth levels


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
