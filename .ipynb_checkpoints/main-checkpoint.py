import requests, json
from pprint import pprint
import pandas as pd
from tabulate import tabulate

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('display.width', 200)  # increase max width for display

# base url for all FPL API endpoints
base_url = 'https://fantasy.premierleague.com/api/'

# get data from bootstrap-static endpoint
r = requests.get(base_url+'bootstrap-static/').json()

# create DataFrame of players
players = pd.json_normalize(r['elements'])

# map team ID to team name
teams_df = pd.json_normalize(r['teams'])
team_map = dict(zip(teams_df['id'], teams_df['name']))
players['team_name'] = players['team'].map(team_map)

# map element_type to position name
positions_df = pd.json_normalize(r['element_types'])
position_map = dict(zip(positions_df['id'], positions_df['singular_name']))
players['position'] = players['element_type'].map(position_map)

position_order = {
    'Manager': 0,
    'Goalkeeper': 1,
    'Defender': 2,
    'Midfielder': 3,
    'Forward': 4
}

players['position_order'] = players['position'].map(position_order).fillna(99)

players['cost_million'] = players['now_cost'] / 10
players['selected_by_percent'] = players['selected_by_percent'].astype(float)
players['form'] = players['form'].astype(float)

# Filter out managers
players_no_managers = players[players['position'] != 'Manager']

# Sort filtered players by selected_by_percent descending
players_sorted = players_no_managers.sort_values(by='selected_by_percent', ascending=False)

players_sorted_renamed = players_sorted.rename(columns={
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

print(tabulate(
    players_sorted_renamed[['Player ID', 'First Name', 'Last Name', 'Team', 'Position',
                           'Cost (Million £)', 'Selected By (%)', 'Form', 'Total Points']],
    headers='keys',
    tablefmt='fancy_grid'
))