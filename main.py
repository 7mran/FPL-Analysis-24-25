import requests, json
from pprint import pprint
import pandas as pd

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

print(players_sorted[['id', 'first_name', 'second_name', 'team_name', 'position',
                      'cost_million', 'selected_by_percent', 'form', 'total_points']].to_string(index=False, col_space=15))