#!/usr/bin/env python3
"""
NFL Roster Depth Chart Compiler

Automatically compiles a complete 32-team NFL roster depth chart using:
1. ESPN depth chart pages (primary source)
2. ESPN API (backup source)
3. Player validation to ensure all 2553 players are collected

Features:
- Comprehensive scraping of all 32 NFL teams
- Backup API integration for missing data
- Player count validation (2553 total expected)
- Error handling and retry logic
- Data export (JSON/CSV)
- Detailed logging and progress tracking
- Position mapping and injury status tracking
"""

import os
import re
import sys
import json
import time
import logging
import argparse
from datetime import datetime
from typing import List, Dict, Optional, Tuple, Set
from collections import defaultdict
import csv

import requests
from bs4 import BeautifulSoup

# Constants
EXPECTED_TOTAL_PLAYERS = 2553  # Total NFL roster spots across 32 teams
PLAYERS_PER_TEAM_MIN = 53  # Minimum active roster
PLAYERS_PER_TEAM_MAX = 90  # Maximum with practice squad

# All 32 NFL teams with their ESPN slugs
NFL_TEAMS = {
    "ARI": "ari", "ATL": "atl", "BAL": "bal", "BUF": "buf",
    "CAR": "car", "CHI": "chi", "CIN": "cin", "CLE": "cle",
    "DAL": "dal", "DEN": "den", "DET": "det", "GB": "gb",
    "HOU": "hou", "IND": "ind", "JAX": "jax", "KC": "kc",
    "LAC": "lac", "LAR": "lar", "LV": "lv", "MIA": "mia",
    "MIN": "min", "NE": "ne", "NO": "no", "NYG": "nyg",
    "NYJ": "nyj", "PHI": "phi", "PIT": "pit", "SF": "sf",
    "SEA": "sea", "TB": "tb", "TEN": "ten", "WAS": "was"
}

# Position groups for classification
POSITION_GROUPS = {
    "QB": "Offense", "RB": "Offense", "FB": "Offense",
    "WR": "Offense", "TE": "Offense",
    "LT": "Offense", "LG": "Offense", "C": "Offense", 
    "RG": "Offense", "RT": "Offense", "OL": "Offense", "OT": "Offense", "G": "Offense",
    "DE": "Defense", "DT": "Defense", "NT": "Defense",
    "LB": "Defense", "OLB": "Defense", "MLB": "Defense", "ILB": "Defense",
    "CB": "Defense", "S": "Defense", "FS": "Defense", "SS": "Defense", "DB": "Defense",
    "K": "Special Teams", "P": "Special Teams", "LS": "Special Teams",
    "PR": "Special Teams", "KR": "Special Teams"
}

# Depth chart order labels
DEPTH_LABELS = ["1st", "2nd", "3rd", "4th", "5th", "6th"]

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('depth_chart_compilation.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class NFLDepthChartCompiler:
    """Main compiler class for NFL depth charts."""
    
    def __init__(self, output_dir: str = "output", max_retries: int = 3):
        """
        Initialize the compiler.
        
        Args:
            output_dir: Directory to save output files
            max_retries: Maximum number of retries for failed requests
        """
        self.output_dir = output_dir
        self.max_retries = max_retries
        self.players: List[Dict] = []
        self.teams_processed: Set[str] = set()
        self.failed_teams: Set[str] = set()
        self.player_names: Set[str] = set()  # Track unique player names
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        logger.info("NFL Depth Chart Compiler initialized")
        logger.info(f"Output directory: {output_dir}")
        logger.info(f"Max retries: {max_retries}")
    
    def fetch_page(self, url: str, timeout: int = 20) -> Optional[str]:
        """
        Fetch a web page with retries.
        
        Args:
            url: URL to fetch
            timeout: Request timeout in seconds
            
        Returns:
            Page HTML content or None if failed
        """
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        
        for attempt in range(self.max_retries):
            try:
                logger.info(f"Fetching {url} (attempt {attempt + 1}/{self.max_retries})")
                resp = requests.get(url, timeout=timeout, headers=headers)
                resp.raise_for_status()
                return resp.text
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed for {url}: {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    logger.error(f"All retries failed for {url}")
        return None
    
    def parse_player_info(self, raw_text: str) -> Tuple[str, str]:
        """
        Parse player name and injury status from text.
        
        Args:
            raw_text: Raw player text (e.g., "Patrick Mahomes" or "Travis Kelce (Q)")
            
        Returns:
            Tuple of (player_name, injury_status)
        """
        text = raw_text.strip()
        
        # Check for injury status in parentheses
        match = re.match(r'^(.+?)\s*\(([^)]+)\)\s*$', text)
        if match:
            name = match.group(1).strip()
            status = match.group(2).strip()
            return name, status
        
        # Check for status suffix
        match = re.match(r'^(.+?)\s+(Q|O|IR|PUP|D|OUT|QUESTIONABLE|DOUBTFUL)$', text, re.I)
        if match:
            name = match.group(1).strip()
            status = match.group(2).strip()
            return name, status
        
        return text, "Active"
    
    def scrape_espn_depth_chart(self, team_abbr: str, espn_slug: str) -> List[Dict]:
        """
        Scrape ESPN depth chart for a team.
        
        Args:
            team_abbr: Team abbreviation (e.g., "KC")
            espn_slug: ESPN team slug (e.g., "kc")
            
        Returns:
            List of player dictionaries
        """
        url_patterns = [
            f"https://www.espn.com/nfl/team/depth/_/name/{espn_slug}",
            f"https://www.espn.com/nfl/team/roster/_/name/{espn_slug}"
        ]
        
        players = []
        
        for url in url_patterns:
            html = self.fetch_page(url)
            if not html:
                continue
            
            soup = BeautifulSoup(html, "html.parser")
            
            # Try to find depth chart tables
            tables = soup.find_all("table", class_=re.compile(r"depth|roster", re.I))
            if not tables:
                tables = soup.find_all("table")
            
            logger.info(f"Found {len(tables)} tables for {team_abbr}")
            
            # Parse each table
            for table in tables:
                rows = table.find_all("tr")
                
                current_position = None
                depth_index = 0
                
                for row in rows:
                    # Check if this is a position header row
                    headers = row.find_all("th")
                    if headers:
                        # This might be a position label
                        header_text = headers[0].get_text(strip=True)
                        if len(header_text) <= 4 and header_text.isupper():
                            current_position = header_text
                            depth_index = 0
                            continue
                    
                    # Parse player row
                    cells = row.find_all("td")
                    if not cells:
                        continue
                    
                    # Extract player information
                    for cell in cells:
                        player_text = cell.get_text(" ", strip=True)
                        if not player_text or len(player_text) < 3:
                            continue
                        
                        # Parse player name and injury status
                        name, injury_status = self.parse_player_info(player_text)
                        
                        # Skip if not a valid player name
                        if not name or len(name) < 3:
                            continue
                        
                        # Infer position if not set
                        position = current_position or "UNK"
                        
                        # Add player
                        player_data = {
                            "name": name,
                            "team": team_abbr,
                            "position": position,
                            "depth": DEPTH_LABELS[min(depth_index, len(DEPTH_LABELS) - 1)],
                            "position_group": POSITION_GROUPS.get(position, "Unknown"),
                            "injury_status": injury_status,
                            "source": "ESPN",
                            "timestamp": datetime.utcnow().isoformat()
                        }
                        
                        players.append(player_data)
                        depth_index += 1
            
            if players:
                logger.info(f"Successfully scraped {len(players)} players from {url}")
                break
        
        return players
    
    def fetch_espn_api_backup(self, team_abbr: str, espn_slug: str) -> List[Dict]:
        """
        Fetch roster from ESPN API as backup.
        
        Args:
            team_abbr: Team abbreviation
            espn_slug: ESPN team slug
            
        Returns:
            List of player dictionaries
        """
        # ESPN's internal API endpoint (may require adjustments)
        api_urls = [
            f"https://site.api.espn.com/apis/site/v2/sports/football/nfl/teams/{espn_slug}/roster",
            f"https://sports.core.api.espn.com/v2/sports/football/leagues/nfl/teams/{espn_slug}/depthcharts"
        ]
        
        players = []
        
        for api_url in api_urls:
            html = self.fetch_page(api_url)
            if not html:
                continue
            
            try:
                data = json.loads(html)
                
                # Parse roster data (structure may vary)
                if "athletes" in data:
                    for athlete in data["athletes"]:
                        player_data = {
                            "name": athlete.get("displayName", "Unknown"),
                            "team": team_abbr,
                            "position": athlete.get("position", {}).get("abbreviation", "UNK"),
                            "depth": "UNK",
                            "position_group": "Unknown",
                            "injury_status": "Active",
                            "source": "ESPN_API",
                            "timestamp": datetime.utcnow().isoformat()
                        }
                        
                        # Map position group
                        pos = player_data["position"]
                        player_data["position_group"] = POSITION_GROUPS.get(pos, "Unknown")
                        
                        players.append(player_data)
                
                if players:
                    logger.info(f"Successfully fetched {len(players)} players from API")
                    break
                    
            except json.JSONDecodeError as e:
                logger.warning(f"Failed to parse JSON from {api_url}: {e}")
                continue
        
        return players
    
    def process_team(self, team_abbr: str) -> int:
        """
        Process a single team's depth chart.
        
        Args:
            team_abbr: Team abbreviation (e.g., "KC")
            
        Returns:
            Number of players found for this team
        """
        logger.info(f"Processing team: {team_abbr}")
        
        espn_slug = NFL_TEAMS.get(team_abbr)
        if not espn_slug:
            logger.error(f"Unknown team abbreviation: {team_abbr}")
            return 0
        
        # Try ESPN scraping first
        players = self.scrape_espn_depth_chart(team_abbr, espn_slug)
        
        # If scraping failed or returned too few players, try API backup
        if len(players) < PLAYERS_PER_TEAM_MIN:
            logger.warning(f"ESPN scraping returned only {len(players)} players, trying API backup")
            api_players = self.fetch_espn_api_backup(team_abbr, espn_slug)
            
            if len(api_players) > len(players):
                players = api_players
        
        # Add players to main list
        if players:
            self.players.extend(players)
            self.teams_processed.add(team_abbr)
            
            # Track unique player names
            for p in players:
                self.player_names.add(p["name"])
            
            logger.info(f"Successfully processed {team_abbr}: {len(players)} players")
        else:
            self.failed_teams.add(team_abbr)
            logger.error(f"Failed to get any players for {team_abbr}")
        
        return len(players)
    
    def compile_all_teams(self) -> None:
        """Compile depth charts for all 32 NFL teams."""
        logger.info("Starting compilation of all 32 NFL teams")
        logger.info("=" * 80)
        
        start_time = time.time()
        total_players = 0
        
        for team_abbr in sorted(NFL_TEAMS.keys()):
            try:
                count = self.process_team(team_abbr)
                total_players += count
                
                # Small delay between teams to be respectful
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"Unexpected error processing {team_abbr}: {e}")
                self.failed_teams.add(team_abbr)
        
        elapsed_time = time.time() - start_time
        
        logger.info("=" * 80)
        logger.info("Compilation complete")
        logger.info(f"Total time: {elapsed_time:.2f} seconds")
        logger.info(f"Teams processed: {len(self.teams_processed)}/32")
        logger.info(f"Teams failed: {len(self.failed_teams)}")
        logger.info(f"Total players found: {total_players}")
        logger.info(f"Unique players: {len(self.player_names)}")
        
        if self.failed_teams:
            logger.warning(f"Failed teams: {', '.join(sorted(self.failed_teams))}")
    
    def validate_data(self) -> Dict:
        """
        Validate the compiled data.
        
        Returns:
            Dictionary with validation results
        """
        logger.info("Validating compiled data...")
        
        validation = {
            "total_players": len(self.players),
            "unique_players": len(self.player_names),
            "teams_processed": len(self.teams_processed),
            "teams_failed": len(self.failed_teams),
            "expected_total": EXPECTED_TOTAL_PLAYERS,
            "meets_expectation": False,
            "players_by_team": {},
            "players_by_position_group": defaultdict(int),
            "warnings": [],
            "errors": []
        }
        
        # Count players by team
        for player in self.players:
            team = player["team"]
            validation["players_by_team"][team] = validation["players_by_team"].get(team, 0) + 1
            
            # Count by position group
            pos_group = player.get("position_group", "Unknown")
            validation["players_by_position_group"][pos_group] += 1
        
        # Check team player counts
        for team, count in validation["players_by_team"].items():
            if count < PLAYERS_PER_TEAM_MIN:
                validation["warnings"].append(
                    f"Team {team} has only {count} players (expected at least {PLAYERS_PER_TEAM_MIN})"
                )
            elif count > PLAYERS_PER_TEAM_MAX:
                validation["warnings"].append(
                    f"Team {team} has {count} players (expected at most {PLAYERS_PER_TEAM_MAX})"
                )
        
        # Check total player count
        if validation["total_players"] < EXPECTED_TOTAL_PLAYERS * 0.95:
            validation["errors"].append(
                f"Total player count ({validation['total_players']}) is significantly below "
                f"expected ({EXPECTED_TOTAL_PLAYERS})"
            )
        elif validation["total_players"] >= EXPECTED_TOTAL_PLAYERS * 0.95:
            validation["meets_expectation"] = True
        
        # Check for missing teams
        missing_teams = set(NFL_TEAMS.keys()) - self.teams_processed
        if missing_teams:
            validation["errors"].append(f"Missing teams: {', '.join(sorted(missing_teams))}")
        
        # Log results
        logger.info(f"Validation results:")
        logger.info(f"  Total players: {validation['total_players']}")
        logger.info(f"  Unique players: {validation['unique_players']}")
        logger.info(f"  Expected total: {validation['expected_total']}")
        logger.info(f"  Meets expectation: {validation['meets_expectation']}")
        
        if validation["warnings"]:
            logger.warning(f"Warnings: {len(validation['warnings'])}")
            for warning in validation["warnings"]:
                logger.warning(f"  - {warning}")
        
        if validation["errors"]:
            logger.error(f"Errors: {len(validation['errors'])}")
            for error in validation["errors"]:
                logger.error(f"  - {error}")
        
        return validation
    
    def export_json(self, filename: str = "nfl_depth_chart.json") -> str:
        """
        Export depth chart data to JSON.
        
        Args:
            filename: Output filename
            
        Returns:
            Path to exported file
        """
        filepath = os.path.join(self.output_dir, filename)
        
        export_data = {
            "metadata": {
                "compiled_at": datetime.utcnow().isoformat(),
                "total_players": len(self.players),
                "unique_players": len(self.player_names),
                "teams_processed": len(self.teams_processed),
                "compiler_version": "1.0.0"
            },
            "players": self.players
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Exported JSON to: {filepath}")
        return filepath
    
    def export_csv(self, filename: str = "nfl_depth_chart.csv") -> str:
        """
        Export depth chart data to CSV.
        
        Args:
            filename: Output filename
            
        Returns:
            Path to exported file
        """
        filepath = os.path.join(self.output_dir, filename)
        
        if not self.players:
            logger.warning("No players to export")
            return filepath
        
        # Get all keys from first player
        fieldnames = list(self.players[0].keys())
        
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self.players)
        
        logger.info(f"Exported CSV to: {filepath}")
        return filepath
    
    def export_validation_report(self, validation: Dict, filename: str = "validation_report.json") -> str:
        """
        Export validation report.
        
        Args:
            validation: Validation results dictionary
            filename: Output filename
            
        Returns:
            Path to exported file
        """
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(validation, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Exported validation report to: {filepath}")
        return filepath
    
    def generate_summary(self) -> str:
        """
        Generate a text summary of the compilation.
        
        Returns:
            Summary text
        """
        summary_lines = [
            "=" * 80,
            "NFL DEPTH CHART COMPILATION SUMMARY",
            "=" * 80,
            f"Compilation Date: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}",
            "",
            "STATISTICS:",
            f"  Total Players: {len(self.players)}",
            f"  Unique Players: {len(self.player_names)}",
            f"  Teams Processed: {len(self.teams_processed)}/32",
            f"  Teams Failed: {len(self.failed_teams)}",
            f"  Expected Total: {EXPECTED_TOTAL_PLAYERS}",
            "",
        ]
        
        if self.failed_teams:
            summary_lines.extend([
                "FAILED TEAMS:",
                f"  {', '.join(sorted(self.failed_teams))}",
                ""
            ])
        
        # Position group breakdown
        pos_groups = defaultdict(int)
        for player in self.players:
            pos_groups[player.get("position_group", "Unknown")] += 1
        
        summary_lines.append("POSITION GROUP BREAKDOWN:")
        for group in sorted(pos_groups.keys()):
            summary_lines.append(f"  {group}: {pos_groups[group]}")
        
        summary_lines.append("=" * 80)
        
        return "\n".join(summary_lines)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="NFL Roster Depth Chart Compiler",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "--output-dir",
        default="output",
        help="Output directory for compiled data (default: output)"
    )
    
    parser.add_argument(
        "--max-retries",
        type=int,
        default=3,
        help="Maximum retries for failed requests (default: 3)"
    )
    
    parser.add_argument(
        "--export-json",
        action="store_true",
        help="Export data as JSON"
    )
    
    parser.add_argument(
        "--export-csv",
        action="store_true",
        help="Export data as CSV"
    )
    
    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="Only validate data without compilation"
    )
    
    args = parser.parse_args()
    
    # Create compiler
    compiler = NFLDepthChartCompiler(
        output_dir=args.output_dir,
        max_retries=args.max_retries
    )
    
    # Compile all teams
    if not args.validate_only:
        compiler.compile_all_teams()
    
    # Validate
    validation = compiler.validate_data()
    
    # Export data
    if args.export_json or not args.export_csv:
        compiler.export_json()
    
    if args.export_csv:
        compiler.export_csv()
    
    # Export validation report
    compiler.export_validation_report(validation)
    
    # Print summary
    summary = compiler.generate_summary()
    print("\n" + summary)
    
    # Save summary to file
    summary_path = os.path.join(args.output_dir, "compilation_summary.txt")
    with open(summary_path, 'w') as f:
        f.write(summary)
    logger.info(f"Saved summary to: {summary_path}")
    
    # Exit code based on validation
    if validation["meets_expectation"] and not validation["errors"]:
        logger.info("Compilation successful!")
        return 0
    elif validation["errors"]:
        logger.error("Compilation completed with errors")
        return 1
    else:
        logger.warning("Compilation completed with warnings")
        return 0


if __name__ == "__main__":
    sys.exit(main())
