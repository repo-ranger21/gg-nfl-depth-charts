"""Tests for NFL Depth Chart Compiler."""

import pytest
import json
import csv
import os
import tempfile
from unittest.mock import Mock, patch, MagicMock
from nfl_depth_chart_compiler import (
    NFLDepthChartCompiler,
    NFL_TEAMS,
    EXPECTED_TOTAL_PLAYERS,
    POSITION_GROUPS
)


class TestNFLDepthChartCompiler:
    """Test cases for NFL Depth Chart Compiler."""
    
    @pytest.fixture
    def compiler(self, tmp_path):
        """Create compiler instance with temporary output directory."""
        return NFLDepthChartCompiler(output_dir=str(tmp_path), max_retries=2)
    
    @pytest.fixture
    def mock_html_depth_chart(self):
        """Mock HTML for ESPN depth chart page."""
        return """
        <html>
        <body>
            <table class="depth-chart">
                <tr><th>QB</th></tr>
                <tr><td>Patrick Mahomes</td></tr>
                <tr><td>Chad Henne</td></tr>
                <tr><th>RB</th></tr>
                <tr><td>Isiah Pacheco</td></tr>
                <tr><td>Jerick McKinnon (Q)</td></tr>
                <tr><th>WR</th></tr>
                <tr><td>Travis Kelce</td></tr>
            </table>
        </body>
        </html>
        """
    
    def test_compiler_initialization(self, tmp_path):
        """Test compiler initialization."""
        compiler = NFLDepthChartCompiler(output_dir=str(tmp_path), max_retries=3)
        
        assert compiler.output_dir == str(tmp_path)
        assert compiler.max_retries == 3
        assert len(compiler.players) == 0
        assert len(compiler.teams_processed) == 0
        assert os.path.exists(str(tmp_path))
    
    def test_parse_player_info_healthy(self, compiler):
        """Test parsing healthy player name."""
        name, status = compiler.parse_player_info("Patrick Mahomes")
        
        assert name == "Patrick Mahomes"
        assert status == "Active"
    
    def test_parse_player_info_with_injury(self, compiler):
        """Test parsing player with injury status."""
        name, status = compiler.parse_player_info("Travis Kelce (Q)")
        
        assert name == "Travis Kelce"
        assert status == "Q"
    
    def test_parse_player_info_questionable(self, compiler):
        """Test parsing player with questionable status."""
        name, status = compiler.parse_player_info("Mike Evans (Questionable)")
        
        assert name == "Mike Evans"
        assert status == "Questionable"
    
    def test_parse_player_info_out(self, compiler):
        """Test parsing player with OUT status."""
        name, status = compiler.parse_player_info("Aaron Rodgers OUT")
        
        assert name == "Aaron Rodgers"
        assert status == "OUT"
    
    @patch('nfl_depth_chart_compiler.requests.get')
    def test_fetch_page_success(self, mock_get, compiler):
        """Test successful page fetch."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "<html>Test</html>"
        mock_get.return_value = mock_response
        
        result = compiler.fetch_page("https://example.com")
        
        assert result == "<html>Test</html>"
        assert mock_get.call_count == 1
    
    @patch('nfl_depth_chart_compiler.requests.get')
    @patch('nfl_depth_chart_compiler.time.sleep')  # Mock sleep to speed up tests
    def test_fetch_page_retry(self, mock_sleep, mock_get, compiler):
        """Test page fetch with retries."""
        # Create mock responses
        mock_response_success = Mock()
        mock_response_success.status_code = 200
        mock_response_success.text = "<html>Success</html>"
        mock_response_success.raise_for_status.return_value = None
        
        # First call raises exception, second succeeds (compiler has max_retries=2)
        mock_get.side_effect = [
            Exception("Connection error"),
            mock_response_success
        ]
        
        result = compiler.fetch_page("https://example.com")
        
        assert result == "<html>Success</html>"
        assert mock_get.call_count == 2
        assert mock_sleep.call_count == 1  # Should sleep after first failure
    
    @patch('nfl_depth_chart_compiler.requests.get')
    def test_fetch_page_all_retries_fail(self, mock_get, compiler):
        """Test page fetch when all retries fail."""
        mock_get.side_effect = Exception("Connection error")
        
        result = compiler.fetch_page("https://example.com")
        
        assert result is None
        assert mock_get.call_count == compiler.max_retries
    
    @patch.object(NFLDepthChartCompiler, 'fetch_page')
    def test_scrape_espn_depth_chart(self, mock_fetch, compiler, mock_html_depth_chart):
        """Test scraping ESPN depth chart."""
        mock_fetch.return_value = mock_html_depth_chart
        
        players = compiler.scrape_espn_depth_chart("KC", "kc")
        
        assert len(players) > 0
        assert all(p["team"] == "KC" for p in players)
        assert all(p["source"] == "ESPN" for p in players)
        assert any(p["name"] == "Patrick Mahomes" for p in players)
        assert any(p["name"] == "Jerick McKinnon" for p in players)
        
        # Check injury status parsing
        mckinnon = [p for p in players if p["name"] == "Jerick McKinnon"][0]
        assert mckinnon["injury_status"] == "Q"
    
    def test_process_team_unknown_team(self, compiler):
        """Test processing unknown team."""
        result = compiler.process_team("XXX")
        
        assert result == 0
        assert "XXX" not in compiler.teams_processed
    
    @patch.object(NFLDepthChartCompiler, 'scrape_espn_depth_chart')
    @patch.object(NFLDepthChartCompiler, 'fetch_espn_api_backup')
    def test_process_team_with_fallback(self, mock_api, mock_scrape, compiler):
        """Test team processing with API fallback."""
        # Scraping returns too few players
        mock_scrape.return_value = [
            {"name": "Player 1", "team": "KC", "position": "QB"}
        ]
        
        # API returns more players
        mock_api.return_value = [
            {"name": f"Player {i}", "team": "KC", "position": "QB"}
            for i in range(55)
        ]
        
        result = compiler.process_team("KC")
        
        assert result == 55
        assert "KC" in compiler.teams_processed
        assert len(compiler.players) == 55
    
    def test_validate_data_empty(self, compiler):
        """Test validation with no data."""
        validation = compiler.validate_data()
        
        assert validation["total_players"] == 0
        assert validation["meets_expectation"] is False
        assert len(validation["errors"]) > 0
    
    def test_validate_data_with_players(self, compiler):
        """Test validation with sufficient players."""
        # Add mock players
        for i in range(EXPECTED_TOTAL_PLAYERS):
            team = list(NFL_TEAMS.keys())[i % 32]
            compiler.players.append({
                "name": f"Player {i}",
                "team": team,
                "position": "QB",
                "position_group": "Offense",
                "injury_status": "Active"
            })
            compiler.player_names.add(f"Player {i}")
        
        compiler.teams_processed = set(NFL_TEAMS.keys())
        
        validation = compiler.validate_data()
        
        assert validation["total_players"] == EXPECTED_TOTAL_PLAYERS
        assert validation["meets_expectation"] is True
        assert len(validation["errors"]) == 0
    
    def test_validate_data_missing_teams(self, compiler):
        """Test validation with missing teams."""
        # Add players for only half the teams
        teams_to_add = list(NFL_TEAMS.keys())[:16]
        for team in teams_to_add:
            for i in range(53):
                compiler.players.append({
                    "name": f"{team} Player {i}",
                    "team": team,
                    "position": "QB",
                    "position_group": "Offense"
                })
        
        compiler.teams_processed = set(teams_to_add)
        
        validation = compiler.validate_data()
        
        assert validation["teams_processed"] == 16
        assert len(validation["errors"]) > 0
        assert any("Missing teams" in error for error in validation["errors"])
    
    def test_export_json(self, compiler, tmp_path):
        """Test JSON export."""
        # Add some mock data
        compiler.players = [
            {
                "name": "Patrick Mahomes",
                "team": "KC",
                "position": "QB",
                "depth": "1st",
                "position_group": "Offense",
                "injury_status": "Active"
            }
        ]
        compiler.player_names.add("Patrick Mahomes")
        compiler.teams_processed.add("KC")
        
        filepath = compiler.export_json("test_output.json")
        
        assert os.path.exists(filepath)
        
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        assert "metadata" in data
        assert "players" in data
        assert data["metadata"]["total_players"] == 1
        assert len(data["players"]) == 1
        assert data["players"][0]["name"] == "Patrick Mahomes"
    
    def test_export_csv(self, compiler, tmp_path):
        """Test CSV export."""
        # Add some mock data
        compiler.players = [
            {
                "name": "Patrick Mahomes",
                "team": "KC",
                "position": "QB",
                "depth": "1st",
                "position_group": "Offense",
                "injury_status": "Active"
            },
            {
                "name": "Travis Kelce",
                "team": "KC",
                "position": "TE",
                "depth": "1st",
                "position_group": "Offense",
                "injury_status": "Active"
            }
        ]
        
        filepath = compiler.export_csv("test_output.csv")
        
        assert os.path.exists(filepath)
        
        with open(filepath, 'r', newline='') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        
        assert len(rows) == 2
        assert rows[0]["name"] == "Patrick Mahomes"
        assert rows[1]["name"] == "Travis Kelce"
    
    def test_export_validation_report(self, compiler, tmp_path):
        """Test validation report export."""
        validation = {
            "total_players": 100,
            "meets_expectation": False,
            "warnings": ["Test warning"],
            "errors": []
        }
        
        filepath = compiler.export_validation_report(validation, "test_validation.json")
        
        assert os.path.exists(filepath)
        
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        assert data["total_players"] == 100
        assert data["meets_expectation"] is False
    
    def test_generate_summary(self, compiler):
        """Test summary generation."""
        compiler.players = [{"name": "Player 1", "position_group": "Offense"}]
        compiler.player_names = {"Player 1"}
        compiler.teams_processed = {"KC"}
        compiler.failed_teams = set()
        
        summary = compiler.generate_summary()
        
        assert "NFL DEPTH CHART COMPILATION SUMMARY" in summary
        assert "Total Players: 1" in summary
        assert "Unique Players: 1" in summary
        assert "Teams Processed: 1/32" in summary
    
    def test_all_teams_defined(self):
        """Test that all 32 NFL teams are defined."""
        assert len(NFL_TEAMS) == 32
        
        # Check that all teams have valid abbreviations
        expected_teams = {
            "ARI", "ATL", "BAL", "BUF", "CAR", "CHI", "CIN", "CLE",
            "DAL", "DEN", "DET", "GB", "HOU", "IND", "JAX", "KC",
            "LAC", "LAR", "LV", "MIA", "MIN", "NE", "NO", "NYG",
            "NYJ", "PHI", "PIT", "SF", "SEA", "TB", "TEN", "WAS"
        }
        
        assert set(NFL_TEAMS.keys()) == expected_teams
    
    def test_position_groups_complete(self):
        """Test that position groups are properly defined."""
        assert "QB" in POSITION_GROUPS
        assert "RB" in POSITION_GROUPS
        assert "WR" in POSITION_GROUPS
        assert "TE" in POSITION_GROUPS
        assert "K" in POSITION_GROUPS
        assert "P" in POSITION_GROUPS
        
        # Check position group values
        assert POSITION_GROUPS["QB"] == "Offense"
        assert POSITION_GROUPS["CB"] == "Defense"
        assert POSITION_GROUPS["K"] == "Special Teams"


class TestIntegration:
    """Integration tests for the compiler."""
    
    @patch.object(NFLDepthChartCompiler, 'fetch_page')
    def test_full_compilation_mock(self, mock_fetch, tmp_path):
        """Test full compilation with mocked data."""
        # Mock HTML that will be returned for all teams
        mock_html = """
        <html>
        <body>
            <table>
                <tr><th>QB</th></tr>
                <tr><td>Quarterback One</td></tr>
                <tr><td>Quarterback Two</td></tr>
            </table>
        </body>
        </html>
        """
        mock_fetch.return_value = mock_html
        
        compiler = NFLDepthChartCompiler(output_dir=str(tmp_path), max_retries=1)
        
        # Process just a few teams for speed
        test_teams = ["KC", "SF", "BUF"]
        for team in test_teams:
            compiler.process_team(team)
        
        assert len(compiler.teams_processed) == 3
        assert len(compiler.players) > 0
        assert all(p["team"] in test_teams for p in compiler.players)
    
    def test_expected_player_count_constant(self):
        """Test that expected player count is reasonable."""
        # 32 teams * ~53 active roster = ~1696 minimum
        # 32 teams * ~90 with practice squad = ~2880 maximum
        assert 1500 <= EXPECTED_TOTAL_PLAYERS <= 3000
        assert EXPECTED_TOTAL_PLAYERS == 2553


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
