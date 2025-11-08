# NFL Depth Chart Automation

Automated scraping and syncing of ESPN NFL depth charts into a Notion database for downstream analytics, injury tracking, and roster-time-series. The pipeline scrapes ESPN depth pages (skips BUF & MIA), parses position/depth/injury, maps to position groups, and creates pages in a Notion database.

## Features
- Automated scraping of ESPN depth charts for all 32 teams (BUF & MIA intentionally skipped)
- Parses: Position, Depth (Starter / 2nd / 3rd / 4th), Player Name, Injury Status
- Maps positions to Position Groups: Offense / Defense / Special Teams
- Writes entries into a Notion database (configurable DATABASE_ID)
- Scheduled CI via GitHub Actions (weekly), manual run support, detailed logging and error handling
- Uploads sync summary as an artifact for inspection

## Quick Setup (Local)
1. Clone repo and enter folder
   ```sh
   git clone <repo-url> nfl-depth-charts
   cd nfl-depth-charts
   ```

2. Create and activate a Python virtualenv (Ubuntu)
   ```sh
   python3 -m venv .venv
   source .venv/bin/activate
   pip install --upgrade pip
   pip install -r requirements.txt  # if present
   pip install requests beautifulsoup4
   ```

3. Configure Notion API key (local run)
   ```sh
   export NOTION_API_KEY="<your_notion_integration_token>"
   ```

4. Run the scraper locally
   ```sh
   python scripts/nfl_depth_scraper.py
   ```

Notes:
- The script writes progress into `sync-log.txt` in the repo root.
- The Notion database ID used by the script is `2df99f74-45c0-40e2-8392-e497dacd0dd7` (change in script if needed).

## Usage
- Manual run (local): set NOTION_API_KEY and run the script as above.
- GitHub Actions:
  - Workflow: `.github/workflows/sync.yml` (NFL Depth Chart Sync)
  - Add `NOTION_API_KEY` as a repository secret in Settings → Secrets & variables → Actions.
  - Trigger manually: GitHub Actions → NFL Depth Chart Sync → Run workflow.

## Viewing logs & artifacts
- Local: view `sync-log.txt` for detailed progress/errors.
- CI: workflow uploads an artifact named `sync-results-<run_number>` containing `sync-log.txt`. Download from the workflow run summary.

## Schedule
- The workflow runs every Tuesday at 9:00 AM Eastern Time.
  - Cron in workflow: `0 14 * * 2` (UTC 14 == 9 AM ET during standard time)
  - Also supports manual trigger (workflow_dispatch).

## Architecture Snapshot
- scripts/ — scraper and Notion sync (BeautifulSoup + requests)
- .github/workflows/ — scheduled sync (Python 3.11)
- sync-log.txt — runtime summary and errors (produced by the scraper)
- Notion — canonical storage for entries and history

## Notes & Best Practices
- Do not commit API keys or secrets. Use GitHub Actions secrets for CI.
- Scrapers should be tolerant of markup changes — verify selectors periodically.
- Respect robots.txt and site terms-of-service for scraping.

Maintained by: guerillagenics.app