"""
Fantasy Premier League Analysis Tool

This tool provides comprehensive analysis of Fantasy Premier League (FPL) data including:
- Player rankings and statistics
- Form analysis over different time periods
- Value for money calculations
- Visual charts and comparisons
- Historical performance tracking

Author: Imran Ahmed Kamal
Data Source: Fantasy Premier League API (https://fantasy.premierleague.com/api/)
"""

# IMPORTS AND DEPENDENCIES
# ============================================================================

import requests
import pandas as pd
from tabulate import tabulate
import matplotlib.pyplot as plt
import numpy as np
import os
import sys

# ============================================================================
# GLOBAL CONSTANTS AND CONFIGURATION
# ============================================================================

# Configure pandas display options for better readability
pd.set_option('display.width', 200)

# Base URL for the Fantasy Premier League API
base_url = 'https://fantasy.premierleague.com/api/'


def clear_screen():
    """
    Clear the console screen for better readability.

    Handles different operating systems and terminal environments gracefully.
    Falls back to spacing if screen clearing isn't available.
    """
    try:
        # Check if we're in a proper terminal environment
        if hasattr(os, 'environ') and 'TERM' in os.environ:
            # We have a proper terminal
            if os.name == 'nt':  # Windows
                os.system('cls')
            else:  # Unix/Linux/Mac
                os.system('clear')
        else:
            # Not in a proper terminal (like some IDEs), just add spacing
            print('\n' * 3)
            print('=' * 60)
    except Exception:
        # If anything fails, just print some newlines for spacing
        print('\n' * 3)
        print('=' * 60)


def print_header():
    """Print a formatted header for the application."""
    print("=" * 60)
    print("🏆 FANTASY PREMIER LEAGUE ANALYSIS TOOL 🏆")
    print("=" * 60)
    print()


def print_section_header(title):
    """
    Print a formatted section header.

    Args:
        title (str): The title to display in the header
    """
    print(f"\n{'─' * 50}")
    print(f"📊 {title}")
    print(f"{'─' * 50}")


def wait_for_user():
    """
    Wait for user input before continuing.

    Handles keyboard interrupts and EOF exceptions gracefully.
    """
    try:
        input("\n📌 Press Enter to return to the menu...")
    except (KeyboardInterrupt, EOFError):
        print("\n👋 Exiting...")
        sys.exit()


def get_valid_integer(prompt, min_val=None, max_val=None, default=None):
    """
    Get a valid integer input from the user with optional constraints.

    Args:
        prompt (str): The prompt to show to the user
        min_val (int, optional): Minimum allowed value
        max_val (int, optional): Maximum allowed value
        default (int, optional): Default value if user presses Enter

    Returns:
        int: A valid integer within the specified constraints
    """
    while True:
        user_input = input(prompt).strip()

        # Handle empty input with default value
        if user_input == "":
            if default is not None:
                return default
            else:
                print("❌ Please enter a number.")
                continue

        try:
            val = int(user_input)

            # Check if value is within specified range
            if (min_val is not None and val < min_val) or (max_val is not None and val > max_val):
                print(f"❌ Please enter a number between {min_val} and {max_val}.")
            else:
                return val
        except ValueError:
            print("❌ Invalid input. Please enter a valid number.")


def get_valid_position():
    """
    Get a valid position input from user.

    Returns:
        str or None: Valid position name (lowercase) or None for all positions
    """
    valid_positions = ['goalkeeper', 'defender', 'midfielder', 'forward']

    while True:
        try:
            pos = input(
                "Enter position (goalkeeper/defender/midfielder/forward) or press Enter for all: ").strip().lower()

            # Empty input means all positions
            if not pos:
                return None

            # Check if position is valid
            if pos in valid_positions:
                return pos

            print(f"❌ Invalid position. Choose from: {', '.join(valid_positions)}")
        except (EOFError, KeyboardInterrupt):
            print("\nExiting...")
            sys.exit(0)

# ============================================================================
# DATA LOADING AND API FUNCTIONS
# ============================================================================
def get_player_name(player_id, players_df):
    """
    Get player name from ID - helper function to avoid repetition.

    Args:
        player_id (int): The player's ID
        players_df (pd.DataFrame): DataFrame containing player data

    Returns:
        str: Formatted player name (First Name Last Name)
    """
    player_row = players_df[players_df['Player ID'] == player_id]
    if player_row.empty:
        return f"Player {player_id} (ID not found)"
    return f"{player_row.iloc[0]['First Name']} {player_row.iloc[0]['Last Name']}"

def load_fpl_data():
    """
    Load FPL data from the API and return processed DataFrames.

    Fetches data from the FPL API and creates clean, user-friendly DataFrames
    with proper column names and calculated fields.

    Returns:
        tuple: (players_cleaned, team_map)
            - players_cleaned: DataFrame with cleaned player data
            - team_map: Dictionary mapping team IDs to team names
    """
    # Fetch data from FPL API
    r = requests.get(base_url + 'bootstrap-static/').json()

    # Create DataFrames from API response
    players = pd.json_normalize(r['elements'])  # Player data
    teams_df = pd.json_normalize(r['teams'])  # Team data
    positions_df = pd.json_normalize(r['element_types'])  # Position data

    # Create mapping dictionaries for easier lookups
    team_map = dict(zip(teams_df['id'], teams_df['name']))
    position_map = dict(zip(positions_df['id'], positions_df['singular_name']))

    # Add human-readable team and position names
    players['team_name'] = players['team'].map(team_map)
    players['position'] = players['element_type'].map(position_map)

    # Add position ordering for sorting (if needed)
    players['position_order'] = players['position'].map({
        'Manager': 0,
        'Goalkeeper': 1,
        'Defender': 2,
        'Midfielder': 3,
        'Forward': 4
    }).fillna(99)

    # Convert cost from 0.1m units to millions (e.g., 75 -> 7.5)
    players['cost_million'] = players['now_cost'] / 10

    # Convert percentage strings to floats
    players['selected_by_percent'] = players['selected_by_percent'].astype(float)
    players['form'] = players['form'].astype(float)

    # Create a cleaned version for display (remove managers, rename columns)
    players_cleaned = players[players['position'] != 'Manager'].copy()
    players_cleaned = players_cleaned.rename(columns={
        'id': 'Player ID',
        'first_name': 'First Name',
        'second_name': 'Last Name',
        'team_name': 'Team',
        'position': 'Position',
        'cost_million': 'Cost (Million £)',
        'selected_by_percent': 'Selected By (%)',
        'form': 'Form',
        'total_points': 'Total Points'
    })

    return players_cleaned, team_map


def get_gameweek_history(player_id):
    """
    Get gameweek history for a specific player.

    Args:
        player_id (int): The player's ID

    Returns:
        pd.DataFrame: DataFrame containing gameweek history data
    """
    try:
        # Fetch player's detailed history from API
        r = requests.get(base_url + f'element-summary/{player_id}/').json()
        return pd.json_normalize(r['history'])
    except:
        # Return empty DataFrame if request fails
        return pd.DataFrame()

# ============================================================================
# DATA ANALYSIS AND STATISTICS FUNCTIONS
# ============================================================================
def show_top_players(players_df, up_to_gameweek=None, top_n=20, position=None):
    """
    Display top players by total points.

    Args:
        players_df (pd.DataFrame): DataFrame containing player data
        up_to_gameweek (int, optional): Calculate points only up to this gameweek
        top_n (int): Number of top players to show
        position (str, optional): Filter by position (goalkeeper/defender/midfielder/forward)
    """
    # Apply position filter if specified
    if position:
        position = position.capitalize()
        valid_positions = ['Goalkeeper', 'Defender', 'Midfielder', 'Forward']
        if position not in valid_positions:
            print(f"Invalid position: {position}. Choose from: {', '.join(valid_positions)}")
            return
        players_df = players_df[players_df['Position'] == position]

    # Calculate points up to specific gameweek if requested
    if up_to_gameweek:
        temp_data = []
        for pid in players_df['Player ID']:
            gw_hist = get_gameweek_history(pid)
            if gw_hist.empty:
                continue

            # Sum points only up to the specified gameweek
            gw_total = gw_hist[gw_hist['round'] <= up_to_gameweek]['total_points'].sum()
            temp_data.append({'Player ID': pid, 'Points to GW': gw_total})

        # Merge with original data and sort by calculated points
        temp_df = pd.DataFrame(temp_data)
        merged = pd.merge(players_df, temp_df, on='Player ID')
        merged = merged.sort_values(by='Points to GW', ascending=False)

        if top_n > 0:
            merged = merged.head(top_n)

        print(tabulate(
            merged[['Player ID', 'First Name', 'Last Name', 'Team', 'Position', 'Cost (Million £)', 'Points to GW']],
            headers='keys', tablefmt='fancy_grid'))
    else:
        # Use total points from season
        sorted_df = players_df.sort_values(by='Total Points', ascending=False)
        if top_n > 0:
            sorted_df = sorted_df.head(top_n)

        print(tabulate(
            sorted_df[['Player ID', 'First Name', 'Last Name', 'Team', 'Position', 'Cost (Million £)', 'Total Points']],
            headers='keys', tablefmt='fancy_grid'))


def show_player_history(player_id, team_map, players_df):
    """
    Show full gameweek history for a specific player.

    Args:
        player_id (int): The player's ID
        team_map (dict): Dictionary mapping team IDs to team names
        players_df (pd.DataFrame): DataFrame containing player data
    """
    # Get player name for display
    player_name = get_player_name(player_id, players_df)
    print(f"\n=== GAMEWEEK HISTORY: {player_name} ===")

    # Fetch gameweek data
    gw = get_gameweek_history(player_id)
    if gw.empty:
        print("No gameweek data available for this player.")
        return

    # Add opponent team names for better readability
    gw['Opponent'] = gw['opponent_team'].map(team_map)

    # Display the history in a formatted table
    print(tabulate(
        gw[['round', 'Opponent', 'was_home', 'minutes', 'goals_scored', 'assists', 'clean_sheets', 'total_points']],
        headers='keys', tablefmt='fancy_grid'))


def show_top_by_pick_rate(players_df, top_n=10, position=None):
    """
    Display top players by pick rate (selected by percentage).

    Args:
        players_df (pd.DataFrame): DataFrame containing player data
        top_n (int): Number of top players to show
        position (str, optional): Filter by position
    """
    df = players_df.copy()

    # Apply position filter if specified
    if position:
        position = position.capitalize()
        valid_positions = ['Goalkeeper', 'Defender', 'Midfielder', 'Forward']
        if position not in valid_positions:
            print(f"Invalid position: {position}. Choose from: {', '.join(valid_positions)}")
            return
        df = df[df['Position'] == position]

    # Sort by pick rate (highest first)
    sorted_df = df.sort_values(by='Selected By (%)', ascending=False)
    if top_n > 0:
        sorted_df = sorted_df.head(top_n)

    print(tabulate(
        sorted_df[['Player ID', 'First Name', 'Last Name', 'Team', 'Position', 'Cost (Million £)', 'Selected By (%)']],
        headers='keys', tablefmt='fancy_grid'))


def show_player_gameweek_stats(player_id, gameweek, team_map, players_df):
    """
    Show a specific player's stats for a given gameweek.

    Args:
        player_id (int): The player's ID
        gameweek (int): The gameweek number
        team_map (dict): Dictionary mapping team IDs to team names
        players_df (pd.DataFrame): DataFrame containing player data
    """
    # Get player name for display
    player_name = get_player_name(player_id, players_df)
    print(f"\n=== GAMEWEEK {gameweek} STATS: {player_name} ===")

    # Fetch gameweek data
    gw = get_gameweek_history(player_id)
    if gw.empty:
        print("No gameweek data available for this player.")
        return

    # Find the specific gameweek
    row = gw[gw['round'] == gameweek]
    if row.empty:
        print(f"No data for Gameweek {gameweek}.")
        return

    row = row.iloc[0]
    opponent = team_map.get(row['opponent_team'], 'Unknown')

    # Display the stats
    print(f"Gameweek {gameweek} vs {opponent} ({'Home' if row['was_home'] else 'Away'})")
    print(f"Minutes: {row['minutes']}, Goals: {row['goals_scored']}, Assists: {row['assists']}, "
          f"Clean Sheets: {row['clean_sheets']}, Total Points: {row['total_points']}")


def show_players_sorted_by_team(players_df):
    """
    Show all players sorted by team name.

    Args:
        players_df (pd.DataFrame): DataFrame containing player data
    """
    sorted_df = players_df.sort_values(by=['Team', 'Last Name', 'First Name'])
    print(tabulate(
        sorted_df[['Player ID', 'First Name', 'Last Name', 'Team', 'Position', 'Cost (Million £)', 'Total Points']],
        headers='keys', tablefmt='fancy_grid'))


def show_players_sorted_alphabetically(players_df):
    """
    Show all players sorted alphabetically by last name.

    Args:
        players_df (pd.DataFrame): DataFrame containing player data
    """
    sorted_df = players_df.sort_values(by=['Last Name', 'First Name'])
    print(tabulate(
        sorted_df[['Player ID', 'First Name', 'Last Name', 'Team', 'Position', 'Cost (Million £)', 'Total Points']],
        headers='keys', tablefmt='fancy_grid'))


def show_players_by_position(players_df, position):
    """
    Show players from a specific position, sorted by total points.

    Args:
        players_df (pd.DataFrame): DataFrame containing player data
        position (str): The position to filter by
    """
    position = position.capitalize()  # Make input case-insensitive
    valid_positions = ['Goalkeeper', 'Defender', 'Midfielder', 'Forward']

    if position not in valid_positions:
        print(f"Invalid position: {position}. Choose from: {', '.join(valid_positions)}")
        return

    # Filter by position and sort by total points
    filtered = players_df[players_df['Position'] == position].sort_values(by='Total Points', ascending=False)

    print(tabulate(filtered[['Player ID', 'First Name', 'Last Name', 'Team', 'Cost (Million £)', 'Total Points']],
                   headers='keys', tablefmt='fancy_grid'))


def show_top_value_for_money(players_df, top_n=20, position=None, min_points=50):
    """
    Show players with best value for money (points per million).

    Args:
        players_df (pd.DataFrame): DataFrame containing player data
        top_n (int): Number of top players to show
        position (str, optional): Filter by position
        min_points (int): Minimum points threshold to filter out low-scoring cheap players
    """
    df = players_df.copy()

    # Filter players with minimum points to avoid low-scoring cheap players
    df = df[df['Total Points'] >= min_points]

    # Apply position filter if specified
    if position:
        position = position.capitalize()
        valid_positions = ['Goalkeeper', 'Defender', 'Midfielder', 'Forward']
        if position not in valid_positions:
            print(f"Invalid position: {position}. Choose from: {', '.join(valid_positions)}")
            return
        df = df[df['Position'] == position]

    # Calculate value for money (points per million cost)
    df['Value (Pts/£m)'] = df['Total Points'] / df['Cost (Million £)']

    # Sort by value for money (highest first)
    sorted_df = df.sort_values(by='Value (Pts/£m)', ascending=False)
    if top_n > 0:
        sorted_df = sorted_df.head(top_n)

    print(f"\nTop {top_n} Players by Value for Money (min {min_points} points):")
    print(tabulate(sorted_df[
                       ['Player ID', 'First Name', 'Last Name', 'Team', 'Position', 'Cost (Million £)', 'Total Points',
                        'Value (Pts/£m)']],
                   headers='keys', tablefmt='fancy_grid', floatfmt='.1f'))


def show_top_form_players(players_df, top_n=20, position=None, last_n_gameweeks=5, from_gameweek=None,
                          to_gameweek=None):
    """
    Show players with best form over a specific period or last N gameweeks.

    Args:
        players_df (pd.DataFrame): DataFrame containing player data
        top_n (int): Number of top players to show
        position (str, optional): Filter by position
        last_n_gameweeks (int): Number of recent gameweeks to analyze
        from_gameweek (int, optional): Start gameweek for specific period
        to_gameweek (int, optional): End gameweek for specific period
    """
    df = players_df.copy()

    # Apply position filter if specified
    if position:
        position = position.capitalize()
        valid_positions = ['Goalkeeper', 'Defender', 'Midfielder', 'Forward']
        if position not in valid_positions:
            print(f"Invalid position: {position}. Choose from: {', '.join(valid_positions)}")
            return
        df = df[df['Position'] == position]

    # Calculate form over specified period for each player
    form_data = []
    for pid in df['Player ID']:
        gw_hist = get_gameweek_history(pid)
        if gw_hist.empty:
            continue

        # Determine which gameweeks to analyze
        if from_gameweek and to_gameweek:
            # Specific period: from GW X to GW Y
            period_gws = gw_hist[(gw_hist['round'] >= from_gameweek) & (gw_hist['round'] <= to_gameweek)]
            period_desc = f"GW {from_gameweek}-{to_gameweek}"
        elif from_gameweek:
            # From specific gameweek to end of available data
            period_gws = gw_hist[gw_hist['round'] >= from_gameweek]
            max_gw = period_gws['round'].max() if not period_gws.empty else from_gameweek
            period_desc = f"GW {from_gameweek}-{max_gw}"
        else:
            # Last N gameweeks (most recent)
            period_gws = gw_hist.nlargest(last_n_gameweeks, 'round')
            period_desc = f"Last {last_n_gameweeks} GW"

        # Calculate form statistics
        form_points = period_gws['total_points'].sum()
        games_played = len(period_gws[period_gws['minutes'] > 0])
        avg_points = form_points / max(games_played, 1) if games_played > 0 else 0

        form_data.append({
            'Player ID': pid,
            f'{period_desc} Points': form_points,
            'Games Played': games_played,
            'Avg Points/Game': avg_points
        })

    # Merge form data with player data and sort
    form_df = pd.DataFrame(form_data)
    merged = pd.merge(df, form_df, on='Player ID')
    merged = merged.sort_values(by=f'{period_desc} Points', ascending=False)

    if top_n > 0:
        merged = merged.head(top_n)

    print(f"\nTop {top_n} Players by Form ({period_desc}):")
    print(tabulate(merged[['Player ID', 'First Name', 'Last Name', 'Team', 'Position', 'Cost (Million £)',
                           f'{period_desc} Points', 'Games Played', 'Avg Points/Game']],
                   headers='keys', tablefmt='fancy_grid', floatfmt='.1f'))


def show_player_form_analysis(player_id, team_map, players_df, last_n_gameweeks=5, from_gameweek=None,
                              to_gameweek=None):
    """
    Show detailed form analysis for a specific player over a specified period.

    Args:
        player_id (int): The player's ID
        team_map (dict): Dictionary mapping team IDs to team names
        players_df (pd.DataFrame): DataFrame containing player data
        last_n_gameweeks (int): Number of recent gameweeks to analyze
        from_gameweek (int, optional): Start gameweek for specific period
        to_gameweek (int, optional): End gameweek for specific period
    """
    # Get player name for display
    player_name = get_player_name(player_id, players_df)

    # Fetch gameweek data
    gw = get_gameweek_history(player_id)
    if gw.empty:
        print("No gameweek data available for this player.")
        return

    gw = gw.sort_values(by='round')

    # Calculate overall season stats
    total_points = gw['total_points'].sum()
    games_played = len(gw[gw['minutes'] > 0])
    avg_points = total_points / max(games_played, 1)

    # Determine period to analyze
    if from_gameweek and to_gameweek:
        # Specific period: from GW X to GW Y
        period_gws = gw[(gw['round'] >= from_gameweek) & (gw['round'] <= to_gameweek)]
        period_desc = f"GW {from_gameweek}-{to_gameweek}"
    elif from_gameweek:
        # From specific gameweek to end of available data
        period_gws = gw[gw['round'] >= from_gameweek]
        max_gw = period_gws['round'].max() if not period_gws.empty else from_gameweek
        period_desc = f"GW {from_gameweek}-{max_gw}"
    else:
        # Last N gameweeks (most recent)
        period_gws = gw.nlargest(last_n_gameweeks, 'round')
        period_desc = f"Last {last_n_gameweeks} gameweeks"

    if period_gws.empty:
        print(f"No data available for the specified period: {period_desc}")
        return

    # Calculate period stats
    period_points = period_gws['total_points'].sum()
    period_games = len(period_gws[period_gws['minutes'] > 0])
    period_avg = period_points / max(period_games, 1)

    # Calculate form trend (comparing first half vs second half of period)
    if len(period_gws) >= 4:
        period_sorted = period_gws.sort_values(by='round')
        mid_point = len(period_sorted) // 2
        early_period = period_sorted.iloc[:mid_point]['total_points'].mean()
        late_period = period_sorted.iloc[mid_point:]['total_points'].mean()
        trend = "Improving" if late_period > early_period else "Declining" if late_period < early_period else "Stable"
    else:
        trend = "Insufficient data"

    # Display analysis
    print(f"\n=== FORM ANALYSIS: {player_name} ===")
    print(f"Overall Season:")
    print(f"  Total Points: {total_points}")
    print(f"  Games Played: {games_played}")
    print(f"  Average Points/Game: {avg_points:.1f}")
    print(f"\nPeriod Analysis ({period_desc}):")
    print(f"  Total Points: {period_points}")
    print(f"  Games Played: {period_games}")
    print(f"  Average Points/Game: {period_avg:.1f}")
    print(f"  Trend: {trend}")

    # Show detailed gameweeks for the period
    print(f"\nGameweeks Detail ({period_desc}):")
    display_gws = period_gws.sort_values(by='round', ascending=False)
    display_gws['Opponent'] = display_gws['opponent_team'].map(team_map)
    display_gws['Home/Away'] = display_gws['was_home'].map({True: 'H', False: 'A'})

    print(tabulate(display_gws[['round', 'Opponent', 'Home/Away', 'minutes', 'goals_scored',
                                'assists', 'clean_sheets', 'total_points']],
                   headers=['GW', 'Opponent', 'H/A', 'Min', 'Goals', 'Assists', 'CS', 'Points'],
                   tablefmt='fancy_grid'))


# ============================================================================
# DATA VISUALIZATION FUNCTIONS
# ============================================================================
def plot_form_comparison(player_ids, team_map, players_df, last_n_gameweeks=8, from_gameweek=None, to_gameweek=None):
    """
    Plot form comparison for multiple players over a specified period.

    Args:
        player_ids (list): List of player IDs to compare
        team_map (dict): Dictionary mapping team IDs to team names
        players_df (pd.DataFrame): DataFrame containing player data
        last_n_gameweeks (int): Number of recent gameweeks to analyze
        from_gameweek (int, optional): Start gameweek for specific period
        to_gameweek (int, optional): End gameweek for specific period
    """
    plt.figure(figsize=(12, 8))

    # Colors for different players
    colors = ['blue', 'red', 'green', 'orange', 'purple', 'brown']

    for i, player_id in enumerate(player_ids):
        gw = get_gameweek_history(player_id)
        if gw.empty:
            continue

        # Get player name for legend
        player_name = get_player_name(player_id, players_df)

        # Filter gameweeks based on specified period
        if from_gameweek and to_gameweek:
            period_gws = gw[(gw['round'] >= from_gameweek) & (gw['round'] <= to_gameweek)]
            period_desc = f"GW {from_gameweek}-{to_gameweek}"
        elif from_gameweek:
            period_gws = gw[gw['round'] >= from_gameweek]
            max_gw = period_gws['round'].max() if not period_gws.empty else from_gameweek
            period_desc = f"GW {from_gameweek}-{max_gw}"
        else:
            period_gws = gw.nlargest(last_n_gameweeks, 'round')
            period_desc = f"Last {last_n_gameweeks} GW"

        if period_gws.empty:
            continue

        # Sort by gameweek and plot
        period_gws = period_gws.sort_values(by='round')
        rounds = period_gws['round']
        points = period_gws['total_points']

        color = colors[i % len(colors)]
        plt.plot(rounds, points, marker='o', label=player_name, color=color, linewidth=2)

    # Customize the plot
    plt.title(f"Form Comparison - {period_desc}")
    plt.xlabel("Gameweek")
    plt.ylabel("Points")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.show()


def plot_player_points(player_id, team_map, players_df, player_name=None):
    """
    Plot a player's points over all gameweeks.

    Args:
        player_id (int): The player's ID
        team_map (dict): Dictionary mapping team IDs to team names
        players_df (pd.DataFrame): DataFrame containing player data
        player_name (str, optional): Player name (will be fetched if not provided)
    """
    if not player_name:
        player_name = get_player_name(player_id, players_df)

    # Fetch gameweek data
    gw = get_gameweek_history(player_id)
    if gw.empty:
        print("No gameweek data available for this player.")
        return

    # Sort by gameweek and prepare data
    gw = gw.sort_values(by='round')
    rounds = gw['round']
    points = gw['total_points']

    # Create the plot
    plt.figure(figsize=(10, 5))
    plt.plot(rounds, points, marker='o', color='blue', label='Points')
    plt.title(f"{player_name} – Points per Gameweek")
    plt.xlabel("Gameweek")
    plt.ylabel("Points")
    plt.grid(True)
    plt.legend()
    plt.yticks(range(0, int(max(points) + 2), 2))  # <- this sets y-axis ticks to multiples of 2
    plt.tight_layout()
    plt.show()


def plot_player_price(player_id, team_map, players_df, player_name=None):
    """
    Plot a player's price changes over all gameweeks.

    Creates a line chart showing how a player's price has changed throughout
    the season, with appropriate scaling and formatting.

    Args:
        player_id (int): The player's ID
        team_map (dict): Dictionary mapping team IDs to team names
        players_df (pd.DataFrame): DataFrame containing player data
        player_name (str, optional): Player name (will be fetched if not provided)
    """
    # Get player name if not provided
    if not player_name:
        player_name = get_player_name(player_id, players_df)

    # Fetch gameweek data for the player
    gw = get_gameweek_history(player_id)
    if gw.empty:
        print("No gameweek data available for this player.")
        return

    # Sort data by gameweek and prepare price data
    gw = gw.sort_values(by='round')
    rounds = gw['round']
    prices = gw['value'] / 10  # Convert from 0.1m units to millions (e.g., 75 -> 7.5)

    # Get initial price for better Y-axis scaling
    gw1_price = prices.iloc[0]

    # Calculate appropriate Y-axis limits centered around starting price
    y_min = max(0, gw1_price - 2)  # Don't go below 0
    y_max = gw1_price + 2
    y_ticks = np.arange(y_min, y_max + 0.2, 0.2)  # Ticks every £0.2m

    # Create and customize the plot
    plt.figure(figsize=(10, 5))
    plt.plot(rounds, prices, marker='s', color='green', label='Price (£m)')
    plt.title(f"{player_name} – Price per Gameweek")
    plt.xlabel("Gameweek")
    plt.ylabel("Price (£m)")
    plt.grid(True)
    plt.legend()
    plt.xticks(np.arange(rounds.min(), rounds.max() + 1, 2))  # X-axis ticks every 2 gameweeks
    plt.yticks(y_ticks)
    plt.ylim(y_min, y_max)
    plt.tight_layout()
    plt.show()


def compare_players_points(player1_id, player2_id, team_map, players_df):
    """
    Compare two players' points performance over the season.

    Displays total points comparison and creates a visual chart showing
    both players' points per gameweek side by side.

    Args:
        player1_id (int): First player's ID
        player2_id (int): Second player's ID
        team_map (dict): Dictionary mapping team IDs to team names
        players_df (pd.DataFrame): DataFrame containing player data
    """
    # Get player names for display
    player1_name = get_player_name(player1_id, players_df)
    player2_name = get_player_name(player2_id, players_df)

    print(f"\n=== COMPARING: {player1_name} vs {player2_name} ===")

    # Fetch gameweek data for both players
    gw1 = get_gameweek_history(player1_id)
    gw2 = get_gameweek_history(player2_id)

    # Check if data is available for both players
    if gw1.empty or gw2.empty:
        print("Cannot compare - missing gameweek data for one or both players.")
        return

    # Sort data by gameweek for proper chronological display
    gw1 = gw1.sort_values(by='round')
    gw2 = gw2.sort_values(by='round')

    # Calculate and display total points comparison
    total1 = gw1['total_points'].sum()
    total2 = gw2['total_points'].sum()

    print(f"{player1_name}: {total1} points")
    print(f"{player2_name}: {total2} points")
    print(f"Difference: {abs(total1 - total2)} points")

    # Create comparison chart
    plt.figure(figsize=(12, 6))

    # Plot both players' points with different markers and colors
    plt.plot(gw1['round'], gw1['total_points'], marker='o', label=player1_name, color='blue', linewidth=2)
    plt.plot(gw2['round'], gw2['total_points'], marker='s', label=player2_name, color='red', linewidth=2)

    # Customize the plot
    plt.title(f"Points Comparison: {player1_name} vs {player2_name}")
    plt.xlabel("Gameweek")
    plt.ylabel("Points")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.show()

# ============================================================================
# USER INTERFACE FUNCTIONS
# ============================================================================
def show_main_menu():
    """
    Display the main menu with organized sections.

    Shows all available options grouped by functionality:
    - Player rankings and lists
    - Form and performance analysis
    - Individual player analysis
    - Advanced analysis
    """
    print_header()

    # Player rankings and basic lists
    print("🔍 PLAYER RANKINGS & LISTS")
    print("   1. Top players by total points")
    print("   2. Top players by pick rate")
    print("   3. Top players by value for money")
    print("   4. Players by position")
    print("   5. All players (sorted alphabetically)")
    print("   6. All players (sorted by team)")

    # Form and performance analysis
    print("\n⚡ FORM & PERFORMANCE ANALYSIS")
    print("   7. Top players by recent form")
    print("   8. Top players up to specific gameweek")
    print("   9. Player form analysis (detailed)")
    print("  10. Compare multiple players' form")

    # Individual player analysis
    print("\n📈 INDIVIDUAL PLAYER ANALYSIS")
    print("  11. Player's full gameweek history")
    print("  12. Player's specific gameweek stats")
    print("  13. Player points chart")
    print("  14. Player price chart")
    print("  15. Compare two players' points")

    # Advanced analysis options
    print("\n🎯 ADVANCED ANALYSIS")
    print("  16. Custom form analysis (date range)")
    print("  17. Custom period comparison")
    print("  18. Multi-player form comparison")

    # Exit option
    print("\n❌ EXIT")
    print("   0. Exit application")

    print("\n" + "=" * 60)

# ============================================================================
# SUBMENU HANDLERS
# ============================================================================

def show_individual_analysis_menu():
    """
    Handle individual player analysis submenu.

    Provides a focused menu for single-player analysis functions like
    history, charts, and comparisons. This function is currently not used
    in the main loop but could be integrated for better organization.
    """
    while True:
        clear_screen()
        print_section_header("INDIVIDUAL PLAYER ANALYSIS")

        # Display submenu options
        print("1. Player's full gameweek history")
        print("2. Player's specific gameweek stats")
        print("3. Player points chart")
        print("4. Player price chart")
        print("5. Compare two players' points")
        print("0. Back to main menu")

        # Get and validate user choice
        choice = input("Select option (0-18): ").strip()
        if not choice.isdigit() or not (0 <= int(choice) <= 18):
            print("❌ Invalid option. Please enter a number between 0 and 18.")
            wait_for_user()
            continue
        choice = int(choice)

        # Handle menu choices
        if choice == 0:
            break
        elif choice == 1:
            pid = get_valid_integer("Enter player ID: ", min_val=1)
            show_player_history(pid, team_map)
            wait_for_user()
        elif choice == 2:
            pid = get_valid_integer("Enter player ID: ", min_val=1)
            gw = get_valid_integer("Enter gameweek number: ", min_val=1)
            show_player_gameweek_stats(pid, gw, team_map)
            wait_for_user()
        elif choice == 3:
            pid = get_valid_integer("Enter player ID: ", min_val=1)
            # Validate player exists before plotting
            player_row = players_df[players_df['Player ID'] == pid]
            if player_row.empty:
                print("❌ Player ID not found.")
            else:
                name = f"{player_row.iloc[0]['First Name']} {player_row.iloc[0]['Last Name']}"
                plot_player_points(pid, team_map, name)
            wait_for_user()
        elif choice == 4:
            pid = get_valid_integer("Enter player ID: ", min_val=1)
            # Validate player exists before plotting
            player_row = players_df[players_df['Player ID'] == pid]
            if player_row.empty:
                print("❌ Player ID not found.")
            else:
                name = f"{player_row.iloc[0]['First Name']} {player_row.iloc[0]['Last Name']}"
                plot_player_price(pid, team_map, name)
            wait_for_user()
        elif choice == 5:
            pid1 = get_valid_integer("Enter first player ID: ", min_val=1)
            pid2 = get_valid_integer("Enter second player ID: ", min_val=1)
            compare_players_points(pid1, pid2, team_map, players_df)
            wait_for_user()
        else:
            print("❌ Invalid option. Try again.")
            wait_for_user()


def show_advanced_analysis_menu():
    """
    Handle advanced analysis submenu.

    Provides advanced analysis options like custom date ranges,
    multi-player comparisons, and custom period analysis.
    This function is currently not used in the main loop.
    """
    while True:
        clear_screen()
        print_section_header("ADVANCED ANALYSIS")

        # Display advanced analysis options
        print("1. Custom form analysis (date range)")
        print("2. Custom period comparison")
        print("3. Multi-player form comparison")
        print("0. Back to main menu")

        choice = input("\nSelect option (0-3): ").strip()

        # Handle menu choices
        if choice == '0':
            break
        elif choice == '1':
            # Custom form analysis for single player over specified period
            pid = get_valid_integer("Enter player ID: ", min_val=1)
            from_gw = get_valid_integer("Enter starting gameweek: ", min_val=1)
            to_gw = get_valid_integer("Enter ending gameweek: ", min_val=from_gw)
            show_player_form_analysis(pid, team_map, players_df, from_gameweek=from_gw, to_gameweek=to_gw)
            wait_for_user()
        elif choice == '2':
            # Custom period comparison for top players
            top_n = get_valid_integer("How many top players to show: ", min_val=1)
            pos = get_valid_position()
            from_gw = get_valid_integer("Enter starting gameweek: ", min_val=1)
            to_gw = get_valid_integer("Enter ending gameweek: ", min_val=from_gw)
            show_top_form_players(players_df, top_n=top_n, position=pos, from_gameweek=from_gw, to_gameweek=to_gw)
            wait_for_user()
        elif choice == '3':
            # Multi-player form comparison chart
            ids_input = input("Enter player IDs to compare (comma-separated): ")
            try:
                player_ids = [int(pid.strip()) for pid in ids_input.split(',') if pid.strip().isdigit()]
                if len(player_ids) > 6:
                    print("⚠️ Maximum 6 players for comparison. Using first 6.")
                    player_ids = player_ids[:6]
                from_gw = get_valid_integer("Enter starting gameweek: ", min_val=1)
                to_gw = get_valid_integer("Enter ending gameweek: ", min_val=from_gw)
                plot_form_comparison(player_ids, team_map, players_df, from_gameweek=from_gw, to_gameweek=to_gw)
                wait_for_user()
            except ValueError:
                print("❌ Invalid input. Please enter valid player IDs.")
                wait_for_user()
        else:
            print("❌ Invalid option. Try again.")
            wait_for_user()

# ============================================================================
# MAIN APPLICATION CONTROLLER
# ============================================================================
def main():
    """
    Main application loop with organized menu system.

    Initializes the application, loads FPL data, and handles the main
    menu loop. Processes user input and calls appropriate functions
    based on menu selections.
    """
    # Declare global variables for use throughout the application
    global players_df, team_map

    # Load FPL data from API
    print("🔄 Loading FPL data...")
    try:
        players_df, team_map = load_fpl_data()
        print("✅ Data loaded successfully!")
    except Exception as e:
        print(f"❌ Error loading data: {e}")
        return

    # Main application loop
    while True:
        clear_screen()
        show_main_menu()

        # Get user input for menu selection
        choice = input("Select option (0-18): ").strip()

        # Handle exit option
        if choice == '0':
            print("\n👋 Thanks for using FPL Analysis Tool! Goodbye!")
            break

        # Handle menu option 1: Top players by total points
        elif choice == '1':
            top_n = get_valid_integer("How many top players to show: ", min_val=1)
            show_top_players(players_df, top_n=top_n)
            wait_for_user()

        # Handle menu option 2: Top players by pick rate
        elif choice == '2':
            top_n = get_valid_integer("How many top players to show: ", min_val=1)
            pos = get_valid_position()
            show_top_by_pick_rate(players_df, top_n=top_n, position=pos)
            wait_for_user()

        # Handle menu option 3: Top players by value for money
        elif choice == '3':
            top_n = get_valid_integer("How many top players to show: ", min_val=1)
            pos = get_valid_position()
            min_pts = get_valid_integer("Minimum points threshold (default 50): ", min_val=0) or 50
            show_top_value_for_money(players_df, top_n=top_n, position=pos, min_points=min_pts)
            wait_for_user()

        # Handle menu option 4: Players by position
        elif choice == '4':
            pos = input("Enter position (goalkeeper/defender/midfielder/forward): ").strip().lower()
            show_players_by_position(players_df, pos)
            wait_for_user()

        # Handle menu option 5: All players sorted alphabetically
        elif choice == '5':
            show_players_sorted_alphabetically(players_df)
            wait_for_user()

        # Handle menu option 6: All players sorted by team
        elif choice == '6':
            show_players_sorted_by_team(players_df)
            wait_for_user()

        # Handle menu option 7: Top players by recent form
        elif choice == '7':
            top_n = get_valid_integer("How many top players to show: ", min_val=1)
            pos = get_valid_position()
            n_gws = get_valid_integer("Number of recent gameweeks (default 5): ", min_val=1, default=5)
            show_top_form_players(players_df, top_n=top_n, position=pos, last_n_gameweeks=n_gws)
            wait_for_user()

        # Handle menu option 8: Top players up to specific gameweek
        elif choice == '8':
            top_n = get_valid_integer("How many top players to show: ", min_val=1)
            gw = get_valid_integer("Up to which gameweek: ", min_val=1)
            pos = get_valid_position()
            show_top_players(players_df, up_to_gameweek=gw, top_n=top_n, position=pos)
            wait_for_user()

        # Handle menu option 9: Player form analysis (detailed)
        elif choice == '9':
            pid = get_valid_integer("Enter player ID: ", min_val=1)
            n_gws = get_valid_integer("Number of recent gameweeks (default 5): ", min_val=1, default=5)
            show_player_form_analysis(pid, team_map, players_df, last_n_gameweeks=n_gws)
            wait_for_user()

        # Handle menu option 10: Compare multiple players' form
        elif choice == '10':
            print("Enter player IDs separated by commas (e.g., 123,456,789):")
            pid_input = input().strip()
            try:
                player_ids = [int(pid.strip()) for pid in pid_input.split(',')]
                if len(player_ids) > 6:
                    print("⚠️ Maximum 6 players for comparison. Using first 6.")
                    player_ids = player_ids[:6]
                n_gws = get_valid_integer("Number of recent gameweeks (default 8): ", min_val=1, default=8)
                plot_form_comparison(player_ids, team_map, players_df, last_n_gameweeks=n_gws)
                wait_for_user()
            except ValueError:
                print("❌ Invalid input. Please enter valid player IDs.")
                wait_for_user()

        # Handle menu option 11: Player's full gameweek history
        elif choice == '11':
            pid = get_valid_integer("Enter player ID: ", min_val=1)
            show_player_history(pid, team_map)
            wait_for_user()

        # Handle menu option 12: Player's specific gameweek stats
        elif choice == '12':
            pid = get_valid_integer("Enter player ID: ", min_val=1)
            gw = get_valid_integer("Enter gameweek number: ", min_val=1)
            show_player_gameweek_stats(pid, gw, team_map, players_df)
            wait_for_user()

        # Handle menu option 13: Player points chart
        elif choice == '13':
            pid = get_valid_integer("Enter player ID: ", min_val=1)
            # Validate player exists before plotting
            player_row = players_df[players_df['Player ID'] == pid]
            if player_row.empty:
                print("❌ Player ID not found.")
            else:
                name = f"{player_row.iloc[0]['First Name']} {player_row.iloc[0]['Last Name']}"
                plot_player_points(pid, team_map, players_df, name)
            wait_for_user()

        # Handle menu option 14: Player price chart
        elif choice == '14':
            pid = get_valid_integer("Enter player ID: ", min_val=1)
            # Validate player exists before plotting
            player_row = players_df[players_df['Player ID'] == pid]
            if player_row.empty:
                print("❌ Player ID not found.")
            else:
                name = f"{player_row.iloc[0]['First Name']} {player_row.iloc[0]['Last Name']}"
                plot_player_price(pid, team_map, players_df, name)
            wait_for_user()

        # Handle menu option 15: Compare two players' points
        elif choice == '15':
            pid1 = get_valid_integer("Enter first player ID: ", min_val=1)
            pid2 = get_valid_integer("Enter second player ID: ", min_val=1)
            compare_players_points(pid1, pid2, team_map, players_df)
            wait_for_user()

        # Handle menu option 16: Custom form analysis (date range)
        elif choice == '16':
            pid = get_valid_integer("Enter player ID: ", min_val=1)
            from_gw = get_valid_integer("Enter starting gameweek: ", min_val=1)
            to_gw = get_valid_integer("Enter ending gameweek: ", min_val=from_gw)
            show_player_form_analysis(pid, team_map, players_df, from_gameweek=from_gw, to_gameweek=to_gw)
            wait_for_user()

        # Handle menu option 17: Custom period comparison
        elif choice == '17':
            top_n = get_valid_integer("How many top players to show: ", min_val=1)
            pos = get_valid_position()
            from_gw = get_valid_integer("Enter starting gameweek: ", min_val=1)
            to_gw = get_valid_integer("Enter ending gameweek: ", min_val=from_gw)
            show_top_form_players(players_df, top_n=top_n, position=pos, from_gameweek=from_gw, to_gameweek=to_gw)
            wait_for_user()

        # Handle menu option 18: Multi-player form comparison
        elif choice == '18':
            ids_input = input("Enter player IDs to compare (comma-separated): ")
            try:
                player_ids = [int(pid.strip()) for pid in ids_input.split(',') if pid.strip().isdigit()]
                if len(player_ids) > 6:
                    print("⚠️ Maximum 6 players for comparison. Using first 6.")
                    player_ids = player_ids[:6]
                from_gw = get_valid_integer("Enter starting gameweek: ", min_val=1)
                to_gw = get_valid_integer("Enter ending gameweek: ", min_val=from_gw)
                plot_form_comparison(player_ids, team_map, players_df, from_gameweek=from_gw, to_gameweek=to_gw)
                wait_for_user()
            except ValueError:
                print("❌ Invalid input. Please enter valid player IDs.")
                wait_for_user()

        # Handle invalid menu choices
        else:
            print("❌ Invalid option. Please try again.")
            wait_for_user()


# ============================================================================
# APPLICATION ENTRY POINT
# ============================================================================

if __name__ == '__main__':
    main()
