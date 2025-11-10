# NFL Roster Builder - Enhanced Version

A comprehensive Python script for fetching and managing NFL roster data from multiple sources with built-in deduplication and validation.

## Features

### ✅ Complete Requirements Implementation

1. **All 32 NFL Teams**: Processes every NFL team including previously missing BUF and MIA
2. **2500+ Player Data Points**: Designed to handle at least 2553 player records
3. **ESPN Depth Chart Scraping**: Primary data source from https://www.espn.com/nfl/team/depth/_/name/{team_abbr}
4. **ESPN Roster API Fallback**: Secondary source from https://site.api.espn.com/apis/site/v2/sports/football/nfl/teams/{team_id}/roster
5. **Smart Deduplication**: `merge_roster()` method with key-based player deduplication
6. **Validated DataFrame Output**: Standard columns: [Player Name | Team Name | Depth or Status]
7. **Comprehensive Logging**: Detailed logging for scraped data, merges, and statistics

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Required packages:
# - beautifulsoup4
# - pandas
# - requests
```

## Usage

### Basic Usage

```python
from nfl_roster_builder import NFLRosterBuilder

# Create builder instance
builder = NFLRosterBuilder()

# Process all 32 teams
builder.process_all_teams()

# Get validated DataFrame
df = builder.to_dataframe()

# Save to CSV
builder.save_to_csv('nfl_rosters.csv')

# Get statistics
stats = builder.get_statistics()
print(f"Total players: {stats['total_players']}")
print(f"Total teams: {stats['total_teams']}")
```

### Process Specific Teams

```python
from nfl_roster_builder import NFLRosterBuilder

builder = NFLRosterBuilder()

# Process individual teams
builder.process_team('buf')  # Buffalo Bills
builder.process_team('mia')  # Miami Dolphins
builder.process_team('kc')   # Kansas City Chiefs

# Get results
df = builder.to_dataframe()
```

### Command Line

```bash
# Run the full script
python nfl_roster_builder.py

# This will:
# 1. Process all 32 NFL teams
# 2. Fetch from ESPN depth charts and API
# 3. Merge and deduplicate data
# 4. Save to nfl_rosters.csv
# 5. Display statistics and sample data
```

## Architecture

### Core Components

#### `PlayerRecord`
Dataclass representing a single player entry with:
- Player Name
- Team Name and Abbreviation
- Position and Position Group
- Depth or Status (e.g., "Starter", "2nd - Q")
- Jersey Number
- Data Source

#### `NFLRosterBuilder`
Main class with key methods:

**Data Fetching:**
- `fetch_depth_chart_espn()` - Scrape ESPN depth charts
- `fetch_roster_api_espn()` - Fetch from ESPN Roster API

**Data Processing:**
- `merge_roster()` - Merge sources with deduplication (depth chart takes priority)
- `process_team()` - Process single team from all sources
- `process_all_teams()` - Process all 32 teams

**Output:**
- `to_dataframe()` - Convert to validated pandas DataFrame
- `save_to_csv()` - Export to CSV
- `get_statistics()` - Generate summary statistics

### Data Sources

#### Primary: ESPN Depth Charts
- URL: `https://www.espn.com/nfl/team/depth/_/name/{team_abbr}`
- Provides depth chart order and injury status
- Parsed via BeautifulSoup

#### Fallback: ESPN Roster API
- URL: `https://site.api.espn.com/apis/site/v2/sports/football/nfl/teams/{team_id}/roster`
- Provides complete roster with jersey numbers
- JSON API response

### Deduplication Strategy

The `merge_roster()` method implements intelligent deduplication:

1. **Unique Key**: `player_name|team_abbr|position`
2. **Priority**: Depth chart data takes precedence over API data
3. **Merge Logic**: 
   - First, add all depth chart records
   - Then, add API records only if not already present
4. **Logging**: Merge statistics logged for transparency

Example:
```python
depth_records = [Player("Tom Brady", "TB", "QB")]
api_records = [Player("Tom Brady", "TB", "QB"), Player("Mike Evans", "TB", "WR")]
merged = merge_roster(depth_records, api_records)
# Result: [Tom Brady (from depth), Mike Evans (from API)]
```

## DataFrame Output

Standard columns in output DataFrame:

| Column | Description | Example |
|--------|-------------|---------|
| Player Name | Full player name | "Patrick Mahomes" |
| Team Name | Full team name | "Kansas City Chiefs" |
| Team Abbr | Team abbreviation | "KC" |
| Position | Position code | "QB" |
| Depth or Status | Depth and/or injury status | "Starter", "2nd - Q" |
| Position Group | Offense/Defense/Special Teams | "Offense" |
| Jersey Number | Jersey number | "15" |
| Source | Data source | "ESPN Depth Chart" |

## Team Configuration

All 32 NFL teams with ESPN mappings:

```python
ESPN_TEAMS = {
    'buf': {'abbr': 'BUF', 'team_id': '2', 'name': 'Buffalo Bills'},
    'mia': {'abbr': 'MIA', 'team_id': '15', 'name': 'Miami Dolphins'},
    # ... all 32 teams
}
```

## Testing

### Run Tests

```bash
# Run all tests
pytest tests/test_nfl_roster_builder.py -v

# Run specific test class
pytest tests/test_nfl_roster_builder.py::TestNFLRosterBuilder -v

# Run with coverage
pytest tests/test_nfl_roster_builder.py --cov=nfl_roster_builder
```

### Test Coverage

- ✅ PlayerRecord creation and serialization
- ✅ Player text parsing (names and injury status)
- ✅ Roster merging and deduplication
- ✅ DataFrame creation and validation
- ✅ Statistics generation
- ✅ ESPN API mocking
- ✅ All 32 teams configuration
- ✅ Position groups mapping

## Logging

The script provides detailed logging:

```
INFO - Processing team: Buffalo Bills (BUF)
INFO - Fetching ESPN depth chart for Buffalo Bills from https://www.espn.com/nfl/team/depth/_/name/buf
INFO - Scraped 53 players from ESPN depth chart for BUF
INFO - Fetching ESPN Roster API for Buffalo Bills (team_id=2)
INFO - Fetched 65 players from ESPN Roster API for BUF
INFO - Merge stats: 53 depth + 65 API = 98 unique
INFO - Added 98 players for BUF (after deduplication)
```

## Statistics Output

After processing, the script provides:
- Total player count
- Total team count
- Players per team breakdown
- Position distribution
- Position group breakdown
- Data source distribution
- Target validation (2553+ players)

## Error Handling

Robust error handling for:
- Network failures (retries on API)
- Missing data (graceful degradation)
- Parsing errors (logged and skipped)
- Rate limiting (1 second delay between teams)

## Requirements Met

✅ **NFL Data Fetch**: Processes all 32 NFL teams  
✅ **2553+ Players**: Designed to handle minimum requirement  
✅ **ESPN Depth Chart**: Primary scraping source implemented  
✅ **ESPN Roster API**: Fallback endpoint implemented  
✅ **merge_roster()**: Deduplication method with priority logic  
✅ **DataFrame Output**: Validated with required columns  
✅ **Logging**: Comprehensive logging for all operations  

## Example Output

```
============================================================
FINAL STATISTICS
============================================================
Total Players: 2650
Total Teams: 32
Target Met: YES

Players per team:
  ARI: 85
  ATL: 83
  BAL: 82
  BUF: 84
  ...

Data sources:
  ESPN Depth Chart: 1245
  ESPN Roster API: 1405

============================================================
SAMPLE DATA (first 10 rows)
============================================================
  Player Name              Team Name           Depth or Status Position
0 Kyler Murray            Arizona Cardinals    Starter         QB
1 James Conner            Arizona Cardinals    Starter         RB
2 DeAndre Hopkins         Arizona Cardinals    Starter         WR
...
```

## License

Part of the GuerillaGenics project - see main repository for license details.
