#!/usr/bin/env python3
"""
Guerillagenics NFL Depth Chart Scraper

- Scrapes ESPN depth charts for 32 teams (skips BUF and MIA)
- Parses position, depth (Starter/2nd/3rd/4th), player name, injury status
- Maps positions to position groups (Offense/Defense/Special Teams)
- Creates pages in Notion database (DATA_SOURCE_ID)
- Logs progress and writes summary to sync-log.txt
"""
from __future__ import annotations

import os
import re
import sys
import time
import json
import logging
from datetime import datetime
from typing import List, Tuple, Optional

import requests
from bs4 import BeautifulSoup

# Configuration
NOTION_API_KEY = os.getenv("NOTION_API_KEY")
DATA_SOURCE_ID = "2df99f74-45c0-40e2-8392-e497dacd0dd7"
NOTION_API_URL = "https://api.notion.com/v1/pages"
NOTION_HEADERS = {
    "Authorization": f"Bearer {NOTION_API_KEY}" if NOTION_API_KEY else "",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28",
}

LOGFILE = "sync-log.txt"
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger("nfl_depth_scraper")

# ESPN team slugs / abbreviations to try. BUF and MIA intentionally excluded.
NFL_TEAMS = [
    "nyj", "ne", "bal", "pit", "cle", "cin",
    "hou", "ind", "jax", "ten", "kc", "lv", "lac", "den",
    "dal", "phi", "nyg", "was", "gb", "chi", "min", "det",
    "sf", "sea", "lar", "ari", "atl", "no", "tb", "car"
]

# map common position abbreviations to groups
POSITION_GROUPS = {
    "QB": "Offense", "RB": "Offense", "WR": "Offense", "TE": "Offense", "FB": "Offense",
    "LT": "Offense", "LG": "Offense", "C": "Offense", "RG": "Offense", "RT": "Offense",
    "DE": "Defense", "DT": "Defense", "NT": "Defense", "LB": "Defense", "OLB": "Defense",
    "MLB": "Defense", "CB": "Defense", "S": "Defense", "FS": "Defense", "SS": "Defense",
    "PK": "Special Teams", "P": "Special Teams", "H": "Special Teams",
    "PR": "Special Teams", "KR": "Special Teams", "LS": "Special Teams"
}

DEPTH_MAP = ["Starter", "2nd", "3rd", "4th"]

# ESPN URL patterns to try (some teams have slug, some accept abbrev)
ESPN_URL_PATTERNS = [
    "https://www.espn.com/nfl/team/depth/_/name/{team}",  # common pattern
    "https://www.espn.com/nfl/team/depth/_/name/{team}/",  # trailing slash
    # fallback: team roster/depth page by abbreviation (less reliable)
    "https://www.espn.com/nfl/team/roster/_/name/{team}"
]


def append_log(line: str) -> None:
    now = datetime.utcnow().isoformat()
    entry = f"{now} - {line}"
    logger.info(entry)
    with open(LOGFILE, "a", encoding="utf-8") as fh:
        fh.write(entry + "\n")


def fetch_page(url: str, timeout: int = 20) -> Optional[str]:
    try:
        resp = requests.get(url, timeout=timeout, headers={"User-Agent": "gorillagenics-bot/1.0"})
        resp.raise_for_status()
        return resp.text
    except Exception as e:
        append_log(f"ERROR fetching {url} -> {e}")
        return None


def parse_player_injury(raw: str) -> Tuple[str, str]:
    """
    Extract player name and injury status from a raw text token.
    Examples handled:
      - "Tom Brady" -> ("Tom Brady", "Healthy")
      - "Mike Evans (Q)" -> ("Mike Evans", "Q")
      - "Xavier (Questionable)" -> ("Xavier", "Questionable")
    """
    text = raw.strip()
    # common parentheses patterns
    m = re.match(r"^(?P<name>.+?)\s*\((?P<stat>[^)]+)\)\s*$", text)
    if m:
        name = m.group("name").strip()
        status = m.group("stat").strip()
        return name, status
    # trailing token like " (Q)" was handled; check trailing single token
    m2 = re.match(r"^(?P<name>.+?)\s+[-–—:]\s*(?P<stat>[A-Za-z0-9%]+)$", text)
    if m2:
        return m2.group("name").strip(), m2.group("stat").strip()
    # tokens like "John Doe Q" or ending single-letter statuses
    parts = text.rsplit(" ", 1)
    if len(parts) == 2 and re.fullmatch(r"(Q|O|IR|PUP|SUS|D|Questionable|Out|Probable|Doubtful|GT|Illness)", parts[1], flags=re.I):
        return parts[0].strip(), parts[1].strip()
    # default: healthy / unknown
    return text, "Healthy"


def find_depth_sections(soup: BeautifulSoup) -> List[Tuple[str, List[str]]]:
    """
    Very forgiving: find sections that look like position groups and list players under them.
    Return list of (position_label, list_of_player_texts).
    """
    sections = []
    # ESPN often uses headers with position names and unordered lists or tables
    for header in soup.find_all(["h2", "h3", "h4"]):
        pos = header.get_text(strip=True)
        if not pos or len(pos) > 8:  # skip long, non-position headers
            continue
        # look for next sibling lists or tables
        sibling = header.find_next_sibling()
        players = []
        if sibling:
            # list items
            for li in sibling.select("li"):
                t = li.get_text(" ", strip=True)
                if t:
                    players.append(t)
            # table rows
            if not players:
                for row in sibling.select("tr"):
                    t = " ".join([c.get_text(" ", strip=True) for c in row.find_all(["td", "th"])])
                    if t:
                        players.append(t)
        if players:
            sections.append((pos, players))
    # Fallback: find any table with 'depth' like content
    if not sections:
        for tbl in soup.select("table"):
            headers = [th.get_text(" ", strip=True) for th in tbl.select("th")]
            if any(h and re.search(r"position|depth|player", h, flags=re.I) for h in headers):
                for row in tbl.select("tr"):
                    cells = [c.get_text(" ", strip=True) for c in row.find_all("td")]
                    if cells:
                        # try first cell as position or player; append under a generic 'UNK'
                        sections.append(("UNK", [" | ".join(cells)]))
    return sections


def map_position_to_group(pos_abbrev: str) -> str:
    pos = pos_abbrev.upper().strip()
    # sometimes position strings include depth indicators or slashes: "WR/TE"
    pos = pos.split("/")[0]
    return POSITION_GROUPS.get(pos, "Offense" if pos in ("QB", "RB", "WR", "TE", "FB", "LT", "LG", "C", "RG", "RT") else "Defense")


def create_notion_page(entry_name: str, team: str, position: str, depth: str,
                       pos_group: str, injury_status: str, notes: str = "") -> Tuple[bool, Optional[str]]:
    if not NOTION_API_KEY:
        return False, "Missing NOTION_API_KEY"

    payload = {
        "parent": {"database_id": DATA_SOURCE_ID},
        "properties": {
            "Entry Name": {"title": [{"text": {"content": entry_name}}]},
            "Team": {"select": {"name": team.upper()}},
            "Position": {"select": {"name": position}},
            "Depth": {"select": {"name": depth}},
            "Position Group": {"select": {"name": pos_group}},
            "Injury Status": {"select": {"name": injury_status}},
            "Notes": {"rich_text": [{"text": {"content": notes}}]},
            "Last Updated": {"date": {"start": datetime.utcnow().isoformat()}}
        }
    }
    try:
        resp = requests.post(NOTION_API_URL, headers=NOTION_HEADERS, json=payload, timeout=30)
        if resp.status_code in (200, 201):
            return True, None
        else:
            return False, f"Notion API {resp.status_code}: {resp.text}"
    except Exception as e:
        return False, str(e)


def process_team(team_slug: str) -> Tuple[int, int]:
    """
    Fetches ESPN depth for a team, parses entries, writes to Notion.
    Returns (created_count, failed_count)
    """
    append_log(f"Starting team {team_slug}")
    created = 0
    failed = 0
    page_html = None
    for pattern in ESPN_URL_PATTERNS:
        url = pattern.format(team=team_slug)
        append_log(f"Trying URL: {url}")
        page_html = fetch_page(url)
        if page_html:
            append_log(f"Fetched page for {team_slug} from {url}")
            break
        time.sleep(1)
    if not page_html:
        append_log(f"ERROR: Could not fetch page for {team_slug}")
        return created, len([])  # nothing to create

    soup = BeautifulSoup(page_html, "html.parser")
    sections = find_depth_sections(soup)
    append_log(f"Found {len(sections)} potential sections for {team_slug}")

    for pos_label, player_texts in sections:
        # try to normalize position label to a common abbrev (first token)
        pos = pos_label.split()[0].upper()
        pos_group = map_position_to_group(pos)
        # Each player_text might include depth markers separated by commas or pipes
        for idx, raw in enumerate(player_texts):
            # attempt to split if multiple players are in a single string
            # common separators: ',', '•', '|'
            candidates = re.split(r'\s*[,\|•]\s*', raw)
            for c_i, cand in enumerate(candidates):
                name, injury = parse_player_injury(cand)
                # depth inference: idx or candidate position
                depth_label = DEPTH_MAP[c_i] if c_i < len(DEPTH_MAP) else DEPTH_MAP[-1]
                entry_name = f"{name} — {team_slug.upper()} — {pos}"
                notes = f"Source: ESPN ({team_slug}), raw: {cand}"
                ok, err = create_notion_page(entry_name, team_slug, pos, depth_label, pos_group, injury, notes)
                if ok:
                    created += 1
                    append_log(f"CREATED: {entry_name} [{depth_label}] ({injury})")
                else:
                    failed += 1
                    append_log(f"FAILED: {entry_name} -> {err}")
                # gentle rate limit
                time.sleep(0.25)
    append_log(f"Completed team {team_slug}: created={created}, failed={failed}")
    return created, failed


def main(argv: List[str]) -> int:
    append_log("=== NFL Depth Chart Sync started ===")
    total_created = 0
    total_failed = 0
    for team in NFL_TEAMS:
        try:
            c, f = process_team(team)
            total_created += c
            total_failed += f
        except Exception as e:
            append_log(f"Unhandled error for team {team}: {e}")
    append_log(f"=== Sync complete: total_created={total_created}, total_failed={total_failed} ===")
    return 0 if total_failed == 0 else 2


if __name__ == "__main__":
    exit_code = main(sys.argv[1:])
    sys.exit(exit_code)