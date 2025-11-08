#!/usr/bin/env python3
"""
Simple starter script to fetch a team's depth chart or injury page.
Replace the placeholder URL and parsing logic with the target site structure.
"""
import argparse
import logging
import sys

import requests
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def fetch_team_page(team: str, season: int = None) -> str:
    # Placeholder URL — update per source (nfl.com, pro-football-reference, etc.)
    url = f"https://www.nfl.com/players/team/{team}/depth-chart"
    logger.info("GET %s", url)
    resp = requests.get(url, timeout=15)
    resp.raise_for_status()
    return resp.text


def parse_depth_chart(html: str):
    soup = BeautifulSoup(html, "html.parser")
    # TODO: implement robust selectors and fallback parsing
    players = []
    for row in soup.select("table tr"):
        cols = [c.get_text(strip=True) for c in row.find_all("td")]
        if cols:
            players.append(cols)
    return players


def main(argv):
    p = argparse.ArgumentParser(description="Fetch depth chart for a team")
    p.add_argument("--team", required=True, help="Team code (e.g., NE, KC)")
    p.add_argument("--season", type=int, default=None)
    args = p.parse_args(argv)

    html = fetch_team_page(args.team, args.season)
    data = parse_depth_chart(html)
    logger.info("Parsed %d rows", len(data))
    for r in data[:20]:
        print(r)


if __name__ == "__main__":
    main(sys.argv[1:])