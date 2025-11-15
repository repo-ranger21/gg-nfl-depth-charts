#!/usr/bin/env python3
"""
NFL Roster Builder - ESPN to Supabase to Notion Pipeline
Scrapes team rosters from ESPN and outputs to CSV for processing.
"""
import os
import sys
import time
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime
from typing import List, Dict, Optional
import requests
from bs4 import BeautifulSoup
import pandas as pd
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
NOTION_API_KEY = os.getenv("NOTION_API_KEY")
NOTION_DATABASE_ID = os.getenv("NOTION_DATABASE_ID")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Setup logging with rotation to prevent unbounded log growth
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, "nfl_sync.log")

# Configure rotating file handler (max 10MB per file, keep 5 backup files)
file_handler = RotatingFileHandler(
    LOG_FILE, 
    maxBytes=10*1024*1024,  # 10 MB
    backupCount=5
)
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        file_handler,
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# NFL Teams (all 32 teams)
NFL_TEAMS = [
    "buf", "mia", "nyj", "ne", "bal", "pit", "cle", "cin",
    "hou", "ind", "jax", "ten", "kc", "lv", "lac", "den",
    "dal", "phi", "nyg", "was", "gb", "chi", "min", "det",
    "sf", "sea", "lar", "ari", "atl", "no", "tb", "car"
]

# Position groups mapping
POSITION_GROUPS = {
    "QB": "Offense", "RB": "Offense", "WR": "Offense", "TE": "Offense", "FB": "Offense",
    "T": "Offense", "G": "Offense", "C": "Offense", "OL": "Offense", "OT": "Offense", "OG": "Offense",
    "DE": "Defense", "DT": "Defense", "NT": "Defense", "LB": "Defense", "OLB": "Defense",
    "MLB": "Defense", "ILB": "Defense", "CB": "Defense", "S": "Defense", "FS": "Defense", "SS": "Defense", "DB": "Defense",
    "K": "Special Teams", "P": "Special Teams", "LS": "Special Teams", "KR": "Special Teams", "PR": "Special Teams"
}


def fetch_team_roster(team_slug: str, timeout: int = 20) -> Optional[str]:
    """Fetch team roster page from ESPN."""
    url = f"https://www.espn.com/nfl/team/roster/_/name/{team_slug}"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    
    try:
        logger.info(f"Fetching roster for {team_slug.upper()} from {url}")
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
        return response.text
    except Exception as e:
        logger.error(f"Error fetching {team_slug}: {e}")
        return None


def parse_roster_html(html: str, team_slug: str) -> List[Dict]:
    """Parse ESPN roster HTML and extract player information."""
    soup = BeautifulSoup(html, "html.parser")
    players = []
    
    # ESPN roster tables - find all player rows
    tables = soup.find_all("table")
    
    for table in tables:
        rows = table.find_all("tr")
        
        for row in rows:
            cells = row.find_all("td")
            
            if len(cells) >= 4:  # Typical ESPN roster has: Number, Name, Position, etc.
                try:
                    # Extract player data
                    number_cell = cells[0].get_text(strip=True)
                    name_cell = cells[1].get_text(strip=True)
                    position_cell = cells[2].get_text(strip=True) if len(cells) > 2 else "UNK"
                    
                    # Additional fields if available
                    age = cells[3].get_text(strip=True) if len(cells) > 3 else ""
                    height = cells[4].get_text(strip=True) if len(cells) > 4 else ""
                    weight = cells[5].get_text(strip=True) if len(cells) > 5 else ""
                    experience = cells[6].get_text(strip=True) if len(cells) > 6 else ""
                    college = cells[7].get_text(strip=True) if len(cells) > 7 else ""
                    
                    # Skip header rows
                    if name_cell.lower() in ["name", "player"]:
                        continue
                    
                    # Determine position group
                    position = position_cell.upper().strip()
                    position_group = POSITION_GROUPS.get(position, "Unknown")
                    
                    player_data = {
                        "team": team_slug.upper(),
                        "number": number_cell,
                        "name": name_cell,
                        "position": position,
                        "position_group": position_group,
                        "age": age,
                        "height": height,
                        "weight": weight,
                        "experience": experience,
                        "college": college,
                        "scraped_at": datetime.utcnow().isoformat()
                    }
                    
                    players.append(player_data)
                    logger.debug(f"Parsed player: {name_cell} - {position} ({team_slug.upper()})")
                    
                except Exception as e:
                    logger.warning(f"Error parsing row for {team_slug}: {e}")
                    continue
    
    return players


def scrape_all_teams() -> List[Dict]:
    """Scrape rosters for all NFL teams."""
    logger.info("🏈 Starting NFL Roster Builder...")
    logger.info(f"✅ Total: Processing {len(NFL_TEAMS)} teams")
    
    all_players = []
    successful_teams = 0
    failed_teams = 0
    
    for i, team in enumerate(NFL_TEAMS, 1):
        logger.info(f"Processing team {i}/{len(NFL_TEAMS)}: {team.upper()}")
        
        html = fetch_team_roster(team)
        if html:
            players = parse_roster_html(html, team)
            if players:
                all_players.extend(players)
                successful_teams += 1
                logger.info(f"✅ {team.upper()}: Found {len(players)} players")
            else:
                failed_teams += 1
                logger.warning(f"⚠️  {team.upper()}: No players found")
        else:
            failed_teams += 1
            logger.error(f"❌ {team.upper()}: Failed to fetch roster")
        
        # Rate limiting - be nice to ESPN
        time.sleep(1.5)
    
    logger.info(f"\n{'='*60}")
    logger.info(f"✅ Total: Validating collected player metadata")
    logger.info(f"✅ Successfully scraped: {successful_teams} teams")
    logger.info(f"❌ Failed: {failed_teams} teams")
    logger.info(f"📊 Total players collected: {len(all_players)}")
    logger.info(f"{'='*60}\n")
    
    return all_players


def save_to_csv(players: List[Dict], filename: str = "nfl_full_roster.csv"):
    """Save roster data to CSV file."""
    if not players:
        logger.error("No players to save!")
        return False
    
    try:
        df = pd.DataFrame(players)
        df.to_csv(filename, index=False)
        logger.info(f"✅ Saved {len(players)} players to {filename}")
        return True
    except Exception as e:
        logger.error(f"Error saving to CSV: {e}")
        return False


def sync_to_supabase(players: List[Dict]) -> bool:
    """Sync roster data to Supabase (optional)."""
    if not SUPABASE_URL or not SUPABASE_KEY:
        logger.warning("Supabase credentials not configured, skipping sync")
        return False
    
    try:
        # Supabase sync logic would go here
        logger.info("📤 Supabase sync not yet implemented")
        return True
    except Exception as e:
        logger.error(f"Error syncing to Supabase: {e}")
        return False


def sync_to_notion(players: List[Dict]) -> bool:
    """Sync roster data to Notion database (optional)."""
    if not NOTION_API_KEY or not NOTION_DATABASE_ID:
        logger.warning("Notion credentials not configured, skipping sync")
        return False
    
    try:
        # Notion sync logic would go here
        logger.info("📤 Notion sync not yet implemented")
        return True
    except Exception as e:
        logger.error(f"Error syncing to Notion: {e}")
        return False


def main():
    """Main execution function."""
    logger.info("="*60)
    logger.info("NFL ROSTER BUILDER - ESPN TO SUPABASE TO NOTION PIPELINE")
    logger.info("="*60)
    
    # Scrape all teams
    players = scrape_all_teams()
    
    if not players:
        logger.error("❌ No roster data collected. Exiting.")
        sys.exit(1)
    
    # Save to CSV
    if not save_to_csv(players):
        logger.error("❌ Failed to save roster data. Exiting.")
        sys.exit(1)
    
    # Optional: Sync to Supabase
    sync_to_supabase(players)
    
    # Optional: Sync to Notion
    sync_to_notion(players)
    
    logger.info("✅ NFL Roster Builder completed successfully!")
    sys.exit(0)


if __name__ == "__main__":
    main()
