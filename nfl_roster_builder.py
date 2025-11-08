#!/usr/bin/env python3
"""
Enhanced NFL Roster Builder with ESPN Depth Chart Scraping and Roster API Fallback

Features:
- Processes all 32 NFL teams
- Handles 2500+ player data points
- ESPN depth chart scraping
- Fallback ESPN Roster API endpoint
- Deduplication via merge_roster()
- Outputs validated DataFrame with [Player Name | Team Name | Depth or Status]
"""
from __future__ import annotations

import logging
import re
import time
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass

import pandas as pd
import requests
from bs4 import BeautifulSoup

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ESPN team mappings (abbreviation -> team_id for API)
ESPN_TEAMS = {
    'buf': {'abbr': 'BUF', 'team_id': '2', 'name': 'Buffalo Bills'},
    'mia': {'abbr': 'MIA', 'team_id': '15', 'name': 'Miami Dolphins'},
    'ne': {'abbr': 'NE', 'team_id': '17', 'name': 'New England Patriots'},
    'nyj': {'abbr': 'NYJ', 'team_id': '20', 'name': 'New York Jets'},
    'bal': {'abbr': 'BAL', 'team_id': '33', 'name': 'Baltimore Ravens'},
    'cin': {'abbr': 'CIN', 'team_id': '4', 'name': 'Cincinnati Bengals'},
    'cle': {'abbr': 'CLE', 'team_id': '5', 'name': 'Cleveland Browns'},
    'pit': {'abbr': 'PIT', 'team_id': '23', 'name': 'Pittsburgh Steelers'},
    'hou': {'abbr': 'HOU', 'team_id': '34', 'name': 'Houston Texans'},
    'ind': {'abbr': 'IND', 'team_id': '11', 'name': 'Indianapolis Colts'},
    'jax': {'abbr': 'JAX', 'team_id': '30', 'name': 'Jacksonville Jaguars'},
    'ten': {'abbr': 'TEN', 'team_id': '10', 'name': 'Tennessee Titans'},
    'den': {'abbr': 'DEN', 'team_id': '7', 'name': 'Denver Broncos'},
    'kc': {'abbr': 'KC', 'team_id': '12', 'name': 'Kansas City Chiefs'},
    'lv': {'abbr': 'LV', 'team_id': '13', 'name': 'Las Vegas Raiders'},
    'lac': {'abbr': 'LAC', 'team_id': '24', 'name': 'Los Angeles Chargers'},
    'dal': {'abbr': 'DAL', 'team_id': '6', 'name': 'Dallas Cowboys'},
    'nyg': {'abbr': 'NYG', 'team_id': '19', 'name': 'New York Giants'},
    'phi': {'abbr': 'PHI', 'team_id': '21', 'name': 'Philadelphia Eagles'},
    'was': {'abbr': 'WSH', 'team_id': '28', 'name': 'Washington Commanders'},
    'chi': {'abbr': 'CHI', 'team_id': '3', 'name': 'Chicago Bears'},
    'det': {'abbr': 'DET', 'team_id': '8', 'name': 'Detroit Lions'},
    'gb': {'abbr': 'GB', 'team_id': '9', 'name': 'Green Bay Packers'},
    'min': {'abbr': 'MIN', 'team_id': '16', 'name': 'Minnesota Vikings'},
    'atl': {'abbr': 'ATL', 'team_id': '1', 'name': 'Atlanta Falcons'},
    'car': {'abbr': 'CAR', 'team_id': '29', 'name': 'Carolina Panthers'},
    'no': {'abbr': 'NO', 'team_id': '18', 'name': 'New Orleans Saints'},
    'tb': {'abbr': 'TB', 'team_id': '27', 'name': 'Tampa Bay Buccaneers'},
    'ari': {'abbr': 'ARI', 'team_id': '22', 'name': 'Arizona Cardinals'},
    'lar': {'abbr': 'LAR', 'team_id': '14', 'name': 'Los Angeles Rams'},
    'sf': {'abbr': 'SF', 'team_id': '25', 'name': 'San Francisco 49ers'},
    'sea': {'abbr': 'SEA', 'team_id': '26', 'name': 'Seattle Seahawks'},
}

# Position groups mapping
POSITION_GROUPS = {
    "QB": "Offense", "RB": "Offense", "WR": "Offense", "TE": "Offense", "FB": "Offense",
    "LT": "Offense", "LG": "Offense", "C": "Offense", "RG": "Offense", "RT": "Offense",
    "OL": "Offense", "OT": "Offense", "OG": "Offense",
    "DE": "Defense", "DT": "Defense", "NT": "Defense", "LB": "Defense", "OLB": "Defense",
    "MLB": "Defense", "ILB": "Defense", "CB": "Defense", "S": "Defense", "FS": "Defense", 
    "SS": "Defense", "DB": "Defense", "DL": "Defense",
    "K": "Special Teams", "P": "Special Teams", "PK": "Special Teams", "H": "Special Teams",
    "PR": "Special Teams", "KR": "Special Teams", "LS": "Special Teams"
}

DEPTH_MAP = ["Starter", "2nd", "3rd", "4th", "5th", "Backup"]


@dataclass
class PlayerRecord:
    """Represents a single player entry"""
    player_name: str
    team_name: str
    team_abbr: str
    position: str
    depth_or_status: str
    position_group: str = ""
    jersey_number: str = ""
    source: str = ""
    
    def to_dict(self) -> Dict:
        return {
            'Player Name': self.player_name,
            'Team Name': self.team_name,
            'Team Abbr': self.team_abbr,
            'Position': self.position,
            'Depth or Status': self.depth_or_status,
            'Position Group': self.position_group,
            'Jersey Number': self.jersey_number,
            'Source': self.source,
        }
    
    def get_key(self) -> str:
        """Generate unique key for deduplication"""
        return f"{self.player_name}|{self.team_abbr}|{self.position}"


class NFLRosterBuilder:
    """Main class for building NFL rosters from multiple sources"""
    
    def __init__(self):
        self.players: List[PlayerRecord] = []
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def fetch_depth_chart_espn(self, team_slug: str, team_info: Dict) -> List[PlayerRecord]:
        """
        Scrape ESPN depth chart page for a team
        URL: https://www.espn.com/nfl/team/depth/_/name/{team_abbr}
        """
        records = []
        url = f"https://www.espn.com/nfl/team/depth/_/name/{team_slug}"
        
        try:
            logger.info(f"Fetching ESPN depth chart for {team_info['name']} from {url}")
            resp = self.session.get(url, timeout=20)
            resp.raise_for_status()
            
            soup = BeautifulSoup(resp.text, 'html.parser')
            
            # ESPN depth charts typically use tables or structured divs
            # Look for position groups and player listings
            depth_tables = soup.find_all('table', class_=re.compile('Table'))
            
            if depth_tables:
                for table in depth_tables:
                    records.extend(self._parse_depth_table(table, team_info))
            else:
                # Try alternative parsing methods
                depth_sections = soup.find_all('div', class_=re.compile('depth|roster'))
                for section in depth_sections:
                    records.extend(self._parse_depth_section(section, team_info))
            
            logger.info(f"Scraped {len(records)} players from ESPN depth chart for {team_info['abbr']}")
            
        except Exception as e:
            logger.error(f"Error fetching ESPN depth chart for {team_slug}: {e}")
        
        return records
    
    def _parse_depth_table(self, table, team_info: Dict) -> List[PlayerRecord]:
        """Parse ESPN depth chart table"""
        records = []
        
        try:
            rows = table.find_all('tr')
            position = None
            
            for row in rows:
                # Check if this row contains position header
                header = row.find('th')
                if header:
                    position_text = header.get_text(strip=True)
                    # Extract position abbreviation (e.g., "QB", "RB", "WR")
                    match = re.match(r'^([A-Z]{1,3})', position_text)
                    if match:
                        position = match.group(1)
                        continue
                
                # Parse player cells
                cells = row.find_all('td')
                if cells and position:
                    for depth_idx, cell in enumerate(cells):
                        player_text = cell.get_text(strip=True)
                        if player_text:
                            # Parse player name and status
                            name, status = self._parse_player_text(player_text)
                            if name:
                                depth = DEPTH_MAP[depth_idx] if depth_idx < len(DEPTH_MAP) else "Backup"
                                pos_group = POSITION_GROUPS.get(position, "Unknown")
                                
                                record = PlayerRecord(
                                    player_name=name,
                                    team_name=team_info['name'],
                                    team_abbr=team_info['abbr'],
                                    position=position,
                                    depth_or_status=f"{depth} - {status}" if status != "Active" else depth,
                                    position_group=pos_group,
                                    source="ESPN Depth Chart"
                                )
                                records.append(record)
        
        except Exception as e:
            logger.error(f"Error parsing depth table: {e}")
        
        return records
    
    def _parse_depth_section(self, section, team_info: Dict) -> List[PlayerRecord]:
        """Parse alternative depth chart structures"""
        records = []
        
        try:
            # Look for position headers followed by player lists
            headers = section.find_all(['h3', 'h4', 'strong'])
            
            for header in headers:
                pos_text = header.get_text(strip=True)
                match = re.match(r'^([A-Z]{1,3})', pos_text)
                
                if match:
                    position = match.group(1)
                    pos_group = POSITION_GROUPS.get(position, "Unknown")
                    
                    # Find player list after header
                    sibling = header.find_next_sibling()
                    if sibling:
                        players = sibling.find_all(['li', 'div', 'span'])
                        for idx, player_elem in enumerate(players):
                            player_text = player_elem.get_text(strip=True)
                            name, status = self._parse_player_text(player_text)
                            
                            if name:
                                depth = DEPTH_MAP[idx] if idx < len(DEPTH_MAP) else "Backup"
                                record = PlayerRecord(
                                    player_name=name,
                                    team_name=team_info['name'],
                                    team_abbr=team_info['abbr'],
                                    position=position,
                                    depth_or_status=f"{depth} - {status}" if status != "Active" else depth,
                                    position_group=pos_group,
                                    source="ESPN Depth Chart"
                                )
                                records.append(record)
        
        except Exception as e:
            logger.error(f"Error parsing depth section: {e}")
        
        return records
    
    def fetch_roster_api_espn(self, team_slug: str, team_info: Dict) -> List[PlayerRecord]:
        """
        Fetch roster from ESPN API endpoint (fallback)
        URL: https://site.api.espn.com/apis/site/v2/sports/football/nfl/teams/{team_id}/roster
        """
        records = []
        team_id = team_info['team_id']
        url = f"https://site.api.espn.com/apis/site/v2/sports/football/nfl/teams/{team_id}/roster"
        
        try:
            logger.info(f"Fetching ESPN Roster API for {team_info['name']} (team_id={team_id})")
            resp = self.session.get(url, timeout=20)
            resp.raise_for_status()
            
            data = resp.json()
            
            # Parse roster data
            if 'athletes' in data:
                for athlete_group in data['athletes']:
                    position = athlete_group.get('position', 'UNK')
                    items = athlete_group.get('items', [])
                    
                    for idx, athlete in enumerate(items):
                        name = athlete.get('fullName', athlete.get('displayName', 'Unknown'))
                        jersey = athlete.get('jersey', '')
                        
                        # Check injury status
                        status = "Active"
                        if 'status' in athlete:
                            status_type = athlete['status'].get('type', '')
                            if status_type:
                                status = status_type
                        
                        # Determine depth
                        depth = DEPTH_MAP[idx] if idx < len(DEPTH_MAP) else "Backup"
                        pos_group = POSITION_GROUPS.get(position, "Unknown")
                        
                        record = PlayerRecord(
                            player_name=name,
                            team_name=team_info['name'],
                            team_abbr=team_info['abbr'],
                            position=position,
                            depth_or_status=f"{depth} - {status}" if status != "Active" else depth,
                            position_group=pos_group,
                            jersey_number=jersey,
                            source="ESPN Roster API"
                        )
                        records.append(record)
            
            logger.info(f"Fetched {len(records)} players from ESPN Roster API for {team_info['abbr']}")
            
        except Exception as e:
            logger.error(f"Error fetching ESPN Roster API for {team_slug}: {e}")
        
        return records
    
    def _parse_player_text(self, text: str) -> Tuple[str, str]:
        """
        Parse player text to extract name and injury status
        Examples:
        - "Tom Brady" -> ("Tom Brady", "Active")
        - "Mike Evans (Q)" -> ("Mike Evans", "Q")
        - "Rob Gronkowski (Out)" -> ("Rob Gronkowski", "Out")
        """
        text = text.strip()
        
        # Pattern: Name (Status)
        match = re.match(r'^(.+?)\s*\(([^)]+)\)\s*$', text)
        if match:
            name = match.group(1).strip()
            status = match.group(2).strip()
            return name, status
        
        # Pattern: Name - Status
        match = re.match(r'^(.+?)\s*[-–—]\s*([A-Z]+)$', text)
        if match:
            return match.group(1).strip(), match.group(2).strip()
        
        # Check for trailing single-letter status codes
        parts = text.rsplit(' ', 1)
        if len(parts) == 2 and parts[1] in ('Q', 'O', 'D', 'IR', 'PUP', 'SUS'):
            return parts[0].strip(), parts[1].strip()
        
        # Default: healthy player
        return text, "Active"
    
    def process_team(self, team_slug: str) -> int:
        """
        Process a single team using both depth chart scraping and roster API
        Returns number of players added
        """
        if team_slug not in ESPN_TEAMS:
            logger.warning(f"Unknown team slug: {team_slug}")
            return 0
        
        team_info = ESPN_TEAMS[team_slug]
        logger.info(f"Processing team: {team_info['name']} ({team_info['abbr']})")
        
        # Try depth chart scraping first
        depth_records = self.fetch_depth_chart_espn(team_slug, team_info)
        
        # Fallback to roster API
        api_records = self.fetch_roster_api_espn(team_slug, team_info)
        
        # Merge both sources
        merged = self.merge_roster(depth_records, api_records)
        
        self.players.extend(merged)
        logger.info(f"Added {len(merged)} players for {team_info['abbr']} (after deduplication)")
        
        return len(merged)
    
    def merge_roster(self, depth_records: List[PlayerRecord], 
                     api_records: List[PlayerRecord]) -> List[PlayerRecord]:
        """
        Merge two roster sources with deduplication
        
        Priority: Depth chart data takes precedence over API data
        Deduplication: Based on player name + team + position
        """
        merged = {}
        
        # First, add all depth chart records (higher priority)
        for record in depth_records:
            key = record.get_key()
            merged[key] = record
        
        # Then add API records only if not already present
        for record in api_records:
            key = record.get_key()
            if key not in merged:
                merged[key] = record
        
        result = list(merged.values())
        
        # Log merge statistics
        logger.info(f"Merge stats: {len(depth_records)} depth + {len(api_records)} API = {len(result)} unique")
        
        return result
    
    def process_all_teams(self) -> None:
        """Process all 32 NFL teams"""
        logger.info("Starting processing of all 32 NFL teams")
        
        total_players = 0
        for team_slug in sorted(ESPN_TEAMS.keys()):
            try:
                count = self.process_team(team_slug)
                total_players += count
                # Rate limiting
                time.sleep(1)
            except Exception as e:
                logger.error(f"Error processing team {team_slug}: {e}")
        
        logger.info(f"Completed processing all teams. Total players: {total_players}")
    
    def to_dataframe(self) -> pd.DataFrame:
        """
        Convert collected players to validated DataFrame
        
        Key columns: [Player Name | Team Name | Depth or Status]
        """
        if not self.players:
            logger.warning("No players to convert to DataFrame")
            return pd.DataFrame()
        
        # Convert to list of dicts
        data = [player.to_dict() for player in self.players]
        
        # Create DataFrame
        df = pd.DataFrame(data)
        
        # Ensure required columns
        required_cols = ['Player Name', 'Team Name', 'Depth or Status']
        for col in required_cols:
            if col not in df.columns:
                df[col] = ''
        
        # Sort by team and position for readability
        df = df.sort_values(['Team Abbr', 'Position Group', 'Position', 'Player Name'])
        
        # Reset index
        df = df.reset_index(drop=True)
        
        logger.info(f"Created DataFrame with {len(df)} rows and {len(df.columns)} columns")
        
        return df
    
    def save_to_csv(self, filename: str = 'nfl_rosters.csv') -> None:
        """Save roster data to CSV file"""
        df = self.to_dataframe()
        df.to_csv(filename, index=False)
        logger.info(f"Saved {len(df)} player records to {filename}")
    
    def get_statistics(self) -> Dict:
        """Return statistics about collected data"""
        if not self.players:
            return {}
        
        df = self.to_dataframe()
        
        stats = {
            'total_players': len(self.players),
            'total_teams': df['Team Abbr'].nunique(),
            'players_per_team': df.groupby('Team Abbr').size().to_dict(),
            'positions': df['Position'].value_counts().to_dict(),
            'position_groups': df['Position Group'].value_counts().to_dict(),
            'sources': df['Source'].value_counts().to_dict(),
        }
        
        return stats


def main():
    """Main execution function"""
    logger.info("="*60)
    logger.info("NFL Roster Builder - Enhanced Version")
    logger.info("="*60)
    
    builder = NFLRosterBuilder()
    
    # Process all 32 teams
    builder.process_all_teams()
    
    # Get statistics
    stats = builder.get_statistics()
    logger.info("\n" + "="*60)
    logger.info("FINAL STATISTICS")
    logger.info("="*60)
    logger.info(f"Total Players: {stats.get('total_players', 0)}")
    logger.info(f"Total Teams: {stats.get('total_teams', 0)}")
    logger.info(f"Target Met: {'YES' if stats.get('total_players', 0) >= 2553 else 'NO'}")
    
    # Show players per team
    if 'players_per_team' in stats:
        logger.info("\nPlayers per team:")
        for team, count in sorted(stats['players_per_team'].items()):
            logger.info(f"  {team}: {count}")
    
    # Show sources breakdown
    if 'sources' in stats:
        logger.info("\nData sources:")
        for source, count in stats['sources'].items():
            logger.info(f"  {source}: {count}")
    
    # Save to CSV
    builder.save_to_csv('nfl_rosters.csv')
    
    # Display sample data
    df = builder.to_dataframe()
    logger.info("\n" + "="*60)
    logger.info("SAMPLE DATA (first 10 rows)")
    logger.info("="*60)
    print(df.head(10).to_string())
    
    logger.info("\n" + "="*60)
    logger.info("Processing Complete!")
    logger.info("="*60)


if __name__ == "__main__":
    main()
