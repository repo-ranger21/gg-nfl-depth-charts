#!/usr/bin/env python3
"""
Example: Using the NFL Depth Chart Compiler

This script demonstrates various ways to use the NFL Depth Chart Compiler
for different use cases.
"""

from nfl_depth_chart_compiler import NFLDepthChartCompiler, NFL_TEAMS
import json
import sys


def example_1_basic_usage():
    """Example 1: Basic compilation of all teams"""
    print("=" * 80)
    print("EXAMPLE 1: Basic Usage - Compile All Teams")
    print("=" * 80)
    
    # Create compiler with default settings
    compiler = NFLDepthChartCompiler(output_dir="example_output")
    
    # Note: In real usage, this would fetch data from ESPN
    # For this example, we'll demonstrate with mock data
    print("Creating compiler instance...")
    print(f"Output directory: example_output")
    print(f"Ready to compile {len(NFL_TEAMS)} teams")
    print()


def example_2_single_team():
    """Example 2: Process a single team"""
    print("=" * 80)
    print("EXAMPLE 2: Single Team Processing")
    print("=" * 80)
    
    compiler = NFLDepthChartCompiler(output_dir="example_output")
    
    # Process just the Kansas City Chiefs
    team = "KC"
    print(f"Processing team: {team}")
    
    # In real usage:
    # player_count = compiler.process_team(team)
    # print(f"Found {player_count} players for {team}")
    
    print("Would fetch data from ESPN and process the team...")
    print()


def example_3_custom_configuration():
    """Example 3: Custom configuration"""
    print("=" * 80)
    print("EXAMPLE 3: Custom Configuration")
    print("=" * 80)
    
    # Custom settings
    compiler = NFLDepthChartCompiler(
        output_dir="custom_output",
        max_retries=5  # More retries for unstable networks
    )
    
    print("Custom configuration:")
    print(f"  Output directory: custom_output")
    print(f"  Max retries: {compiler.max_retries}")
    print()


def example_4_data_analysis():
    """Example 4: Analyzing compiled data"""
    print("=" * 80)
    print("EXAMPLE 4: Data Analysis")
    print("=" * 80)
    
    compiler = NFLDepthChartCompiler(output_dir="example_output")
    
    # Add some mock data for demonstration
    mock_players = [
        {"name": "Patrick Mahomes", "team": "KC", "position": "QB", "position_group": "Offense"},
        {"name": "Josh Allen", "team": "BUF", "position": "QB", "position_group": "Offense"},
        {"name": "Nick Bosa", "team": "SF", "position": "DE", "position_group": "Defense"},
        {"name": "Micah Parsons", "team": "DAL", "position": "LB", "position_group": "Defense"},
        {"name": "Justin Tucker", "team": "BAL", "position": "K", "position_group": "Special Teams"},
    ]
    
    compiler.players = mock_players
    compiler.player_names = {p["name"] for p in mock_players}
    
    # Analyze by position group
    from collections import defaultdict
    
    pos_groups = defaultdict(list)
    for player in compiler.players:
        pos_groups[player["position_group"]].append(player["name"])
    
    print("Players by Position Group:")
    for group, players in pos_groups.items():
        print(f"\n{group} ({len(players)} players):")
        for player in players:
            print(f"  - {player}")
    print()


def example_5_filtering_data():
    """Example 5: Filtering compiled data"""
    print("=" * 80)
    print("EXAMPLE 5: Filtering Data")
    print("=" * 80)
    
    compiler = NFLDepthChartCompiler(output_dir="example_output")
    
    # Add mock data
    mock_players = [
        {"name": "Patrick Mahomes", "team": "KC", "position": "QB", "depth": "1st", "injury_status": "Active"},
        {"name": "Chad Henne", "team": "KC", "position": "QB", "depth": "2nd", "injury_status": "Active"},
        {"name": "Travis Kelce", "team": "KC", "position": "TE", "depth": "1st", "injury_status": "Q"},
        {"name": "Isiah Pacheco", "team": "KC", "position": "RB", "depth": "1st", "injury_status": "Active"},
    ]
    
    compiler.players = mock_players
    
    # Filter: Get all starters
    starters = [p for p in compiler.players if p["depth"] == "1st"]
    print(f"Starters ({len(starters)} players):")
    for player in starters:
        print(f"  - {player['name']} ({player['position']})")
    
    print()
    
    # Filter: Get injured players
    injured = [p for p in compiler.players if p["injury_status"] != "Active"]
    print(f"Injured Players ({len(injured)} players):")
    for player in injured:
        print(f"  - {player['name']} ({player['injury_status']})")
    
    print()


def example_6_export_and_validation():
    """Example 6: Export with validation"""
    print("=" * 80)
    print("EXAMPLE 6: Export with Validation")
    print("=" * 80)
    
    import tempfile
    with tempfile.TemporaryDirectory() as tmpdir:
        compiler = NFLDepthChartCompiler(output_dir=tmpdir)
        
        # Add mock data
        for i in range(100):
            compiler.players.append({
                "name": f"Player {i}",
                "team": "KC",
                "position": "QB",
                "position_group": "Offense",
                "injury_status": "Active"
            })
        compiler.player_names = {p["name"] for p in compiler.players}
        
        # Validate data
        validation = compiler.validate_data()
        
        print("Validation Results:")
        print(f"  Total players: {validation['total_players']}")
        print(f"  Unique players: {validation['unique_players']}")
        print(f"  Meets expectation: {validation['meets_expectation']}")
        print(f"  Warnings: {len(validation['warnings'])}")
        print(f"  Errors: {len(validation['errors'])}")
        
        # Export if validation passes
        if not validation['errors']:
            json_file = compiler.export_json("depth_chart.json")
            print(f"\n✓ Exported JSON: {json_file}")
            
            csv_file = compiler.export_csv("depth_chart.csv")
            print(f"✓ Exported CSV: {csv_file}")
        else:
            print("\n✗ Export skipped due to validation errors")
    
    print()


def example_7_team_comparison():
    """Example 7: Compare teams"""
    print("=" * 80)
    print("EXAMPLE 7: Team Comparison")
    print("=" * 80)
    
    compiler = NFLDepthChartCompiler(output_dir="example_output")
    
    # Add mock data for two teams
    teams_data = {
        "KC": [
            {"name": "Patrick Mahomes", "position": "QB"},
            {"name": "Travis Kelce", "position": "TE"},
            {"name": "Chris Jones", "position": "DT"},
        ],
        "SF": [
            {"name": "Brock Purdy", "position": "QB"},
            {"name": "George Kittle", "position": "TE"},
            {"name": "Nick Bosa", "position": "DE"},
        ]
    }
    
    for team, players in teams_data.items():
        for player in players:
            compiler.players.append({
                "name": player["name"],
                "team": team,
                "position": player["position"],
                "position_group": "Offense" if player["position"] in ["QB", "TE"] else "Defense"
            })
    
    # Compare roster sizes
    from collections import Counter
    
    team_counts = Counter(p["team"] for p in compiler.players)
    
    print("Team Roster Comparison:")
    for team, count in sorted(team_counts.items()):
        print(f"  {team}: {count} players")
    
    print()


def example_8_cli_usage():
    """Example 8: CLI command examples"""
    print("=" * 80)
    print("EXAMPLE 8: Command Line Usage")
    print("=" * 80)
    
    print("Command line examples:\n")
    
    commands = [
        ("Basic compilation", "python nfl_depth_chart_compiler.py"),
        ("Custom output directory", "python nfl_depth_chart_compiler.py --output-dir my_data"),
        ("Export both formats", "python nfl_depth_chart_compiler.py --export-json --export-csv"),
        ("More retries", "python nfl_depth_chart_compiler.py --max-retries 5"),
        ("Validation only", "python nfl_depth_chart_compiler.py --validate-only"),
        ("Help", "python nfl_depth_chart_compiler.py --help"),
    ]
    
    for description, command in commands:
        print(f"{description}:")
        print(f"  $ {command}")
        print()


def main():
    """Run all examples"""
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 20 + "NFL DEPTH CHART COMPILER EXAMPLES" + " " * 25 + "║")
    print("╚" + "=" * 78 + "╝")
    print("\n")
    
    examples = [
        example_1_basic_usage,
        example_2_single_team,
        example_3_custom_configuration,
        example_4_data_analysis,
        example_5_filtering_data,
        example_6_export_and_validation,
        example_7_team_comparison,
        example_8_cli_usage,
    ]
    
    for i, example in enumerate(examples, 1):
        try:
            example()
        except Exception as e:
            print(f"Error in example {i}: {e}")
            import traceback
            traceback.print_exc()
    
    print("=" * 80)
    print("All examples completed!")
    print("=" * 80)
    print()
    print("For more information, see:")
    print("  - NFL_DEPTH_CHART_COMPILER_README.md")
    print("  - IMPLEMENTATION_SUMMARY.md")
    print()


if __name__ == "__main__":
    main()
