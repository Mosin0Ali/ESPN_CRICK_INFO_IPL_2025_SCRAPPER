from selenium import webdriver
from selenium.webdriver.common.by import By
import json
import os
from datetime import datetime
import time
import random


def format_and_save_player_data(data, team_name):
    try:
        cl_array = {
            1: 'Test',
            2: 'ODI',
            3: 'T20I',
            6: 'T20s',
            5: 'List A'
        }

        player_profile = data['player']
        debut = data['content']['matches']['types'][0]['matches']
        debut_matches = []
        format_done = []

        for deb in debut:
            format_type = deb['events'][0]['match']['format']
            if format_type not in format_done:
                temp = {
                    'format': format_type,
                    'date': deb['events'][0]['match']['startDate'],
                    'ground': deb['events'][0]['match']['ground']['smallName'],
                    'team1': deb['events'][0]['match']['teams'][0]['team']['abbreviation'],
                    'team2': deb['events'][0]['match']['teams'][1]['team']['abbreviation']
                }
                debut_matches.append(temp)
                format_done.append(temp['format'])

        

        player = {
            'name': player_profile['longName'],
            'dob': f"{player_profile['dateOfBirth']['year']}-{player_profile['dateOfBirth']['month']}-{player_profile['dateOfBirth']['date']}",
            'batting_style': player_profile['longBattingStyles'][0] if player_profile['longBattingStyles'] else None,
            'bowling_style': player_profile['longBowlingStyles'][0] if player_profile['longBowlingStyles'] else None,
            'role': player_profile['playingRoles'][0] if player_profile['playingRoles'] else None,
            'career_span': player_profile['intlCareerSpan'],
            'country': player_profile['country']['name'],
            'player_id': data['player']['objectId'],
            'debut_matches': debut_matches,
            'fielding_position': player_profile['fieldingStyles'][0] if player_profile['fieldingStyles'] else None,
            'photo':player_profile['headshotImageUrl']
        }
       

        player_stats = data['content']['careerAverages']['stats']
        recent_matches = data['content']['matches']['types'][0]['recent']
        recent_performances = []

        for recent in recent_matches:
            temp = {
                'batting': recent['battingText'],
                'bowling': recent['bowlingText'],
                'team1': recent['match']['teams'][0]['team']['name'],
                'team2': recent['match']['teams'][1]['team']['name'],
                'date': recent['match']['startDate'],
                'format': recent['match']['format'],
                'ground_small': recent['match']['ground']['smallName'],
                'ground_big': recent['match']['ground']['name']
            }
            recent_performances.append(temp)

        player['recent'] = recent_performances

        temp_stat = {}
        for stat in player_stats:
            temp = {}
            format_type = cl_array[stat['cl']]
            stat_type = stat['type']
            
            if stat_type == 'BATTING':
                temp.update({
                    'matches': stat['mt'],
                    'innings': stat['in'],
                    'runs': stat['rn'],
                    'balls_faced': stat['bl'],
                    'average': stat['avg'],
                    'strike_rate': stat['sr'],
                    'notouts': stat['no'],
                    'fours': stat['fo'],
                    'sixes': stat['si'],
                    'highest_score': stat['hs'],
                    'hundreds': stat['hn'],
                    'fifties': stat['ft'],
                    'catches': stat['ct'],
                    'stumpings': stat['st']
                })
            elif stat_type == 'BOWLING':
                temp.update({
                    'matches': stat['mt'],
                    'innings': stat['in'],
                    'runs_conceeded': stat['rn'],
                    'balls_bowled': stat['bl'],
                    'average': stat['avg'],
                    'strike_rate': stat['sr'],
                    'wickets': stat['wk'],
                    'best_figure': stat['bbi'],
                    'four_wickets': stat['fwk'],
                    'five_wickets': stat['fw'],
                    'ten_wickets': stat['tw'],
                    'economy': stat['bwe']
                })
            temp_stat.setdefault(format_type, {})[stat_type] = temp

        player['stats'] = temp_stat
        player_json = json.dumps(player)

        folder = os.path.join('..', 'data', team_name)
        os.makedirs(folder, exist_ok=True)
        file_path = os.path.join(folder, f"{data['player']['objectId']}.json")

        with open(file_path, 'w') as f:
            f.write(player_json)

        save_updated_at(team_name)
        return True

    except Exception as e:
        print(f"Error: {e}")
        return False


def save_updated_at(team_name):
    file_path = f'data/teams_updated.json'
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r') as f:
                json_data = f.read()
                data_array = json.loads(json_data)
                if not isinstance(data_array, list):
                    data_array = []
        except (json.JSONDecodeError, FileNotFoundError):
            data_array = []
    else:
        data_array = []

    updated_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    found = False

    for team in data_array:
        if team.get('team_name') == team_name:
            team['updated_at'] = updated_at
            found = True
            break

    if not found:
        data_array.append({
            'team_name': team_name,
            'updated_at': updated_at
        })
        
    try:
        with open(file_path, 'w') as f:
            json.dump(data_array, f, indent=4)
    except Exception as e:
        print(f"Error saving updated time: {e}")          
        
        

player_data_url="https://www.espncricinfo.com/cricketers/"
options= webdriver.ChromeOptions()
options.headless=False
driver=webdriver.Chrome(options=options)
data_path="data/"
team_data_folder=f"{data_path}Team-Data"

file_names_with_extensions = [filename for filename in os.listdir(team_data_folder) if os.path.isfile(os.path.join(team_data_folder, filename))]

for team in file_names_with_extensions:
    file_path=f"{team_data_folder}/{team}"
    with open(file_path, 'r') as f:
        data = json.load(f)
        team_name=data['team_slug']
        players=data['players']
        for iplayer in players:
            player_sc_id=f"{iplayer['slug']}-{iplayer['id']}"
            player_url=f"https://www.espncricinfo.com/cricketers/{player_sc_id}"
            driver.get(player_url)
            time.sleep(30) 
            try:
                player_content = driver.find_element(By.ID, "__NEXT_DATA__")
                player_content = player_content.get_attribute('innerHTML')
                player_content=json.loads(player_content)
                player_content=player_content['props']['appPageProps']['data']
                print('Writing data for '+ team_name)
                format_and_save_player_data(player_content, team_name)
            except Exception as e:
                print(f"Error fetching data for {player_url}: {e}")
            
           
        


    



