# NFL Depth Chart Compiler

A comprehensive Python program that automatically compiles complete 32-team NFL roster depth charts using ESPN's depth chart pages as the primary source, with backup API support for robustness.

## Features

- ✅ **Complete Coverage**: Scrapes all 32 NFL teams
- ✅ **Dual Source Strategy**: 
  - Primary: ESPN depth chart web pages
  - Backup: ESPN API endpoints
- ✅ **Player Validation**: Ensures all ~2553 players across NFL rosters are collected
- ✅ **Error Handling**: Robust retry logic with exponential backoff
- ✅ **Multiple Export Formats**: JSON and CSV output
- ✅ **Detailed Logging**: Progress tracking and error reporting
- ✅ **Position Mapping**: Automatic classification into Offense/Defense/Special Teams
- ✅ **Injury Status Tracking**: Parses and records player injury designations
- ✅ **Validation Reports**: Comprehensive data quality checks

## Installation

```bash
# Install dependencies
pip install requests beautifulsoup4

# Or install the full project
pip install -e .
```

## Usage

### Basic Usage

Compile depth charts for all 32 NFL teams:

```bash
python nfl_depth_chart_compiler.py
```

### Advanced Options

```bash
# Specify custom output directory
python nfl_depth_chart_compiler.py --output-dir my_depth_charts

# Export as both JSON and CSV
python nfl_depth_chart_compiler.py --export-json --export-csv

# Adjust retry attempts for unstable networks
python nfl_depth_chart_compiler.py --max-retries 5

# Validation only (no compilation)
python nfl_depth_chart_compiler.py --validate-only
```

### Command Line Arguments

- `--output-dir DIR`: Output directory for compiled data (default: `output`)
- `--max-retries N`: Maximum retries for failed requests (default: 3)
- `--export-json`: Export data as JSON (default if no format specified)
- `--export-csv`: Export data as CSV
- `--validate-only`: Only validate data without compilation

## Output Files

The compiler generates several output files in the specified output directory:

### 1. nfl_depth_chart.json
Complete depth chart data in JSON format with metadata:
```json
{
  "metadata": {
    "compiled_at": "2025-11-08T22:00:00.000000",
    "total_players": 2553,
    "unique_players": 2553,
    "teams_processed": 32,
    "compiler_version": "1.0.0"
  },
  "players": [
    {
      "name": "Patrick Mahomes",
      "team": "KC",
      "position": "QB",
      "depth": "1st",
      "position_group": "Offense",
      "injury_status": "Active",
      "source": "ESPN",
      "timestamp": "2025-11-08T22:00:00.000000"
    }
    // ... more players
  ]
}
```

### 2. nfl_depth_chart.csv
Depth chart data in CSV format for easy spreadsheet analysis.

### 3. validation_report.json
Data quality validation report:
```json
{
  "total_players": 2553,
  "unique_players": 2553,
  "teams_processed": 32,
  "teams_failed": 0,
  "expected_total": 2553,
  "meets_expectation": true,
  "players_by_team": {
    "KC": 53,
    "SF": 53,
    // ... more teams
  },
  "players_by_position_group": {
    "Offense": 1120,
    "Defense": 1280,
    "Special Teams": 153
  },
  "warnings": [],
  "errors": []
}
```

### 4. compilation_summary.txt
Human-readable text summary of the compilation:
```
================================================================================
NFL DEPTH CHART COMPILATION SUMMARY
================================================================================
Compilation Date: 2025-11-08 22:00:00 UTC

STATISTICS:
  Total Players: 2553
  Unique Players: 2553
  Teams Processed: 32/32
  Teams Failed: 0
  Expected Total: 2553

POSITION GROUP BREAKDOWN:
  Defense: 1280
  Offense: 1120
  Special Teams: 153
================================================================================
```

### 5. depth_chart_compilation.log
Detailed compilation log with timestamps and debugging information.

## Data Structure

Each player entry contains:

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Player's full name |
| `team` | string | Team abbreviation (e.g., "KC", "SF") |
| `position` | string | Position abbreviation (e.g., "QB", "RB", "WR") |
| `depth` | string | Depth chart position (e.g., "1st", "2nd", "3rd") |
| `position_group` | string | Group: "Offense", "Defense", or "Special Teams" |
| `injury_status` | string | Injury designation (e.g., "Active", "Q", "O", "IR") |
| `source` | string | Data source: "ESPN" or "ESPN_API" |
| `timestamp` | string | ISO 8601 timestamp of data collection |

## Position Mapping

The compiler automatically maps positions to position groups:

**Offense**: QB, RB, FB, WR, TE, LT, LG, C, RG, RT, OL, OT, G

**Defense**: DE, DT, NT, LB, OLB, MLB, ILB, CB, S, FS, SS, DB

**Special Teams**: K, P, LS, PR, KR

## Validation

The compiler performs comprehensive validation:

1. **Player Count Validation**: Ensures total players meet expected count (~2553)
2. **Team Validation**: Verifies all 32 teams were processed
3. **Per-Team Validation**: Checks each team has 53-90 players
4. **Data Quality Checks**: Validates required fields and formats

Validation results are saved to `validation_report.json` and logged.

## Error Handling

The compiler includes robust error handling:

- **Retry Logic**: Automatically retries failed requests with exponential backoff
- **Fallback Sources**: Falls back to API if web scraping fails
- **Graceful Degradation**: Continues processing other teams if one fails
- **Detailed Logging**: All errors are logged with context for debugging

## Testing

Run the test suite:

```bash
# Run all tests
pytest tests/test_depth_chart_compiler.py -v

# Run specific test
pytest tests/test_depth_chart_compiler.py::TestNFLDepthChartCompiler::test_scrape_espn_depth_chart -v

# Run with coverage
pytest tests/test_depth_chart_compiler.py --cov=nfl_depth_chart_compiler
```

## Integration

### Python Script Integration

```python
from nfl_depth_chart_compiler import NFLDepthChartCompiler

# Create compiler instance
compiler = NFLDepthChartCompiler(
    output_dir="my_depth_charts",
    max_retries=3
)

# Compile all teams
compiler.compile_all_teams()

# Validate data
validation = compiler.validate_data()

# Export data
compiler.export_json()
compiler.export_csv()

# Access player data
for player in compiler.players:
    print(f"{player['name']} - {player['team']} - {player['position']}")
```

### Processing Single Team

```python
compiler = NFLDepthChartCompiler()

# Process just one team
player_count = compiler.process_team("KC")
print(f"Found {player_count} players for Kansas City Chiefs")
```

## Architecture

### NFLDepthChartCompiler Class

Main compiler class with the following key methods:

- `compile_all_teams()`: Compiles depth charts for all 32 teams
- `process_team(team_abbr)`: Processes a single team
- `scrape_espn_depth_chart(team_abbr, espn_slug)`: Scrapes ESPN web pages
- `fetch_espn_api_backup(team_abbr, espn_slug)`: Fetches from ESPN API
- `validate_data()`: Validates compiled data
- `export_json(filename)`: Exports data to JSON
- `export_csv(filename)`: Exports data to CSV
- `generate_summary()`: Generates text summary

### Data Flow

```
1. Initialize Compiler
   └─> Create output directory
   └─> Set up logging

2. For Each NFL Team (32 teams)
   ├─> Try ESPN Web Scraping
   │   ├─> Fetch depth chart page
   │   └─> Parse HTML tables
   │
   ├─> If insufficient data:
   │   └─> Try ESPN API Backup
   │
   └─> Add players to collection

3. Validate Data
   ├─> Check total player count
   ├─> Check per-team counts
   └─> Generate validation report

4. Export Data
   ├─> JSON export
   ├─> CSV export
   ├─> Validation report
   └─> Summary text file
```

## Troubleshooting

### Common Issues

**Issue**: No players found for a team

**Solution**: 
- Check internet connection
- Verify ESPN website is accessible
- Check logs for specific error messages
- Try increasing `--max-retries`

**Issue**: Total player count below expected

**Solution**:
- Review `validation_report.json` for missing teams
- Check `depth_chart_compilation.log` for errors
- Some teams may have incomplete rosters during offseason
- Verify ESPN has published depth charts

**Issue**: Import errors

**Solution**:
```bash
pip install requests beautifulsoup4
```

## Performance

- **Compilation Time**: ~2-5 minutes for all 32 teams (depends on network)
- **Memory Usage**: ~50MB typical
- **Network**: ~100 HTTP requests total
- **Rate Limiting**: 1 second delay between teams to be respectful

## Limitations

1. **Data Freshness**: Depth charts are only as current as ESPN's data
2. **Practice Squad**: May not include all practice squad players
3. **Offseason**: Limited data during offseason months
4. **Format Changes**: ESPN website changes may require code updates

## Future Enhancements

Potential improvements for future versions:

- [ ] Additional data sources (NFL.com, team websites)
- [ ] Historical depth chart tracking
- [ ] Player statistics integration
- [ ] Automated scheduling/updates
- [ ] API endpoint for programmatic access
- [ ] Database backend option
- [ ] Real-time depth chart change notifications

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## License

See repository license file.

## Support

For issues or questions:
- Check the logs in `depth_chart_compilation.log`
- Review `validation_report.json` for data quality issues
- Open an issue on GitHub with log excerpts

## Acknowledgments

- ESPN for providing depth chart data
- NFL for official team information
- BeautifulSoup4 for HTML parsing
- Python requests library for HTTP functionality
