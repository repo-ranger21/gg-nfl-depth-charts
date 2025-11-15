#!/usr/bin/env python3
"""
Roster Verification Report Generator
Validates the scraped roster data and generates a markdown report.
"""
import os
import sys
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime
from typing import Dict
import pandas as pd

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

# Expected NFL teams
EXPECTED_TEAMS = [
    "BUF", "MIA", "NYJ", "NE", "BAL", "PIT", "CLE", "CIN",
    "HOU", "IND", "JAX", "TEN", "KC", "LV", "LAC", "DEN",
    "DAL", "PHI", "NYG", "WAS", "GB", "CHI", "MIN", "DET",
    "SF", "SEA", "LAR", "ARI", "ATL", "NO", "TB", "CAR"
]


def load_roster_data(filename: str = "nfl_full_roster.csv") -> pd.DataFrame:
    """Load roster data from CSV file."""
    try:
        if not os.path.exists(filename):
            logger.error(f"❌ Roster file not found: {filename}")
            return pd.DataFrame()
        
        df = pd.read_csv(filename)
        logger.info(f"✅ Loaded {len(df)} player records from {filename}")
        return df
    except Exception as e:
        logger.error(f"Error loading roster data: {e}")
        return pd.DataFrame()


def validate_roster_data(df: pd.DataFrame) -> Dict:
    """Validate roster data and return validation metrics."""
    if df.empty:
        return {
            "total_players": 0,
            "teams_present": 0,
            "teams_missing": len(EXPECTED_TEAMS),
            "validation_passed": False,
            "errors": ["No data found in roster file"]
        }
    
    validation_results = {
        "total_players": len(df),
        "teams_present": 0,
        "teams_missing": 0,
        "missing_teams": [],
        "team_stats": {},
        "position_distribution": {},
        "validation_passed": True,
        "errors": [],
        "warnings": []
    }
    
    # Check teams
    teams_in_data = df["team"].unique().tolist()
    validation_results["teams_present"] = len(teams_in_data)
    
    missing_teams = [team for team in EXPECTED_TEAMS if team not in teams_in_data]
    validation_results["teams_missing"] = len(missing_teams)
    validation_results["missing_teams"] = missing_teams
    
    if missing_teams:
        validation_results["errors"].append(f"Missing data for {len(missing_teams)} teams: {', '.join(missing_teams)}")
        validation_results["validation_passed"] = False
    
    # Team-level statistics
    for team in teams_in_data:
        team_df = df[df["team"] == team]
        validation_results["team_stats"][team] = {
            "player_count": len(team_df),
            "positions": team_df["position"].nunique()
        }
        
        # Check for suspiciously low roster counts
        if len(team_df) < 20:
            validation_results["warnings"].append(f"{team} has only {len(team_df)} players (expected ~53)")
    
    # Position distribution
    position_counts = df["position"].value_counts().to_dict()
    validation_results["position_distribution"] = position_counts
    
    # Check for required fields
    required_fields = ["team", "name", "position"]
    for field in required_fields:
        if field not in df.columns:
            validation_results["errors"].append(f"Missing required field: {field}")
            validation_results["validation_passed"] = False
        elif df[field].isna().any():
            null_count = df[field].isna().sum()
            validation_results["warnings"].append(f"{field} has {null_count} null values")
    
    # Check for duplicate players
    dup_combos = df.groupby(["team", "name"]).size().reset_index(name="count")
    dup_combos = dup_combos[dup_combos["count"] > 1]
    if not dup_combos.empty:
        validation_results["warnings"].append(f"Found {len(dup_combos)} players with duplicate team/name combinations")
    
    return validation_results


def generate_report(validation: Dict, output_file: str = "roster_verification_report.md") -> bool:
    """Generate markdown verification report."""
    try:
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
        
        report_lines = [
            "# NFL Roster Verification Report",
            "",
            f"**Generated:** {timestamp}",
            "",
            "## Summary",
            "",
            f"- **Total Players:** {validation['total_players']}",
            f"- **Teams Present:** {validation['teams_present']}/32",
            f"- **Teams Missing:** {validation['teams_missing']}",
            f"- **Validation Status:** {'✅ PASSED' if validation['validation_passed'] else '❌ FAILED'}",
            "",
        ]
        
        # Errors section
        if validation.get("errors"):
            report_lines.extend([
                "## ❌ Errors",
                "",
            ])
            for error in validation["errors"]:
                report_lines.append(f"- {error}")
            report_lines.append("")
        
        # Warnings section
        if validation.get("warnings"):
            report_lines.extend([
                "## ⚠️ Warnings",
                "",
            ])
            for warning in validation["warnings"]:
                report_lines.append(f"- {warning}")
            report_lines.append("")
        
        # Missing teams section
        if validation.get("missing_teams"):
            report_lines.extend([
                "## Missing Teams",
                "",
            ])
            for team in validation["missing_teams"]:
                report_lines.append(f"- {team}")
            report_lines.append("")
        
        # Team statistics
        if validation.get("team_stats"):
            report_lines.extend([
                "## Team Statistics",
                "",
                "| Team | Players | Positions |",
                "|------|---------|-----------|",
            ])
            for team, stats in sorted(validation["team_stats"].items()):
                report_lines.append(f"| {team} | {stats['player_count']} | {stats['positions']} |")
            report_lines.append("")
        
        # Position distribution
        if validation.get("position_distribution"):
            report_lines.extend([
                "## Position Distribution",
                "",
                "| Position | Count |",
                "|----------|-------|",
            ])
            for position, count in sorted(validation["position_distribution"].items(), key=lambda x: x[1], reverse=True):
                report_lines.append(f"| {position} | {count} |")
            report_lines.append("")
        
        # Data quality metrics
        report_lines.extend([
            "## Data Quality Metrics",
            "",
            "### Completeness",
            f"- Teams coverage: {validation['teams_present']}/32 ({validation['teams_present']/32*100:.1f}%)",
            f"- Total players: {validation['total_players']} (expected ~1,696 for full rosters)",
            "",
            "### Integrity",
            f"- Critical errors: {len(validation.get('errors', []))}",
            f"- Warnings: {len(validation.get('warnings', []))}",
            "",
        ])
        
        # Write report to file
        report_content = "\n".join(report_lines)
        with open(output_file, "w") as f:
            f.write(report_content)
        
        logger.info(f"✅ Verification report saved to {output_file}")
        return True
        
    except Exception as e:
        logger.error(f"Error generating report: {e}")
        return False


def print_summary(validation: Dict):
    """Print validation summary to console."""
    logger.info("\n" + "="*60)
    logger.info("ROSTER VERIFICATION SUMMARY")
    logger.info("="*60)
    logger.info(f"Total Players: {validation['total_players']}")
    logger.info(f"Teams Present: {validation['teams_present']}/32")
    logger.info(f"Teams Missing: {validation['teams_missing']}")
    
    if validation.get("errors"):
        logger.info(f"\n❌ Errors: {len(validation['errors'])}")
        for error in validation["errors"]:
            logger.error(f"  - {error}")
    
    if validation.get("warnings"):
        logger.info(f"\n⚠️  Warnings: {len(validation['warnings'])}")
        for warning in validation["warnings"]:
            logger.warning(f"  - {warning}")
    
    if validation["validation_passed"]:
        logger.info("\n✅ Validation PASSED")
    else:
        logger.info("\n❌ Validation FAILED")
    
    logger.info("="*60 + "\n")


def main():
    """Main execution function."""
    logger.info("="*60)
    logger.info("NFL ROSTER VERIFICATION REPORT GENERATOR")
    logger.info("="*60)
    
    # Load roster data
    df = load_roster_data()
    
    if df.empty:
        logger.error("❌ No roster data to validate. Exiting.")
        sys.exit(1)
    
    # Validate roster data
    validation_results = validate_roster_data(df)
    
    # Generate report
    if not generate_report(validation_results):
        logger.error("❌ Failed to generate verification report. Exiting.")
        sys.exit(1)
    
    # Print summary
    print_summary(validation_results)
    
    # Exit with appropriate code
    if validation_results["validation_passed"]:
        logger.info("✅ Roster verification completed successfully!")
        sys.exit(0)
    else:
        logger.warning("⚠️  Roster verification completed with errors!")
        sys.exit(0)  # Don't fail the workflow, just warn


if __name__ == "__main__":
    main()
