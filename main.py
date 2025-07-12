import requests
import pandas as pd
from tabulate import tabulate
import matplotlib.pyplot as plt
import numpy as np


pd.set_option('display.width', 200)
base_url = 'https://fantasy.premierleague.com/api/'


# Load FPL data and return all relevant DataFrames
def load_fpl_data():
    r = requests.get(base_url + 'bootstrap-static/').json()

    players = pd.json_normalize(r['elements'])
    teams_df = pd.json_normalize(r['teams'])
    positions_df = pd.json_normalize(r['element_types'])

    team_map = dict(zip(teams_df['id'], teams_df['name']))
    position_map = dict(zip(positions_df['id'], positions_df['singular_name']))

    players['team_name'] = players['team'].map(team_map)
    players['position'] = players['element_type'].map(position_map)
    players['position_order'] = players['position'].map({
        'Manager': 0,
        'Goalkeeper': 1,
        'Defender': 2,
        'Midfielder': 3,
        'Forward': 4
    }).fillna(99)
    players['cost_million'] = players['now_cost'] / 10
    players['selected_by_percent'] = players['selected_by_percent'].astype(float)
    players['form'] = players['form'].astype(float)

    # Cleaned + renamed version for display
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


# Get gameweek history for one player
def get_gameweek_history(player_id):
    r = requests.get(base_url + f'element-summary/{player_id}/').json()
    return pd.json_normalize(r['history'])


def show_top_players(players_df, up_to_gameweek=None, top_n=20, position=None):
    # Optional position filter
    if position:
        position = position.capitalize()
        valid_positions = ['Goalkeeper', 'Defender', 'Midfielder', 'Forward']
        if position not in valid_positions:
            print(f"Invalid position: {position}. Choose from: {', '.join(valid_positions)}")
            return
        players_df = players_df[players_df['Position'] == position]

    if up_to_gameweek:
        temp_data = []
        for pid in players_df['Player ID']:
            gw_hist = get_gameweek_history(pid)
            gw_total = gw_hist[gw_hist['round'] <= up_to_gameweek]['total_points'].sum()
            temp_data.append({'Player ID': pid, 'Points to GW': gw_total})
        temp_df = pd.DataFrame(temp_data)
        merged = pd.merge(players_df, temp_df, on='Player ID')
        merged = merged.sort_values(by='Points to GW', ascending=False)
        if top_n > 0:
            merged = merged.head(top_n)
        print(tabulate(merged[['Player ID', 'First Name', 'Last Name', 'Team', 'Position', 'Cost (Million £)', 'Points to GW']],
                       headers='keys', tablefmt='fancy_grid'))
    else:
        sorted_df = players_df.sort_values(by='Total Points', ascending=False)
        if top_n > 0:
            sorted_df = sorted_df.head(top_n)
        print(tabulate(sorted_df[['Player ID', 'First Name', 'Last Name', 'Team', 'Position', 'Cost (Million £)', 'Total Points']],
                       headers='keys', tablefmt='fancy_grid'))

# Show full gameweek history for a player
def show_player_history(player_id, team_map):
    gw = get_gameweek_history(player_id)
    gw['Opponent'] = gw['opponent_team'].map(team_map)
    print(tabulate(gw[['round', 'Opponent', 'was_home', 'minutes', 'goals_scored', 'assists', 'clean_sheets', 'total_points']],
                   headers='keys', tablefmt='fancy_grid'))

def show_top_by_pick_rate(players_df, top_n=10, position=None):
    df = players_df.copy()

    # Optional position filter
    if position:
        position = position.capitalize()
        valid_positions = ['Goalkeeper', 'Defender', 'Midfielder', 'Forward']
        if position not in valid_positions:
            print(f"Invalid position: {position}. Choose from: {', '.join(valid_positions)}")
            return
        df = df[df['Position'] == position]

    sorted_df = df.sort_values(by='Selected By (%)', ascending=False)
    if top_n > 0:
        sorted_df = sorted_df.head(top_n)

    print(tabulate(sorted_df[['Player ID', 'First Name', 'Last Name', 'Team', 'Position', 'Cost (Million £)', 'Selected By (%)']],
                   headers='keys', tablefmt='fancy_grid'))

# Show a specific player's stats for a given gameweek
def show_player_gameweek_stats(player_id, gameweek, team_map):
    gw = get_gameweek_history(player_id)
    row = gw[gw['round'] == gameweek]
    if row.empty:
        print(f"No data for Gameweek {gameweek}.")
        return
    row = row.iloc[0]
    opponent = team_map.get(row['opponent_team'], 'Unknown')
    print(f"\nGameweek {gameweek} vs {opponent} ({'Home' if row['was_home'] else 'Away'})")
    print(f"Minutes: {row['minutes']}, Goals: {row['goals_scored']}, Assists: {row['assists']}, Clean Sheets: {row['clean_sheets']}, Total Points: {row['total_points']}")

def show_players_sorted_by_team(players_df):
    sorted_df = players_df.sort_values(by=['Team', 'Last Name', 'First Name'])
    print(tabulate(sorted_df[['Player ID', 'First Name', 'Last Name', 'Team', 'Position', 'Cost (Million £)', 'Total Points']],
                   headers='keys', tablefmt='fancy_grid'))

def show_players_sorted_by_id(players_df):
    sorted_df = players_df.sort_values(by='Player ID')
    print(tabulate(sorted_df[['Player ID', 'First Name', 'Last Name', 'Team', 'Position', 'Cost (Million £)', 'Total Points']],
                   headers='keys', tablefmt='fancy_grid'))

# Show all players sorted alphabetically by name
def show_players_sorted_alphabetically(players_df):
    sorted_df = players_df.sort_values(by=['Last Name', 'First Name'])
    print(tabulate(sorted_df[['Player ID', 'First Name', 'Last Name', 'Team', 'Position', 'Cost (Million £)', 'Total Points']],
                   headers='keys', tablefmt='fancy_grid'))

# Show players from a specific position
def show_players_by_position(players_df, position):
    position = position.capitalize()  # Make input case-insensitive
    valid_positions = ['Goalkeeper', 'Defender', 'Midfielder', 'Forward']

    if position not in valid_positions:
        print(f"Invalid position: {position}. Choose from: {', '.join(valid_positions)}")
        return

    filtered = players_df[players_df['Position'] == position].sort_values(by='Total Points', ascending=False)

    print(tabulate(filtered[['Player ID', 'First Name', 'Last Name', 'Team', 'Cost (Million £)', 'Total Points']],
                   headers='keys', tablefmt='fancy_grid'))

def plot_player_points(player_id, team_map, player_name=None):
    gw = get_gameweek_history(player_id)
    if gw.empty:
        print("No gameweek data available for this player.")
        return

    gw = gw.sort_values(by='round')
    rounds = gw['round']
    points = gw['total_points']

    if not player_name:
        player_name = f"Player {player_id}"

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

def plot_player_price(player_id, team_map, player_name=None):
    gw = get_gameweek_history(player_id)
    if gw.empty:
        print("No gameweek data available for this player.")
        return

    gw = gw.sort_values(by='round')
    rounds = gw['round']
    prices = gw['value'] / 10  # Convert to £m

    # Get GW1 price
    gw1_price = prices.iloc[0]

    # Calculate Y-axis limits and ticks
    y_min = max(0, gw1_price - 2)
    y_max = gw1_price + 2
    y_ticks = np.arange(y_min, y_max + 0.2, 0.2)

    if not player_name:
        player_name = f"Player {player_id}"

    plt.figure(figsize=(10, 5))
    plt.plot(rounds, prices, marker='s', color='green', label='Price (£m)')
    plt.title(f"{player_name} – Price per Gameweek")
    plt.xlabel("Gameweek")
    plt.ylabel("Price (£m)")
    plt.grid(True)
    plt.legend()
    plt.xticks(np.arange(rounds.min(), rounds.max() + 1, 2))
    plt.yticks(y_ticks)
    plt.ylim(y_min, y_max)
    plt.tight_layout()
    plt.show()

def compare_players_points(player1_id, player2_id, team_map, players_df):
    gw1 = get_gameweek_history(player1_id)
    gw2 = get_gameweek_history(player2_id)

    if gw1.empty or gw2.empty:
        print("One or both players have no gameweek data.")
        return

    # Sort and align gameweeks
    gw1 = gw1.sort_values(by='round')
    gw2 = gw2.sort_values(by='round')

    rounds1 = gw1['round']
    rounds2 = gw2['round']
    points1 = gw1['total_points']
    points2 = gw2['total_points']

    # Get player names
    name1_row = players_df[players_df['Player ID'] == player1_id]
    name2_row = players_df[players_df['Player ID'] == player2_id]

    if name1_row.empty or name2_row.empty:
        print("Could not find player names.")
        return

    name1 = f"{name1_row.iloc[0]['First Name']} {name1_row.iloc[0]['Last Name']}"
    name2 = f"{name2_row.iloc[0]['First Name']} {name2_row.iloc[0]['Last Name']}"

    # Plot
    plt.figure(figsize=(12, 6))
    plt.plot(rounds1, points1, marker='o', label=name1)
    plt.plot(rounds2, points2, marker='s', label=name2)

    plt.title(f"Points per Gameweek: {name1} vs {name2}")
    plt.xlabel("Gameweek")
    plt.ylabel("Points")
    plt.xticks(range(1, max(rounds1.max(), rounds2.max()) + 1, 1))
    plt.yticks(range(0, max(points1.max(), points2.max()) + 5, 2))
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()

if __name__ == '__main__':
    players_df, team_map = load_fpl_data()

    while True:
        print("==== Fantasy Premier League Interactive Tool ====")
        print("Options:")
        print("1. Show top N players")
        print("2. Show top N players up to a Gameweek")
        print("3. Show top N players up to a Gameweek for a specific position")
        print("4. Show player's full gameweek history")
        print("5. Show specific player's stats for one gameweek")
        print("6. Show all players by position")
        print("7. Show all players sorted alphabetically")
        print("8. Show all players sorted by team")
        print("9. Show all players sorted by ID")
        print("10. Show player points per gameweek")
        print("11. Show player price per gameweek")
        print("12. Compare two players' points per gameweek")
        print("13. Show top N players by pick rate")
        print("0. Exit")
        choice = input("\nEnter your option (0-11): ").strip()

        match choice:
            case '0':
                print("Exiting. Goodbye!")
                break

            case '1':
                top_n = int(input("Enter how many top players to show: "))
                show_top_players(players_df, top_n=top_n)

            case '2':
                top_n = int(input("Enter how many top players to show: "))
                gw = int(input("Up to which Gameweek?: "))
                show_top_players(players_df, up_to_gameweek=gw, top_n=top_n)

            case '3':
                top_n = int(input("Enter how many top players to show: "))
                gw = int(input("Up to which Gameweek?: "))
                pos = input("Enter position (goalkeeper, defender, midfielder, forward): ")
                show_top_players(players_df, up_to_gameweek=gw, top_n=top_n, position=pos)

            case '4':
                pid = int(input("Enter player ID: "))
                show_player_history(pid, team_map)

            case '5':
                pid = int(input("Enter player ID: "))
                gw = int(input("Enter Gameweek number: "))
                show_player_gameweek_stats(pid, gw, team_map)

            case '6':
                pos = input("Enter position (goalkeeper, defender, midfielder, forward): ")
                show_players_by_position(players_df, pos)

            case '7':
                show_players_sorted_alphabetically(players_df)

            case '8':
                show_players_sorted_by_team(players_df)

            case '9':
                show_players_sorted_by_id(players_df)

            case '10':
                pid = int(input("Enter player ID: "))
                player_row = players_df[players_df['Player ID'] == pid]
                if player_row.empty:
                    print("Player ID not found.")
                else:
                    name = f"{player_row.iloc[0]['First Name']} {player_row.iloc[0]['Last Name']}"
                    plot_player_points(pid, team_map, name)

            case '11':
                pid = int(input("Enter player ID: "))
                player_row = players_df[players_df['Player ID'] == pid]
                if player_row.empty:
                    print("Player ID not found.")
                else:
                    name = f"{player_row.iloc[0]['First Name']} {player_row.iloc[0]['Last Name']}"
                    plot_player_price(pid, team_map, name)

            case '12':
                pid1 = int(input("Enter first player ID: "))
                pid2 = int(input("Enter second player ID: "))
                compare_players_points(pid1, pid2, team_map, players_df)

            case '13':
                top_n = int(input("Enter how many top players to show by pick rate: "))
                pos = input(
                    "Enter position (goalkeeper, defender, midfielder, forward) or press Enter to include all: ").strip().lower()
                pos = pos if pos else None
                show_top_by_pick_rate(players_df, top_n=top_n, position=pos)

            case _:
                print("Invalid option. Try again.")