import nfl_data_py as nfl
import pandas as pd
from notion_client import Client
from dotenv import load_dotenv
import os
from datetime import datetime

# Load environment variables
load_dotenv()
notion = Client(auth=os.getenv("NOTION_TOKEN"))
DATABASE_ID = os.getenv("DATABASE_ID")

def get_week_number():
    """Auto-detect current NFL week"""
    # You can manually set this or use NFL schedule API
    return 9  # Change this each week OR automate it

def fetch_nflfastr_stats(week):
    """Pull actual stats from nflfastR"""
    print(f"Fetching Week {week} stats from nflfastR...")
    
    # Get player stats for current season
    stats = nfl.import_weekly_data([2025])
    week_stats = stats[stats['week'] == week].copy()
    
    # Create lookup dictionary
    player_lookup = {}
    
    for _, row in week_stats.iterrows():
        player_name = row['player_display_name']
        player_lookup[player_name] = {
            'passing_yards': row.get('passing_yards', 0),
            'passing_tds': row.get('passing_tds', 0),
            'rushing_yards': row.get('rushing_yards', 0),
            'rushing_tds': row.get('rushing_tds', 0),
            'receptions': row.get('receptions', 0),
            'receiving_yards': row.get('receiving_yards', 0),
            'receiving_tds': row.get('receiving_tds', 0),
            'targets': row.get('targets', 0)
        }
    
    return player_lookup

def query_notion_picks(week):
    """Get all picks for specified week from Notion"""
    print(f"Querying Notion for Week {week} picks...")
    
    results = notion.databases.query(
        database_id=DATABASE_ID,
        filter={
            "property": "Week",
            "number": {
                "equals": week
            }
        }
    )
    
    return results['results']

def update_notion_page(page_id, actual_value, hit):
    """Update a single pick with actual stat value"""
    notion.pages.update(
        page_id=page_id,
        properties={
            "Actual Value": {"number": actual_value},
            "Hit?": {"checkbox": hit}
        }
    )

def match_prop_to_stat(prop_type, player_stats):
    """Map prop type to actual stat value"""
    mapping = {
        'Passing Yards': 'passing_yards',
        'Passing TDs': 'passing_tds',
        'Rushing Yards': 'rushing_yards',
        'Rushing TDs': 'rushing_tds',
        'Receptions': 'receptions',
        'Receiving Yards': 'receiving_yards',
        'Receiving TDs': 'receiving_tds',
        'Targets': 'targets'
    }
    
    stat_key = mapping.get(prop_type)
    if stat_key and stat_key in player_stats:
        return player_stats[stat_key]
    return None

def main():
    week = get_week_number()
    print(f"\n🏈 Starting Week {week} Stat Update Process...\n")
    
    # Step 1: Fetch stats from nflfastR
    player_stats = fetch_nflfastr_stats(week)
    print(f"✅ Loaded stats for {len(player_stats)} players\n")
    
    # Step 2: Query Notion picks
    picks = query_notion_picks(week)
    print(f"✅ Found {len(picks)} picks in Notion\n")
    
    # Step 3: Update each pick
    updated_count = 0
    missing_count = 0
    
    for pick in picks:
        try:
            # Extract pick details
            props = pick['properties']
            player_name = props.get('Player', {}).get('title', [{}])[0].get('plain_text', '')
            prop_type = props.get('Prop Type', {}).get('select', {}).get('name', '')
            line = props.get('Line', {}).get('number', 0)
            over_under = props.get('Over/Under', {}).get('select', {}).get('name', '')
            
            # Find actual stat
            if player_name in player_stats:
                actual_value = match_prop_to_stat(prop_type, player_stats[player_name])
                
                if actual_value is not None:
                    # Determine hit/miss
                    if over_under == 'Over':
                        hit = actual_value > line
                    elif over_under == 'Under':
                        hit = actual_value < line
                    else:
                        hit = False
                    
                    # Update Notion
                    update_notion_page(pick['id'], actual_value, hit)
                    updated_count += 1
                    print(f"✅ {player_name} - {prop_type}: {actual_value} (Line: {line} {over_under}) → {'HIT' if hit else 'MISS'}")
                else:
                    missing_count += 1
                    print(f"⚠️  {player_name} - {prop_type}: Stat not found in nflfastR data")
            else:
                missing_count += 1
                print(f"⚠️  {player_name}: Player not found in Week {week} data")
        
        except Exception as e:
            print(f"❌ Error processing pick: {e}")
    
    # Summary
    print(f"\n{'='*60}")
    print(f"✅ COMPLETE: Updated {updated_count}/{len(picks)} picks")
    print(f"⚠️  Missing data for {missing_count} picks")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    main()
