from selenium import webdriver
from selenium.webdriver.common.by import By
import json
import os
import sys
team_data_url='https://www.espncricinfo.com/series/ipl-2025-1449924'

options= webdriver.ChromeOptions()
options.headless=False
driver=webdriver.Chrome(options=options)
data_path="data/"

#POINTS TABLE AND TEAM FOLDER GENERATION
try:
    driver.get(team_data_url)
    driver.implicitly_wait(10)
    team_content = driver.find_element(By.ID, "__NEXT_DATA__")
    team_content = team_content.get_attribute('innerHTML')
    team_content=json.loads(team_content)
 
    points_table=team_content['props']['appPageProps']['data']['content']['standings']['groups'][0]['teamStats']
    standings = []
    for t in points_table:
        team_slug = t['teamInfo']['longName'].replace(' ', '-')
        img_id = t['teamInfo']['imageUrl']
        standings.append({
            'team_id': t['teamInfo']['objectId'],
            'team': t['teamInfo']['longName'],
            'image': f"https://img1.hscicdn.com/image/upload/f_auto,t_ds_square_w_80{img_id}",
            'played': t['matchesPlayed'],
            'won': t['matchesWon'],
            'lost': t['matchesLost'],
            'tied': t['matchesTied'],
            'points': t['points'],
            'nrr': t['nrr'],
            'team_slug': team_slug
        })
    print('Points table generated .......')
    with open(f"{data_path}points_table.json", 'w') as f:
        json.dump(standings, f)
    print('Points table generated ...')
    
    team_data_folder=f"{data_path}Team-Data"
    if not os.path.exists(team_data_folder):
        os.makedirs(team_data_folder, mode=0o777, exist_ok=True)
    print('Team data folder generated ...')
    for key,t in enumerate(standings):
        team_id = t['team'].replace(' ', '-').lower() + '-' + str(t['team_id'])
        players_url=f"https://www.espncricinfo.com/team/{team_id}"
        driver.get(players_url)
        driver.implicitly_wait(3)
        player_content = driver.find_element(By.ID, "__NEXT_DATA__")
        player_content = player_content.get_attribute('innerHTML')
        player_content=json.loads(player_content)
        player_list=player_content['props']['appPageProps']['data']['data']['content']['recentSquads'][0]['players']
        players=[]
        for plist in player_list:
            player=plist['player']
            players.append({
                'team_name': t['team'],
                'team_logo': t['image'],
                'id': player['objectId'],
                'name': player['longName'],
                'roleType': player['playingRoles'][0] if player['playingRoles'] else None,
                'imageUrl': player['imageUrl'],
                'headshotImageUrl': player['headshotImageUrl'],
                'slug': player['slug'],
                'dob': f"{player['dateOfBirth']['year']}-{player['dateOfBirth']['month']}-{player['dateOfBirth']['date']}",
                'batting_style': player['longBattingStyles'][0] if player['longBattingStyles'] else None,
                'bowling_style': player['longBowlingStyles'][0] if player['longBowlingStyles'] else None,
                'countryTeamId': player['countryTeamId'],
                'playingRoles': player['playingRoles'][0] if player['playingRoles'] else None
            })
        team_data = {**t, 'players': players}
        folder_name=t['team'].replace(' ','-')
        team_folder=f"{data_path}{folder_name}"
        if not os.path.exists(team_folder):
            os.makedirs(team_folder, mode=0o777, exist_ok=True)
        with open(f"{team_data_folder}/{folder_name}.json", 'w') as f:
            json.dump(team_data, f)
        print(f'{team_folder} Team data generated ...')
                
finally:
    driver.quit()

