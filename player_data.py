from selenium import webdriver
from selenium.webdriver.common.by import By
import json
import os
import sys
import traceback

data_folder_path=f"data"

def load_teams():
    team_data_folder = f"{data_folder_path}/Team-Data"
    files = [f for f in os.listdir(team_data_folder) if os.path.isfile(os.path.join(team_data_folder, f))]
    
    if not files:
        print("No teams found.")
        return None, None
    
    while True:
        print("\nTeam List:\n")
        for idx, file in enumerate(files, 1):
            print(f"{idx}. {file.replace('.json', '').replace('-', ' ')}")
        print(f"{len(files) + 1}. Exit")

        try:
            choice = int(input("\nEnter team (number): "))
            if 1 <= choice <= len(files):
                selected_file = os.path.join(team_data_folder, files[choice - 1])
                team_name = files[choice - 1].replace('.json', '')
                return selected_file, team_name
            elif choice == len(files) + 1:
                print("Exiting...")
                sys.exit()
            else:
                print("\nInvalid choice. Please select a valid number.")
        except ValueError:
            print("\nPlease enter a valid number.")  

def load_players(team_file):
    try:
        with open(team_file, "r") as f:
            team_data = json.load(f)
        
        players = team_data.get("players", [])
        if not players:
            print("\nNo players found in this team.")
            return None
        
        while True:
            print("\nPlayer List:\n")
            for idx, player in enumerate(players, 1):
                print(f"{idx}. {player['name']}")
            print(f"{len(players) + 1}. Go back to team selection")

            try:
                choice = int(input("\nEnter player (number): "))
                if 1 <= choice <= len(players):
                    return players[choice - 1]
                elif choice == len(players) + 1:
                    return None
                else:
                    print("\nInvalid choice. Please select a valid number.")
            except ValueError:
                print("\nPlease enter a valid number.")
    except Exception as e:
        print(f"\nError reading file: {e}")
        return None

def format_and_save_player_data(data, team_name):
    try:
        cl_array = {
            1: 'Test',
            2: 'ODI',
            3: 'T20I',
            6: 'T20s',
            5: 'List A',
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
            'photo': f"data/players/{player_profile['longName']}.jpg",
            'dob': f"{player_profile['dateOfBirth']['year']}-{player_profile['dateOfBirth']['month']}-{player_profile['dateOfBirth']['date']}",
            'batting_style': player_profile['longBattingStyles'][0] if player_profile['longBattingStyles'] else None,
            'bowling_style': player_profile['longBowlingStyles'][0] if player_profile['longBowlingStyles'] else None,
            'role': player_profile['playingRoles'][0] if player_profile['playingRoles'] else None,
            'career_span': player_profile['intlCareerSpan'],
            'country': player_profile['country']['name'],
            'player_id': data['player']['objectId'],
            'debut_matches': debut_matches,
            'fielding_position': player_profile['fieldingStyles'][0] if player_profile['fieldingStyles'] else None,
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
            format_type = cl_array.get(stat['cl'], None) 
            if format_type is not None:
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
        
        league_data=data['content']['trophyStats']['trophies']
        searchId = 117
        result = [item for item in league_data if item['trophy']['id'] == searchId]
        if result:
            ipl_data = result[0]['stats']
        else:
            ipl_data = []

        if ipl_data:
            for stat in ipl_data:
                temp = {}
                format_ = 'IPL'
                type_ = stat['type']
                if type_ == 'BATTING':
                    temp['matches'] = stat['mt']
                    temp['innings'] = stat['in']
                    temp['runs'] = stat['rn']
                    temp['balls_faced'] = stat['bl']
                    temp['average'] = stat['avg']
                    temp['strike_rate'] = stat['sr']
                    temp['notouts'] = stat['no']
                    temp['fours'] = stat['fo']
                    temp['sixes'] = stat['si']
                    temp['highest_score'] = stat['hs']
                    temp['hundreds'] = stat['hn']
                    temp['fifties'] = stat['ft']
                    temp['catches'] = stat['ct']
                    temp['stumpings'] = stat['st']
                elif type_ == 'BOWLING':
                    temp['matches'] = stat['mt']
                    temp['innings'] = stat['in']
                    temp['runs_conceeded'] = stat['rn']
                    temp['balls_bowled'] = stat['bl']
                    temp['average'] = stat['avg']
                    temp['strike_rate'] = stat['sr']
                    temp['wickets'] = stat['wk']
                    temp['best_figure'] = stat['bbi']
                    temp['four_wickets'] = stat['fwk']
                    temp['five_wickets'] = stat['fw']
                    temp['ten_wickets'] = stat['tw']
                    temp['economy'] = stat['bwe']
                
                if format_ not in temp_stat:
                    temp_stat[format_] = {}
                temp_stat[format_][type_] = temp
        else:
            temp_stat['IPL'] = {
                'BATTING': {
                    'matches': 0,
                    'innings': 0,
                    'runs': 0,
                    'balls_faced': 0,
                    'average': 0,
                    'strike_rate': 0,
                    'notouts': 0,
                    'fours': 0,
                    'sixes': 0,
                    'highest_score': 0,
                    'hundreds': 0,
                    'fifties': 0,
                    'catches': 0,
                    'stumpings': 0
                },
                'BOWLING': {
                    'matches': 0,
                    'innings': 0,
                    'runs_conceeded': 0,
                    'balls_bowled': 0,
                    'average': 0,
                    'strike_rate': 0,
                    'wickets': 0,
                    'best_figure': 0,
                    'four_wickets': 0,
                    'five_wickets': 0,
                    'ten_wickets': 0,
                    'economy': 0
                }
            }
        
        player['stats'] = temp_stat
        
        player_json = json.dumps(player)
        folder = os.path.join('data', team_name)
        os.makedirs(folder, exist_ok=True)
        file_path = os.path.join(folder, f"{data['player']['objectId']}.json")
        with open(file_path, 'w') as f:
            f.write(player_json)
        return True

    except Exception as e:
        print(f"Error: {e}")
        print("Error:", e)
        print("Traceback:")
        traceback.print_exc()
        return False  
  
while True:
    selected_team_file, team_name = load_teams()
    if selected_team_file and team_name:
        while True:
            selected_player = load_players(selected_team_file)
            if selected_player:
                print("Loading player ....")
                player_data_url = f"https://www.espncricinfo.com/cricketers/{selected_player['name'].lower().replace(' ', '-')}-{selected_player['id']}"
                print(player_data_url)

                # Initialize WebDriver for each player selection
                options = webdriver.ChromeOptions()
                options.headless = False
                driver = webdriver.Chrome(options=options)

                try:
                    driver.get(player_data_url)
                    player_content = driver.find_element(By.ID, "__NEXT_DATA__").get_attribute('innerHTML')
                    player_content = json.loads(player_content)['props']['appPageProps']['data']
                    print(f'Writing data for {team_name}')
                    format_and_save_player_data(player_content, team_name)
                    print("File written successfully!\n")

                except Exception as e:
                    print(f"Error fetching data for {player_data_url}: {e}")

                finally:
                    driver.quit()  # Ensure WebDriver quits after each player is processed

            else:
                break 

